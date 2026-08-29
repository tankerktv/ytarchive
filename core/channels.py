"""Разбор списка каналов.

Формат строки: `Название|URL`. Название задаёт папку, URL — откуда брать перепись.

Правило разбора одно: **ничего не выбрасывается молча.** Строку, которую мы
не поняли, вернём отдельным списком, чтобы она попала в журнал. Молчаливое
отбрасывание строки из списка каналов означает, что канал просто перестанет
качаться, и заметят это через недели.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SEPARATOR = "|"
COMMENT_PREFIX = "#"

#: Символы, недопустимые в имени папки на Windows. Название канала приходит
#: от человека и уезжает в путь, поэтому проверяется здесь, а не при записи:
#: узнать о плохом имени лучше при разборе списка, чем на середине скачивания.
FORBIDDEN_IN_PATH = re.compile(r'[<>:"/\\|?*]')


@dataclass(frozen=True)
class Channel:
    name: str
    url: str


@dataclass(frozen=True)
class Problem:
    """Строка, которую не удалось разобрать, с объяснением почему."""

    line_number: int
    text: str
    reason: str


@dataclass(frozen=True)
class ParseResult:
    channels: tuple[Channel, ...] = ()
    problems: tuple[Problem, ...] = ()


def parse_channels(text: str) -> ParseResult:
    """Разобрать список каналов.

    Пустой список — законный результат, но вызывающий обязан отличать его от
    «файл не прочитался»: качать нечего и качать нечем — разные беды.
    """
    channels: list[Channel] = []
    problems: list[Problem] = []
    seen_names: dict[str, int] = {}

    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue

        if SEPARATOR not in line:
            problems.append(Problem(number, line, "нет разделителя «|»"))
            continue

        name, _, url = line.partition(SEPARATOR)
        name, url = name.strip(), url.strip()

        if not name:
            problems.append(Problem(number, line, "пустое название канала"))
            continue
        if not url:
            problems.append(Problem(number, line, "пустой адрес канала"))
            continue
        if FORBIDDEN_IN_PATH.search(name):
            problems.append(Problem(number, line, "в названии символы, недопустимые в имени папки"))
            continue
        if not url.startswith(("http://", "https://")):
            problems.append(Problem(number, line, "адрес не начинается с http:// или https://"))
            continue

        # Тёзки не сливаем и не переименовываем: два канала в одну папку —
        # это перемешанный архив, разобрать который потом нельзя.
        if name in seen_names:
            problems.append(
                Problem(number, line, f"название повторяет строку {seen_names[name]}")
            )
            continue

        seen_names[name] = number
        channels.append(Channel(name=name, url=url))

    return ParseResult(channels=tuple(channels), problems=tuple(problems))
