"""Разбор вывода yt-dlp в события, понятные интерфейсу.

Все образцы строк взяты дословно из журналов выкачки за 16–29.08.2026,
поэтому разбор проверяется на том, что YouTube и yt-dlp печатают на самом деле,
а не на том, что я про них помню.

Разбор чужого формата — та категория, где тесты окупаются лучше всего:
вывод меняется от версии к версии, а версия yt-dlp меняется чуть ли не
еженедельно. Без проверок поломка обнаружится через неделю тишины.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class EventKind(Enum):
    DESTINATION = "начал файл"
    PROGRESS = "идёт загрузка"
    COMPLETED = "файл докачан"
    ITEM = "перешёл к следующему ролику"
    MERGING = "сливает потоки"
    SLEEPING = "пауза"
    ERROR = "отказ"
    OTHER = "прочее"


@dataclass(frozen=True)
class Event:
    kind: EventKind
    text: str
    path: str = ""
    size_bytes: int | None = None
    seconds: float | None = None
    speed_bps: float | None = None
    index: int | None = None
    total: int | None = None
    percent: float | None = None
    eta: str = ""

    @property
    def is_error(self) -> bool:
        return self.kind is EventKind.ERROR


#: Двоичные приставки: yt-dlp печатает MiB и GiB, а не MB и GB.
#: Спутать их — ошибиться на 5% на мегабайтах и на 7% на гигабайтах,
#: что незаметно портит любую оценку остатка.
_UNITS = {
    "b": 1,
    "kib": 1024,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
}

_DESTINATION = re.compile(r"^\[download\]\s+Destination:\s*(?P<path>.+?)\s*$")
_COMPLETED = re.compile(
    r"^\[download\]\s+100%\s+of\s+(?P<size>[\d.]+)(?P<unit>[KMGT]?i?B)"
    r"(?:\s+in\s+(?P<time>[\d:]+))?"
    r"(?:\s+at\s+(?P<speed>[\d.]+)(?P<sunit>[KMGT]?i?B)/s)?",
    re.IGNORECASE,
)
#: Строка идущей загрузки. Размер бывает с тильдой (`~1.23GiB`) — это оценка,
#: пока сервер не сказал точный размер; скорость и остаток бывают `Unknown`,
#: и это законно, а не поломка: в самом начале их ещё неоткуда взять.
_PROGRESS = re.compile(
    r"^\[download\]\s+(?P<percent>[\d.]+)%\s+of\s+~?\s*(?P<size>[\d.]+)(?P<unit>[KMGT]?i?B)"
    r"(?:\s+at\s+(?:(?P<speed>[\d.]+)(?P<sunit>[KMGT]?i?B)/s|Unknown\s*B?/?s?))?"
    r"(?:\s+ETA\s+(?P<eta>[\d:]+|Unknown))?",
    re.IGNORECASE,
)

_ITEM = re.compile(r"^\[download\]\s+Downloading item\s+(?P<index>\d+)\s+of\s+(?P<total>\d+)")
_MERGING = re.compile(r'^\[Merger\]\s+Merging formats into\s+"(?P<path>.+)"')
_SLEEPING = re.compile(r"Sleeping\s+(?P<seconds>[\d.]+)\s+seconds", re.IGNORECASE)
_ERROR = re.compile(r"^\s*ERROR[:\s]", re.IGNORECASE)


def parse_size(value: str, unit: str) -> int:
    """Перевести «462.12MiB» в байты."""
    key = unit.lower()
    if key not in _UNITS:
        raise ValueError(f"неизвестная единица размера: {unit!r}")
    return int(float(value) * _UNITS[key])


def parse_duration(value: str) -> float:
    """Перевести «00:08:45» или «01:46» в секунды."""
    parts = value.split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"не похоже на длительность: {value!r}")
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60 + float(part)
    return seconds


def parse_line(line: str) -> Event:
    """Разобрать одну строку вывода.

    Неопознанная строка возвращается как OTHER, а не отбрасывается: пусть
    интерфейс решает, показывать её или нет. Молчаливое отбрасывание однажды
    стоило нам месяца незамеченной потери данных.
    """
    stripped = line.rstrip()

    if _ERROR.match(stripped):
        return Event(kind=EventKind.ERROR, text=stripped)

    match = _DESTINATION.match(stripped)
    if match:
        return Event(kind=EventKind.DESTINATION, text=stripped, path=match.group("path"))

    match = _COMPLETED.match(stripped)
    if match:
        size = parse_size(match.group("size"), match.group("unit"))
        seconds = parse_duration(match.group("time")) if match.group("time") else None
        speed = None
        if match.group("speed"):
            speed = float(parse_size(match.group("speed"), match.group("sunit")))
        return Event(
            kind=EventKind.COMPLETED,
            text=stripped,
            size_bytes=size,
            seconds=seconds,
            speed_bps=speed,
        )

    # Идущая загрузка проверяется ПОСЛЕ завершённой: строка «100% of … in …»
    # тоже начинается с процентов, и порядок здесь несущий.
    match = _PROGRESS.match(stripped)
    if match:
        speed = None
        if match.group("speed"):
            speed = float(parse_size(match.group("speed"), match.group("sunit")))
        eta = match.group("eta") or ""
        return Event(
            kind=EventKind.PROGRESS,
            text=stripped,
            percent=float(match.group("percent")),
            size_bytes=parse_size(match.group("size"), match.group("unit")),
            speed_bps=speed,
            eta="" if eta.lower() == "unknown" else eta,
        )

    match = _ITEM.match(stripped)
    if match:
        return Event(
            kind=EventKind.ITEM,
            text=stripped,
            index=int(match.group("index")),
            total=int(match.group("total")),
        )

    match = _MERGING.match(stripped)
    if match:
        return Event(kind=EventKind.MERGING, text=stripped, path=match.group("path"))

    match = _SLEEPING.search(stripped)
    if match:
        return Event(kind=EventKind.SLEEPING, text=stripped, seconds=float(match.group("seconds")))

    return Event(kind=EventKind.OTHER, text=stripped)
