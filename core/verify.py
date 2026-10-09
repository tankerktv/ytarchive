"""Сверка учёта с диском: что числится скачанным и что лежит на самом деле.

Учёт ведёт yt-dlp, файлы лежат в папках каналов, и связывает их только
дисциплина. Разойтись они могут в обе стороны:

* ролик в учёте, файла нет — файл удалили или перенесли руками. Заново он
  не скачается никогда: программа считает его забранным;
* файл есть, в учёте нет — учёт восстанавливали из копии или правили.
  Ролик скачается второй раз;
* строка в учёте повторяется — безвредно, но счёт строк расходится со счётом
  роликов и сбивает с толку при разборе.

Здесь только сравнение множеств. Диск читает обёртка.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.archive import EXTRACTOR_KEY, VIDEO_ID

#: Идентификатор в имени файла — в квадратных скобках перед расширением.
_ID_В_ИМЕНИ = re.compile(r"\[([A-Za-z0-9_-]{11})\]\.[A-Za-z0-9]+$")

#: Что считаем роликом. Субтитры, обложки и обломки с тем же идентификатором
#: роликом не являются: наличие `.jpg` не значит, что видео на месте.
VIDEO_SUFFIXES = (".mkv", ".mp4", ".webm", ".mov", ".m4v")


def id_of(name: str) -> str:
    """Идентификатор ролика из имени файла; пусто, если это не ролик."""
    if not name.lower().endswith(VIDEO_SUFFIXES):
        return ""
    найдено = _ID_В_ИМЕНИ.search(name)
    return найдено.group(1) if найдено else ""


@dataclass(frozen=True)
class Report:
    #: В учёте есть, файла нет.
    missing_files: tuple[str, ...] = ()
    #: Файл есть, в учёте нет: идентификатор → имя файла.
    unrecorded: tuple[tuple[str, str], ...] = ()
    #: Идентификаторы, записанные в учёт больше одного раза, и сколько раз.
    duplicates: tuple[tuple[str, int], ...] = ()
    #: Один ролик лежит в нескольких файлах: идентификатор → имена.
    twins: tuple[tuple[str, tuple[str, ...]], ...] = ()
    records: int = 0
    files: int = 0

    @property
    def clean(self) -> bool:
        return not (self.missing_files or self.unrecorded or self.duplicates or self.twins)

    @property
    def extra_lines(self) -> int:
        return sum(раз - 1 for _ролик, раз in self.duplicates)


def archive_ids_in_order(text: str) -> list[str]:
    """Идентификаторы из учёта, с повторами и в порядке файла."""
    итог = []
    for строка in text.splitlines():
        части = строка.split()
        if len(части) == 2 and части[0] == EXTRACTOR_KEY and VIDEO_ID.match(части[1]):
            итог.append(части[1])
    return итог


def compare(archive_text: str, file_names: list[str]) -> Report:
    """Сравнить учёт с именами файлов.

    `file_names` — пути относительно папки архива: по ним человек найдёт
    файл, а по одному имени в пяти папках каналов — нет.
    """
    записи = archive_ids_in_order(archive_text)
    счёт: dict[str, int] = {}
    for ролик in записи:
        счёт[ролик] = счёт.get(ролик, 0) + 1

    на_диске: dict[str, list[str]] = {}
    for имя in file_names:
        ролик = id_of(имя)
        if ролик:
            на_диске.setdefault(ролик, []).append(имя)

    return Report(
        missing_files=tuple(sorted(ролик for ролик in счёт if ролик not in на_диске)),
        unrecorded=tuple(
            sorted((ролик, имена[0]) for ролик, имена in на_диске.items() if ролик not in счёт)
        ),
        duplicates=tuple(sorted((ролик, раз) for ролик, раз in счёт.items() if раз > 1)),
        twins=tuple(
            sorted((ролик, tuple(sorted(имена))) for ролик, имена in на_диске.items() if len(имена) > 1)
        ),
        records=len(записи),
        files=sum(len(имена) for имена in на_диске.values()),
    )


def without_duplicates(archive_text: str) -> str:
    """Учёт без повторных строк. Порядок и непонятые строки сохраняются.

    Непонятое не выбрасываем: это чужой формат, который читает yt-dlp, и
    «почистив» строку, смысла которой не знаем, можно обнулить учёт.
    """
    видели: set[str] = set()
    итог = []
    for строка in archive_text.splitlines():
        части = строка.split()
        понятая = len(части) == 2 and части[0] == EXTRACTOR_KEY and VIDEO_ID.match(части[1])
        if понятая:
            if части[1] in видели:
                continue
            видели.add(части[1])
        итог.append(строка)
    return "\n".join(итог) + ("\n" if итог else "")
