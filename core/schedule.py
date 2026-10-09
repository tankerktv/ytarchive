"""Ритм проходов: сколько ждать до следующего.

Раньше это решал планировщик Windows — «каждые полчаса», одинаково на все
случаи. Своё расписание позволяет отвечать на то, чем кончился проход,
и это не украшение:

* что-то скачали — почти наверняка в очереди осталось ещё, и ждать полчаса
  впустую значит растянуть архив на недели;
* ничего не нашлось — новые ролики выходят не каждую минуту, и частые
  проверки только жгут запросы к YouTube;
* нужен человек — куки сами не появятся. Долбиться каждые полчаса в стену
  бессмысленно и вредно: именно так и зарабатывается «подтвердите, что вы
  не бот».

Здесь только арифметика, без сна и без часов, — чтобы решение можно было
проверить мгновенно, а не ждать его полчаса.
"""

from __future__ import annotations

from dataclasses import dataclass

МИНУТА = 60.0


@dataclass(frozen=True)
class Rhythm:
    """Пределы ожидания между проходами, в секундах."""

    #: Ничего нового не нашлось.
    idle: float = 30 * МИНУТА
    #: Что-то скачали — вернуться скоро.
    busy: float = 1 * МИНУТА
    #: Нужен человек: истёкшие куки, устаревший yt-dlp.
    trouble: float = 60 * МИНУТА

    def __post_init__(self) -> None:
        for имя, значение in (
            ("idle", self.idle),
            ("busy", self.busy),
            ("trouble", self.trouble),
        ):
            if значение <= 0:
                raise ValueError(f"{имя} должен быть больше нуля, а не {значение}")
        if self.busy > self.idle:
            # Иначе «нашлась работа» замедляло бы выкачку вместо ускорения —
            # ровно наоборот смыслу.
            raise ValueError("пауза после удачного прохода не должна быть длиннее холостой")


def next_pause(*, downloaded: int, needs_human: bool, rhythm: Rhythm) -> float:
    """Сколько ждать после прохода.

    Порядок проверок важен: «нужен человек» перевешивает удачу. Проход мог
    забрать половину канала и упереться в истёкшие куки — возвращаться через
    минуту, чтобы снова упереться, незачем.
    """
    if needs_human:
        return rhythm.trouble
    if downloaded > 0:
        return rhythm.busy
    return rhythm.idle


# --- часы работы ---

МИНУТ_В_СУТКАХ = 24 * 60


@dataclass(frozen=True)
class Hours:
    """Отрезок суток, когда качать можно. Минуты от полуночи.

    Начало позже конца — законно: «23:00–07:00» переходит через полночь,
    и ради ночной выкачки это и задумано.
    """

    start: int
    end: int

    def __post_init__(self) -> None:
        for значение in (self.start, self.end):
            if not 0 <= значение < МИНУТ_В_СУТКАХ:
                raise ValueError("время суток — от 00:00 до 23:59")
        if self.start == self.end:
            # Нулевой отрезок или целые сутки? Угадывать не будем: «качать
            # всегда» задаётся пустой строкой, а не одинаковыми концами.
            raise ValueError("начало и конец совпадают — чтобы качать всегда, оставьте поле пустым")


def _минуты(текст: str) -> int:
    часть = текст.strip()
    часы, знак, минуты = часть.partition(":")
    if not часы.isdigit() or (знак and not минуты.isdigit()):
        raise ValueError(f"время пишется как ЧЧ или ЧЧ:ММ, а не «{часть}»")
    итог = int(часы) * 60 + (int(минуты) if знак else 0)
    if int(часы) > 23 or (знак and int(минуты) > 59):
        raise ValueError(f"нет такого времени суток: «{часть}»")
    return итог


def parse_hours(text: str) -> Hours | None:
    """Разобрать «23-7» или «23:00-07:30». Пустая строка — качать всегда."""
    очищенный = text.strip()
    if not очищенный:
        return None
    начало, знак, конец = очищенный.partition("-")
    if not знак:
        raise ValueError(f"часы работы пишутся как «23-7» или «23:00-07:30», а не «{очищенный}»")
    return Hours(start=_минуты(начало), end=_минуты(конец))


def format_hours(hours: Hours | None) -> str:
    if hours is None:
        return ""
    return f"{clock_text(hours.start)}-{clock_text(hours.end)}"


def clock_text(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def is_open(hours: Hours | None, minute: float) -> bool:
    """Можно ли качать в эту минуту суток. Конец отрезка в него не входит."""
    if hours is None:
        return True
    if hours.start < hours.end:
        return hours.start <= minute < hours.end
    return minute >= hours.start or minute < hours.end


def minutes_until_open(hours: Hours | None, minute: float) -> float:
    """Сколько минут ждать до открытия. Ноль — уже открыто."""
    if is_open(hours, minute):
        return 0.0
    assert hours is not None
    return (hours.start - minute) % МИНУТ_В_СУТКАХ
