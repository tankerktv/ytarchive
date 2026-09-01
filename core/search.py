"""Поиск канала по названию.

Человек знает название, а не хендл — это и выяснилось на живом: «alex m»
дало трёх разных, из которых один на 2111 роликов и до 1,9 ТБ, а нужен был
совсем другой, на 37 роликов.

Отсюда главное требование: **объём показывается до добавления.** Разница
между 29 и 1929 гигабайтами должна быть видна при выборе, а не обнаруживаться
утром по забитому диску.

Здесь только разбор и арифметика. Сам поиск и перепись — в обёртке.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from core.planner import estimate_range

#: Идентификатор канала YouTube: UC и 22 символа.
CHANNEL_ID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")

#: Разделитель в строке выдачи. Задаётся нами же в `--print`, поэтому
#: менять его можно только вместе с обёрткой.
SEPARATOR = "|"


@dataclass(frozen=True)
class Candidate:
    """Найденный канал. Числа появляются не сразу: перепись большого канала
    занимает минуты, и окно показывает строку раньше, чем узнает объём."""

    name: str
    channel_id: str
    hits: int = 1
    videos: int | None = None
    seconds: float | None = None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/channel/{self.channel_id}/videos"

    @property
    def measured(self) -> bool:
        return self.videos is not None and self.seconds is not None

    def size_range(self) -> tuple[int, int] | None:
        return estimate_range(self.seconds) if self.measured else None

    def describe(self) -> str:
        """Строка для человека. Пока не измерено — так и говорим,
        а не показываем ноль: ноль выглядит как «пустой канал»."""
        if not self.measured:
            return "меряю…"
        низ, верх = self.size_range()
        return (
            f"{self.videos} роликов · {self.seconds / 3600:.1f} ч · "
            f"{низ / 1000**3:.0f}–{верх / 1000**3:.0f} ГБ"
        )


def parse_search_output(lines: list[str]) -> list[Candidate]:
    """Собрать кандидатов из выдачи поиска.

    Поиск возвращает ролики, а не каналы, поэтому один канал приходит
    несколько раз. Считаем попадания: чем их больше, тем вероятнее, что
    человек искал именно его — и тем выше он в списке.
    """
    порядок: list[str] = []
    имена: dict[str, str] = {}
    счёт: dict[str, int] = {}

    for raw in lines:
        строка = raw.strip()
        if SEPARATOR not in строка:
            continue
        имя, _, идентификатор = строка.rpartition(SEPARATOR)
        имя, идентификатор = имя.strip(), идентификатор.strip()
        if not имя or имя == "NA" or not CHANNEL_ID.match(идентификатор):
            continue
        if идентификатор not in счёт:
            порядок.append(идентификатор)
            имена[идентификатор] = имя
            счёт[идентификатор] = 0
        счёт[идентификатор] += 1

    кандидаты = [
        Candidate(name=имена[i], channel_id=i, hits=счёт[i]) for i in порядок
    ]
    # Сортировка устойчивая: при равном числе попаданий сохраняется
    # порядок выдачи YouTube, а он не случаен.
    return sorted(кандидаты, key=lambda c: -c.hits)


def with_measurement(candidate: Candidate, durations: list[float]) -> Candidate:
    """Дополнить кандидата переписью.

    Ролики без длительности не считаются вовсе: это обычно трансляции
    и премьеры, у которых её ещё нет. Включить их как нули значило бы
    занизить оценку объёма.
    """
    годные = [d for d in durations if d and d > 0]
    return replace(candidate, videos=len(годные), seconds=float(sum(годные)))


def fits(candidate: Candidate, free_bytes: int, reserve: int = 20 * 1024**3) -> bool | None:
    """Влезет ли по верхней границе. `None` — пока неизвестно.

    Судим по верхней границе намеренно: ошибиться в сторону «влезет»
    хуже, чем в сторону «не влезет». Первое кончается забитым диском
    посреди ночи, второе — лишним вопросом.
    """
    if not candidate.measured:
        return None
    _, верх = candidate.size_range()
    return free_bytes - reserve >= верх
