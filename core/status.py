"""Состояние выкачки для показа человеку.

Чистая логика: на входе строки журнала и факт «процесс жив», на выходе снимок,
который окну остаётся нарисовать.

**Судить о работе по свежести журнала нельзя.** Журнал разрежен: строка пишется
на файл, а не на каждый процент. Ролик SoyuzUS на 4,7 ГБ качается два часа сорок
девять минут — всё это время в журнале тишина, хотя выкачка идёт полным ходом.
Поэтому «работает ли» приходит снаружи, от того, кто видит процессы, а журнал
отвечает только на вопрос «что именно происходит».
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum



class RunState(Enum):
    RUNNING = "качает"
    BETWEEN = "пауза между роликами"
    #: Обход жив, но сейчас не качает: ждёт следующего прохода. Раньше это
    #: показывалось как «не запущена» — рядом с подписью «обход работает».
    #: Человек, видя «не запущена», шёл нажимать «Запустить».
    WAITING = "ждёт следующего прохода"
    IDLE = "не запущена"
    NEEDS_HUMAN = "остановлена, нужен человек"

    @property
    def is_working(self) -> bool:
        return self in (RunState.RUNNING, RunState.BETWEEN)


@dataclass(frozen=True)
class Status:
    state: RunState
    current_file: str = ""
    channel: str = ""
    last_size_bytes: int | None = None
    last_speed_bps: float | None = None
    errors: int = 0
    archive_count: int = 0
    stopped_reason: str = ""

    def headline(self, перевод=str) -> str:
        """Одна строка для шапки окна.

        Переводчик передаётся доводом, а не берётся из общего места: ядру
        нельзя знать ни про язык интерфейса, ни про то, откуда он берётся.
        По умолчанию — тождественный, то есть по-русски, как в исходнике.
        """
        состояние = перевод(self.state.value)
        if self.state is RunState.NEEDS_HUMAN:
            # Причина хранится по-русски как ключ и переводится тем, кто
            # показывает. Без перевода английское окно говорило бы
            # «stopped, needs you: нужен вход в аккаунт».
            return f"{состояние}: {перевод(self.stopped_reason)}"
        if self.state is RunState.IDLE:
            сколько = перевод("в архиве {} роликов").format(self.archive_count)
            return f"{состояние} · {сколько}"
        if self.current_file:
            return f"{состояние}: {self.current_file}"
        return состояние


    def title(self, перевод=str) -> str:
        """Короткий заголовок для карточки состояния в окне.

        Без имени файла и счёта роликов: в окне они показаны рядом, крупно
        и по отдельности. Повторённые в заголовке, они превращали его в
        строку на всю ширину, из которой состояние приходилось выискивать.
        """
        состояние = перевод(self.state.value)
        состояние = состояние[:1].upper() + состояние[1:]
        if self.state is RunState.NEEDS_HUMAN and self.stopped_reason:
            return f"{состояние}: {перевод(self.stopped_reason)}"
        return состояние


def build_status(
    *,
    process_running: bool,
    archive_count: int = 0,
    live=None,
    worker_running: bool = False,
) -> Status:
    """Собрать снимок состояния.

    **Состояние берётся из живого снимка, а не из текста журнала.** Раньше
    оно вычитывалось разбором строк — искались «остановлено — » и
    «: проверка — ». Пока журнал был только по-русски, это работало; с его
    переводом окно ослепло бы молча, а хуже слепоты только слепота без
    предупреждения. Журнал теперь читает человек, а окно — снимок.

    `process_running` приходит снаружи намеренно: изнутри отличить «идёт
    двухчасовой ролик» от «всё давно упало» невозможно, журнал в это время
    молчит одинаково.
    """
    from core.livestate import LiveState

    живое = live if live is not None else LiveState()

    if живое.stopped_reason:
        state = RunState.NEEDS_HUMAN
    elif not process_running:
        # Прохода нет. Но обход при этом может быть жив и ждать следующего —
        # это не «не запущена».
        state = RunState.WAITING if worker_running else RunState.IDLE
    elif живое.sleeping:
        state = RunState.BETWEEN
    else:
        state = RunState.RUNNING

    return Status(
        state=state,
        current_file=живое.file_name if state.is_working else "",
        channel=живое.channel,
        last_size_bytes=живое.size_bytes or None,
        last_speed_bps=живое.speed_bps or None,
        errors=живое.errors,
        archive_count=archive_count,
        stopped_reason=живое.stopped_reason,
    )


def is_new_trouble(told: str, current: str) -> bool:
    """Пора ли сказать человеку о беде всплывающим сообщением.

    Говорим один раз на каждую новую причину. Окно обновляется каждые две
    секунды, и повторять «истекли куки» с той же частотой значит приучить
    человека закрывать сообщения не читая. Смена причины — новая беда, и о
    ней говорим снова.
    """
    return bool(current) and current != told


class Hint(Enum):
    """Чего не хватает, чтобы выкачка вообще могла начаться."""

    NO_CHANNELS = "no-channels"
    NO_COOKIES = "no-cookies"


def next_hint(*, channels: int, has_cookies: bool) -> Hint | None:
    """Что подсказать человеку на главной вкладке.

    Одна подсказка за раз и в порядке, в котором это делают: без каналов
    говорить про куки рано. Когда всё на месте — ничего: подсказка, висящая
    у работающей программы, превращается в шум, который перестают читать.
    """
    if channels <= 0:
        return Hint.NO_CHANNELS
    if not has_cookies:
        return Hint.NO_COOKIES
    return None


def size_parts(size_bytes: float) -> tuple[float, str]:
    """Объём числом и единицей: до терабайта — в гигабайтах, дальше в терабайтах.

    «1331,2 ГБ» читается хуже, чем «1,30 ТБ», а архив канала легко за него
    переваливает.
    """
    гигабайты = size_bytes / 1024**3
    if гигабайты >= 1024:
        return гигабайты / 1024, "tb"
    return гигабайты, "gb"


def is_fresh(*, saved_at: float, saved_key, now: float, key, ttl: float) -> bool:
    """Годится ли сохранённый счёт файлов.

    Окно обновляется каждые две секунды и каждый раз обходило весь архив —
    две тысячи файлов. На локальном диске это незаметно, на сетевом окно
    начинало бы тормозить само себя.

    Счёт годится, пока не истёк срок И не изменился ключ. Ключ — это то, что
    меняется, когда меняется архив: учёт скачанного дописывается на каждом
    ролике. Поэтому новый ролик виден сразу, а не через минуту; срок нужен
    для того, чего ключ не ловит, — файлов, перенесённых руками.
    """
    return saved_key == key and 0 <= now - saved_at < ttl
