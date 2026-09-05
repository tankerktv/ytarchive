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

from core.progress import Event, EventKind, parse_line


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
    last_message: str = ""
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


#: Приметы сообщений цикла. Держим здесь, а не в окне: окно не должно
#: разбирать текст, иначе логика расползётся по слоям.
STOPPED_MARK = "остановлено — "
CHANNEL_MARK = ": проверка — "


def build_status(
    lines: list[str],
    *,
    process_running: bool,
    archive_count: int = 0,
) -> Status:
    """Собрать снимок состояния.

    `process_running` приходит снаружи намеренно: изнутри журнала отличить
    «идёт двухчасовой ролик» от «всё давно упало» невозможно.
    """
    current_file = ""
    channel = ""
    last_size: int | None = None
    last_speed: float | None = None
    errors = 0
    last_message = ""
    stopped_reason = ""
    sleeping = False

    for raw in lines:
        text = raw.strip()
        if not text:
            continue
        last_message = text

        # Строки цикла идут с отметкой времени в начале — отрезаем её,
        # чтобы разбор прогресса видел то же, что печатает yt-dlp.
        # Обрезать пробелы обязательно: наши строки идут с отступом,
        # и без этого проверки на начало строки молча не срабатывают.
        body = (text.split("  ", 1)[1] if _starts_with_time(text) else text).strip()

        if STOPPED_MARK in body:
            stopped_reason = body.split(STOPPED_MARK, 1)[1]
        if CHANNEL_MARK in body:
            channel = body.split(CHANNEL_MARK, 1)[0].strip()

        event: Event = parse_line(body.strip())
        if event.kind is EventKind.DESTINATION:
            current_file = _basename(event.path)
            sleeping = False
        elif event.kind is EventKind.COMPLETED:
            last_size = event.size_bytes
            last_speed = event.speed_bps
        elif event.kind is EventKind.ERROR:
            errors += 1
        elif event.kind is EventKind.SLEEPING:
            sleeping = True
        elif body.startswith("качаю "):
            current_file = body[len("качаю "):].strip()
            sleeping = False
        elif body.startswith("готово "):
            pass

    if stopped_reason:
        state = RunState.NEEDS_HUMAN
    elif not process_running:
        state = RunState.IDLE
    elif sleeping:
        state = RunState.BETWEEN
    else:
        state = RunState.RUNNING

    return Status(
        state=state,
        current_file=current_file if state.is_working else "",
        channel=channel,
        last_size_bytes=last_size,
        last_speed_bps=last_speed,
        errors=errors,
        archive_count=archive_count,
        last_message=last_message,
        stopped_reason=stopped_reason,
    )


def _starts_with_time(text: str) -> bool:
    return (
        len(text) >= 8
        and text[2] == ":"
        and text[5] == ":"
        and text[:2].isdigit()
        and text[3:5].isdigit()
    )


def _basename(path: str) -> str:
    for sep in ("\\", "/"):
        if sep in path:
            path = path.rsplit(sep, 1)[1]
    return path
