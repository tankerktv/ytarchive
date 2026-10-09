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
            return f"{состояние}: {self.stopped_reason}"
        if self.state is RunState.IDLE:
            сколько = перевод("в архиве {} роликов").format(self.archive_count)
            return f"{состояние} · {сколько}"
        if self.current_file:
            return f"{состояние}: {self.current_file}"
        return состояние


def build_status(
    *,
    process_running: bool,
    archive_count: int = 0,
    live=None,
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
        state = RunState.IDLE
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
