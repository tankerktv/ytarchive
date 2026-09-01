"""Непрерывная работа своими силами, без планировщика задач.

Раньше проходы заводил планировщик Windows: раз в полчаса, одинаково на все
случаи. Он же был единственной причиной, по которой программа не работала
на маке и линуксе.

Здесь тот же смысл, но внутри: цикл «проход — пауза — проход», где длину
паузы выбирает `core.schedule` по тому, чем кончился проход.

Сам проход сюда передаётся готовым. Замок прохода, журнал и живое состояние
остаются там, где и были, — в точке входа; демон ведает только ритмом,
остановкой и тем, чтобы работал ровно один.

Два свойства, ради которых это написано именно так:

* **Остановка быстрая.** Просьба доходит до самого yt-dlp, а не только до
  конца текущего канала: канал бывает на шестьсот роликов, и человек,
  нажавший «стоп», не должен ждать до ночи.
* **Демон один.** Автозапуск и кнопка «Пуск» легко дают двух — они не
  сговариваются. Замок, который держится всю жизнь процесса, это исключает.

Часы и сон передаются снаружи — иначе цикл проверялся бы получасами.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from core.flow import SessionSummary
from core.schedule import Rhythm, next_pause
from runner.lockfile import acquire

#: Насколько дробим паузу. Пауза бывает часовой, а на просьбу остановиться
#: надо отвечать сразу — поэтому спим короткими кусками и между ними
#: спрашиваем, не пора ли уходить.
ЛОМОТЬ = 1.0

#: Как часто отмечаемся в замке демона, чтобы он не протух за долгую паузу.
ОТМЕТКА = 60.0

ИМЯ_ЗАМКА = "ytarchive-daemon.lock"
ИМЯ_ФЛАГА = "ytarchive-stop"


def stop_path(tools_dir: Path) -> Path:
    return Path(tools_dir) / ИМЯ_ФЛАГА


def ask_stop(tools_dir: Path) -> None:
    """Попросить работающий демон остановиться.

    Флагом, а не сигналом: сигналы на Windows работают иначе, чем везде,
    а окно и командная строка должны уметь это одинаково.
    """
    stop_path(tools_dir).write_text("стоп\n", encoding="utf-8", newline="\n")


def clear_stop(tools_dir: Path) -> None:
    try:
        stop_path(tools_dir).unlink()
    except OSError:
        pass


def stop_requested(tools_dir: Path) -> bool:
    return stop_path(tools_dir).exists()


def daemon_running(tools_dir: Path) -> bool:
    """Работает ли демон. Смотрим по его замку — тому же, что не даёт
    завестись второму."""
    from core.locking import LockState, judge_lock
    from runner.lockfile import STALE_AFTER, pid_alive, read_lock

    сведения = read_lock(Path(tools_dir) / ИМЯ_ЗАМКА)
    if сведения is None:
        return False
    решение = judge_lock(
        сведения, now=time.time(), pid_alive=pid_alive(сведения.pid), stale_after=STALE_AFTER
    )
    # Занятым считаем только живого хозяина: протухший и брошенный замки
    # означают, что демона нет, — иначе окно вечно показывало бы «работает».
    return решение is LockState.HELD


@dataclass
class _Пауза:
    """Сон, который умеет прерваться и отметиться в замке."""

    sleep: Callable[[float], None]
    clock: Callable[[], float]

    def выждать(self, сколько: float, *, пора_уходить, отметиться) -> bool:
        """Переждать паузу. `False` значит «попросили остановиться»."""
        конец = self.clock() + сколько
        последняя_отметка = self.clock()
        while self.clock() < конец:
            if пора_уходить():
                return False
            if self.clock() - последняя_отметка >= ОТМЕТКА:
                отметиться()
                последняя_отметка = self.clock()
            # Остаток здесь всегда положительный: условие цикла это и значит.
            self.sleep(min(ЛОМОТЬ, конец - self.clock()))
        return not пора_уходить()


def run_forever(
    make_pass: Callable[[Callable[[], bool]], SessionSummary],
    *,
    tools_dir: Path,
    rhythm: Rhythm | None = None,
    on_message: Callable[[str], None] | None = None,
    passes: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> int:
    """Крутить проходы, пока не попросят остановиться. Возвращает их число.

    `make_pass` получает способ спросить «не пора ли остановиться» и обязан
    передать его вглубь, до yt-dlp. `passes` ограничивает число проходов —
    нужно проверкам, чтобы цикл заканчивался; в работе не задаётся.
    """
    ритм = rhythm or Rhythm()
    скажи = on_message or (lambda _: None)
    tools_dir = Path(tools_dir)

    # Флаг мог остаться с прошлой остановки: не сняв его, демон встанет
    # сразу же, и человек будет нажимать «Пуск» в недоумении.
    clear_stop(tools_dir)

    замок, объяснение = acquire(tools_dir / ИМЯ_ЗАМКА)
    if замок is None:
        скажи(f"уже работает: {объяснение}")
        return 0

    пауза = _Пауза(sleep=sleep, clock=clock)
    отмечено = clock()

    def пора() -> bool:
        """Не пора ли остановиться — и заодно отметка в замке.

        Отметка именно здесь, потому что об этом спрашивают постоянно, в том
        числе из самой выкачки. Без неё замок демона протухал посреди долгого
        прохода: проход на час — это час без единой отметки, а замок считается
        брошенным через десять минут. Окно тогда показывает «обход не
        запущен» и предлагает завести второй.

        Спрашивают часто, поэтому отмечаемся не чаще, чем раз в ОТМЕТКА:
        запись файла дважды в секунду — не то, ради чего это писалось.
        """
        nonlocal отмечено
        сейчас = clock()
        if сейчас - отмечено >= ОТМЕТКА:
            замок.heartbeat()
            отмечено = сейчас
        return stop_requested(tools_dir)

    сделано = 0
    try:
        with замок:
            while passes is None or сделано < passes:
                итог = make_pass(пора)
                замок.heartbeat()
                сделано += 1
                # Про итог прохода не говорим: это дело самого прохода,
                # у него для этого есть журнал. Повторив, мы бы удвоили
                # каждую строку в глазах человека.

                if пора():
                    скажи("остановлено по просьбе")
                    break
                if passes is not None and сделано >= passes:
                    break

                ждать = next_pause(
                    downloaded=итог.downloaded,
                    needs_human=итог.needs_human,
                    rhythm=ритм,
                )
                скажи(f"следующий проход через {ждать / 60:.0f} мин")
                if not пауза.выждать(ждать, пора_уходить=пора, отметиться=замок.heartbeat):
                    скажи("остановлено по просьбе")
                    break
    finally:
        clear_stop(tools_dir)

    return сделано
