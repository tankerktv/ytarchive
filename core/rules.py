"""Правила отбора роликов канала: не короче, не длиннее, не старше.

Галочки снимают ролики поштучно, и на канале в шестьсот роликов это вечер
работы. Правило говорит то же одной строкой — и действует на ролики, которые
ещё не вышли.

Правила пишутся третьим полем в строке канала:

    Имя|адрес|min=60;max=7200;after=2024-01-01

Правило вычёркивает ролик из очереди, но ничего не удаляет с диска и не
трогает учёт: уберите правило — ролик вернётся в очередь.

**Неизвестное правилу не подчиняется.** У трансляции нет длительности,
у части роликов перепись не отдаёт дату. Такой ролик проходит: потерять
ролик молча хуже, чем скачать лишний.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SEPARATOR = ";"
_ДАТА = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

#: Ключи, которые мы понимаем. Остальное — опечатка, и о ней надо сказать.
KNOWN = ("min", "max", "after")


@dataclass(frozen=True)
class Rules:
    #: Не короче стольких секунд. Ноль — без ограничения.
    min_seconds: int = 0
    #: Не длиннее стольких секунд. Ноль — без ограничения.
    max_seconds: int = 0
    #: Не старше этой даты, в виде ГГГГММДД — так её печатает yt-dlp, и так
    #: строки сравниваются без разбора. Пусто — без ограничения.
    after: str = ""

    def __bool__(self) -> bool:
        return bool(self.min_seconds or self.max_seconds or self.after)


class RulesError(ValueError):
    """Правило не разобрано. Текст — для человека, который его писал."""


def parse_rules(text: str) -> Rules:
    """Разобрать поле правил. Пустое поле — правил нет.

    Непонятное не пропускается молча: опечатка в `mни=60` означала бы, что
    человек считает короткие ролики отсечёнными, а они качаются.
    """
    min_seconds = max_seconds = 0
    after = ""
    for кусок in text.split(SEPARATOR):
        кусок = кусок.strip()
        if not кусок:
            continue
        ключ, знак, значение = кусок.partition("=")
        ключ, значение = ключ.strip().lower(), значение.strip()
        if not знак or ключ not in KNOWN:
            raise RulesError(f"непонятное правило «{кусок}»; понятные: {', '.join(KNOWN)}")
        if ключ == "after":
            найдено = _ДАТА.match(значение)
            if not найдено or not _дата_бывает(*map(int, найдено.groups())):
                raise RulesError(f"дата в правиле after пишется как ГГГГ-ММ-ДД, а не «{значение}»")
            after = "".join(найдено.groups())
            continue
        if not значение.isdigit():
            raise RulesError(f"в правиле {ключ} нужны секунды целым числом, а не «{значение}»")
        if ключ == "min":
            min_seconds = int(значение)
        else:
            max_seconds = int(значение)

    if min_seconds and max_seconds and min_seconds > max_seconds:
        raise RulesError("min больше max — под такое правило не подойдёт ни один ролик")
    return Rules(min_seconds=min_seconds, max_seconds=max_seconds, after=after)


def _дата_бывает(год: int, месяц: int, день: int) -> bool:
    from datetime import date

    try:
        date(год, месяц, день)
    except ValueError:
        return False
    return True


def format_rules(rules: Rules) -> str:
    """Собрать поле правил. Обратимо с `parse_rules` — проверено тестом."""
    части = []
    if rules.min_seconds:
        части.append(f"min={rules.min_seconds}")
    if rules.max_seconds:
        части.append(f"max={rules.max_seconds}")
    if rules.after:
        части.append(f"after={rules.after[:4]}-{rules.after[4:6]}-{rules.after[6:]}")
    return SEPARATOR.join(части)


def allows(rules: Rules, seconds: float, upload_date: str) -> bool:
    """Проходит ли ролик. `seconds` ≤ 0 и пустая дата значат «неизвестно»."""
    if seconds > 0:
        if rules.min_seconds and seconds < rules.min_seconds:
            return False
        if rules.max_seconds and seconds > rules.max_seconds:
            return False
    if rules.after and upload_date and upload_date < rules.after:
        return False
    return True
