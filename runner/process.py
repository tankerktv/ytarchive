"""Запуск потомка под надзором.

Тонкая обёртка: вся политика — в `core.supervisor`, здесь только работа
с подсистемой процессов. Правило «если в обёртке появился `if` с
содержательным условием, его место в ядре» соблюдается буквально —
решение о снятии принимает `judge`, а не этот файл.

Три вещи оплачены сутками простоя 27–29.08.2026 и потому сделаны явно:

1. **Потомку даётся пустой ввод.** Унаследованный ввод — верный способ
   получить процесс, который молча ждёт ответа на приглашение, которого
   никто не видит. Под планировщиком, где консоли нет вовсе, это выглядит
   как зависание с нулевым временем ЦП.
2. **Вывод вычитывается непрерывно, отдельным потоком.** Если этого не
   делать, труба переполняется и потомок встаёт на записи — снова
   «зависание» без единой причины в журнале.
3. **Снимается всё дерево процессов, и снятие проверяется.** yt-dlp
   поднимает ffmpeg для слияния; убитый родитель оставляет его сиротой.
   Мы такие сироты ловили — по 9 часов с нулевым ЦП.
"""

from __future__ import annotations

import os
import queue
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from core.supervisor import ProcessState, Verdict, WatchdogPolicy, judge

#: Как часто спрашиваем надзорщика. Чаще незачем — пределы измеряются
#: десятками секунд, а лишние пробуждения только жгут процессор.
POLL_INTERVAL = 0.5

#: Сколько строк вывода держим. Полный журнал yt-dlp на большом канале —
#: это сотни тысяч строк прогресса; хранить их в памяти незачем.
KEEP_LINES = 400


@dataclass
class RunOutcome:
    verdict: Verdict
    exit_code: int | None = None
    lines: list[str] = field(default_factory=list)
    elapsed: float = 0.0
    killed: bool = False
    kill_failed: bool = False

    @property
    def is_ok(self) -> bool:
        return self.verdict is Verdict.OK

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def _kill_tree(process: subprocess.Popen, grace: float) -> tuple[bool, bool]:
    """Снять потомка вместе с его собственными потомками.

    Возвращает (сняли, не удалось снять). Снятие обязательно проверяется:
    команда, которая «сработала», но оставила процесс живым, хуже её отсутствия —
    надзорщик решит, что дело сделано, и пойдёт дальше.
    """
    if process.poll() is not None:
        return False, False

    if sys.platform == "win32":
        # taskkill /T обходит дерево; без него ffmpeg остаётся сиротой.
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            check=False,
        )
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass

    try:
        process.wait(timeout=grace)
        return True, False
    except subprocess.TimeoutExpired:
        pass

    # Мягкое не помогло — бьём насмерть и проверяем ещё раз.
    try:
        if sys.platform != "win32":
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass

    try:
        process.wait(timeout=grace)
        return True, False
    except subprocess.TimeoutExpired:
        return True, True


def run_watched(
    argv: list[str],
    policy: WatchdogPolicy,
    *,
    on_line: Callable[[str], None] | None = None,
    clock: Callable[[], float] = time.monotonic,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> RunOutcome:
    """Запустить команду и держать её под надзором до конца.

    `on_line` зовётся на каждую строку вывода — через него интерфейс получает
    прогресс. Исключение в нём не должно ронять выкачку, поэтому оно гасится.
    """
    popen_kwargs: dict[str, object] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        # Пустой ввод, а не унаследованный: см. пункт 1 в заголовке файла.
        "stdin": subprocess.DEVNULL,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "bufsize": 1,
        "cwd": cwd,
        "env": env,
    }
    if sys.platform != "win32":
        popen_kwargs["start_new_session"] = True

    started = clock()
    process = subprocess.Popen(argv, **popen_kwargs)  # type: ignore[arg-type]

    lines: list[str] = []
    inbox: queue.Queue[str] = queue.Queue()

    def drain() -> None:
        # Читаем до конца всегда: недочитанная труба останавливает потомка.
        assert process.stdout is not None
        for raw in process.stdout:
            inbox.put(raw.rstrip("\r\n"))

    reader = threading.Thread(target=drain, daemon=True, name="ytarchive-reader")
    reader.start()

    last_output = started
    verdict = Verdict.RUNNING
    killed = kill_failed = False

    while True:
        got_line = False
        while True:
            try:
                line = inbox.get_nowait()
            except queue.Empty:
                break
            got_line = True
            lines.append(line)
            if len(lines) > KEEP_LINES:
                del lines[: len(lines) - KEEP_LINES]
            if on_line is not None:
                try:
                    on_line(line)
                except Exception:  # noqa: BLE001 — падение интерфейса не должно ронять выкачку
                    pass

        now = clock()
        if got_line:
            last_output = now

        exited = process.poll() is not None
        state = ProcessState(
            started_at=started,
            last_output_at=last_output,
            now=now,
            exited=exited,
            exit_code=process.returncode if exited else None,
        )
        verdict = judge(state, policy)

        if verdict.needs_kill:
            killed, kill_failed = _kill_tree(process, policy.kill_grace)
            break
        if verdict.is_final:
            break

        time.sleep(POLL_INTERVAL)

    # Добираем хвост вывода: между последней проверкой и завершением
    # потомок мог сказать что-то важное — например, причину отказа.
    reader.join(timeout=2.0)
    while True:
        try:
            lines.append(inbox.get_nowait())
        except queue.Empty:
            break

    return RunOutcome(
        verdict=verdict,
        exit_code=process.returncode,
        lines=lines[-KEEP_LINES:],
        elapsed=clock() - started,
        killed=killed,
        kill_failed=kill_failed,
    )


def iter_lines(outcome: RunOutcome) -> Iterable[str]:
    return iter(outcome.lines)
