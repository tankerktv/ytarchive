"""Библиотека: что уже лежит в архиве и как это показать.

Программа умела скачать, но не помогала смотреть: найти ролик означало идти
в проводник и листать папку на шестьсот файлов. Здесь — список скачанного
по всем каналам разом, с поиском и порядком.

Источник правды — имена файлов. В имени есть всё нужное: дата выхода,
название, идентификатор; папка называет канал. Учёт скачанного для этого
не годится — в нём одни идентификаторы.

Чистая логика: на входе имена и размеры, на выходе записи. Диск читает обёртка.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from core.verify import VIDEO_SUFFIXES

_ИМЯ = re.compile(
    r"^(?:(?P<год>\d{4})-(?P<месяц>\d{2})-(?P<день>\d{2}) - )?"
    r"(?P<название>.+?) \[(?P<ролик>[A-Za-z0-9_-]{11})\]\.(?P<расширение>[A-Za-z0-9]+)$"
)


@dataclass(frozen=True)
class Item:
    video_id: str
    title: str
    channel: str
    #: Путь относительно папки архива — по нему обёртка откроет файл.
    path: str
    #: Дата выхода, ГГГГММДД. Пусто, если в имени её нет.
    date: str = ""
    size_bytes: int = 0
    #: Ролика больше нет в списке канала на YouTube: удалён или скрыт.
    gone: bool = False

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    @property
    def thumbnail_url(self) -> str:
        return f"https://i.ytimg.com/vi/{self.video_id}/mqdefault.jpg"

    @property
    def date_text(self) -> str:
        if len(self.date) != 8:
            return "—"
        return f"{self.date[:4]}-{self.date[4:6]}-{self.date[6:]}"


def parse_name(channel: str, name: str, size_bytes: int = 0) -> Item | None:
    """Запись из имени файла. None — это не ролик нашего архива.

    Обломки, обложки и субтитры несут тот же идентификатор, но роликом не
    являются: показать `.part` в библиотеке значило бы обещать то, что
    не откроется.
    """
    if not name.lower().endswith(VIDEO_SUFFIXES):
        return None
    найдено = _ИМЯ.match(name)
    if not найдено:
        return None
    дата = ""
    if найдено.group("год"):
        дата = найдено.group("год") + найдено.group("месяц") + найдено.group("день")
    return Item(
        video_id=найдено.group("ролик"),
        title=найдено.group("название"),
        channel=channel,
        path=f"{channel}/{name}",
        date=дата,
        size_bytes=size_bytes,
    )


def build(
    files: list[tuple[str, str, int]], gone: frozenset[str] = frozenset()
) -> list[Item]:
    """Собрать библиотеку из троек (канал, имя файла, размер).

    Порядок — свежие сверху: человек чаще ищет то, что вышло недавно.
    Ролики без даты уходят в конец, а не теряются.
    """
    записи = []
    for канал, имя, размер in files:
        запись = parse_name(канал, имя, размер)
        if запись is None:
            continue
        if запись.video_id in gone:
            запись = replace(запись, gone=True)
        записи.append(запись)
    return sorted(записи, key=lambda з: (з.date or "0", з.title.casefold()), reverse=True)


def matches(item: Item, *, query: str = "", channel: str = "", only_gone: bool = False) -> bool:
    """Подходит ли запись под отбор. Пустой отбор пропускает всё."""
    if channel and item.channel != channel:
        return False
    if only_gone and not item.gone:
        return False
    запрос = query.strip().casefold()
    return not запрос or запрос in item.title.casefold()


def description_from_tags(tags: dict) -> str:
    """Описание ролика из меток файла.

    yt-dlp вшивает описание в сам файл при загрузке, поэтому оно есть и у
    роликов, скачанных задолго до появления библиотеки. Имя метки зависит от
    контейнера: в mkv — `DESCRIPTION`, в mp4 — `description`. В `comment`
    лежит адрес ролика, а не описание, — его не берём.
    """
    по_имени = {str(ключ).lower(): значение for ключ, значение in tags.items()}
    for имя in ("description", "synopsis"):
        значение = по_имени.get(имя)
        if isinstance(значение, str) and значение.strip():
            return значение.strip()
    return ""
