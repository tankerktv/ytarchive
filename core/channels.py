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
from enum import Enum

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


HEADER = (
    "# Каналы для выкачки. Формат: <Папка>|<адрес вкладки videos>\n"
    "# Строки с # игнорируются. Название задаёт папку в архиве.\n"
    "# Переименовывать лучше из окна: оно переименует и папку. Поправив имя\n"
    "# здесь руками, получите новую папку, а прежняя останется как есть.\n"
)


def format_channels(channels: tuple[Channel, ...] | list[Channel]) -> str:
    """Собрать текст списка каналов.

    Обратимость с `parse_channels` проверена тестом: окно правит этот файл,
    и потеря канала при записи означала бы, что он просто перестанет
    качаться — молча, до тех пор пока кто-нибудь не заметит.
    """
    строки = [f"{c.name}{SEPARATOR}{c.url}" for c in channels]
    return HEADER + "\n".join(строки) + ("\n" if строки else "")


def move_channel(
    channels: tuple[Channel, ...] | list[Channel], index: int, delta: int
) -> tuple[Channel, ...]:
    """Переставить канал в списке.

    Порядок списка — это порядок обхода: очередь строится по нему, и первый
    канал забирается первым. Значит перестановка и есть управление
    приоритетом, отдельного поля для него заводить незачем.

    Выход за край — не ошибка, а «дальше некуда»: список возвращается как был.
    """
    список = list(channels)
    если_некуда = tuple(список)
    if not 0 <= index < len(список):
        return если_некуда
    куда = index + delta
    if not 0 <= куда < len(список):
        return если_некуда
    список[index], список[куда] = список[куда], список[index]
    return tuple(список)


def remove_channel(
    channels: tuple[Channel, ...] | list[Channel], index: int
) -> tuple[Channel, ...]:
    """Убрать канал из списка.

    Скачанное при этом остаётся на диске и в учёте — убираем из очереди,
    а не из архива. Вернуть канал обратно можно, и заново он не полезет.
    """
    список = list(channels)
    if not 0 <= index < len(список):
        return tuple(список)
    del список[index]
    return tuple(список)


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


# --- переименование ---------------------------------------------------------


class RenameVerdict(Enum):
    """Можно ли дать каналу такое имя. Причина отказа — значением, а не
    текстом: текст показывает окно, и на своём языке."""

    OK = "ok"
    NO_SUCH = "no-such"
    EMPTY = "empty"
    FORBIDDEN = "forbidden"
    SAME = "same"
    DUPLICATE = "duplicate"


def check_rename(
    channels: tuple[Channel, ...] | list[Channel], index: int, new_name: str
) -> RenameVerdict:
    """Проверить новое имя канала. Имя — оно же имя папки, отсюда строгость."""
    список = list(channels)
    if not 0 <= index < len(список):
        return RenameVerdict.NO_SUCH

    имя = new_name.strip()
    if not имя:
        return RenameVerdict.EMPTY
    if FORBIDDEN_IN_PATH.search(имя):
        return RenameVerdict.FORBIDDEN
    if имя == список[index].name:
        return RenameVerdict.SAME

    # Сравниваем без учёта регистра: на Windows «soyuz» и «Soyuz» — одна
    # папка, и два канала в ней дали бы перемешанный архив, разобрать который
    # потом нельзя. Самого себя не считаем: поменять регистр своего имени можно.
    for номер, канал in enumerate(список):
        if номер != index and канал.name.casefold() == имя.casefold():
            return RenameVerdict.DUPLICATE
    return RenameVerdict.OK


def rename_channel(
    channels: tuple[Channel, ...] | list[Channel], index: int, new_name: str
) -> tuple[Channel, ...]:
    """Список с переименованным каналом. Порядок и адрес не меняются."""
    приговор = check_rename(channels, index, new_name)
    if приговор is not RenameVerdict.OK:
        raise ValueError(f"переименовать нельзя: {приговор.value}")
    список = list(channels)
    список[index] = Channel(name=new_name.strip(), url=список[index].url)
    return tuple(список)


class FolderMove(Enum):
    """Что делать с папкой при переименовании канала."""

    NOTHING = "nothing"
    MOVE = "move"
    CONFLICT = "conflict"


def judge_folder_rename(*, old_exists: bool, new_exists: bool, same_folder: bool) -> FolderMove:
    """Решить судьбу папки.

    Переименование канала без папки и есть тот раскол, который уже случался:
    новое пошло бы в новую папку, старое осталось бы в прежней. Поэтому папка
    едет вместе с именем.

    Если папка с новым именем уже есть и это ДРУГАЯ папка — отказ. Сливать
    две папки молча нельзя: там могут лежать ролики другого канала.
    `same_folder` — случай смены одного регистра: для Windows это та же папка,
    и её можно просто переименовать.
    """
    if not old_exists:
        return FolderMove.NOTHING
    if new_exists and not same_folder:
        return FolderMove.CONFLICT
    return FolderMove.MOVE
