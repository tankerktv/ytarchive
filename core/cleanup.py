"""Что из накопившегося можно убрать: старые журналы и обломки загрузок.

Каждый проход заводит свой журнал — за месяц их набирается под две тысячи.
А прерванная загрузка оставляет недокачанный файл, который yt-dlp потом
продолжит; если ролик так и не понадобился, обломок лежит вечно.

Здесь только отбор: на входе имена с возрастом, на выходе — что убрать.
Удаляет обёртка, и только после того, как список показан человеку.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

СУТКИ = 86400.0

#: Сколько самых свежих журналов не трогаем никогда, сколько бы им ни было.
#: Программа могла простоять выключенной полгода: вернувшись, человек должен
#: найти журналы последних проходов, а не пустую папку.
KEEP_NEWEST = 20

#: Хвосты имён, которыми yt-dlp помечает недокачанное.
_ОБЛОМОК = re.compile(r"\.(part|ytdl)$|\.part-Frag\d+$", re.IGNORECASE)
_ID = re.compile(r"\[([A-Za-z0-9_-]{11})\]")


@dataclass(frozen=True)
class FileInfo:
    name: str
    modified: float
    size: int = 0


def old_logs(
    logs: list[FileInfo], now: float, keep_days: float, keep_newest: int = KEEP_NEWEST
) -> list[FileInfo]:
    """Журналы старше `keep_days` суток. Ноль суток — хранить всё.

    Самые свежие `keep_newest` не отдаём, даже если они старые.
    """
    if keep_days <= 0:
        return []
    по_свежести = sorted(logs, key=lambda файл: файл.modified, reverse=True)
    кандидаты = по_свежести[keep_newest:]
    граница = now - keep_days * СУТКИ
    return sorted((файл for файл in кандидаты if файл.modified < граница), key=lambda ф: ф.name)


def is_leftover(name: str) -> bool:
    return bool(_ОБЛОМОК.search(name))


def stale_leftovers(
    files: list[FileInfo], now: float, downloaded: frozenset[str], older_than_days: float = 7.0
) -> list[FileInfo]:
    """Обломки, которые уже не пригодятся.

    Убирать можно в двух случаях:

    * ролик уже в учёте — он скачан целиком, обломок остался от старой попытки;
    * обломок не трогали дольше `older_than_days` — загрузку давно бросили.

    Свежий обломок нескачанного ролика не трогаем: это продолжение, которое
    yt-dlp подхватит следующим проходом. Удалив его, мы бы заставили качать
    гигабайты заново — ровно то, ради чего обломки и хранятся.
    """
    граница = now - older_than_days * СУТКИ
    итог = []
    for файл in files:
        if not is_leftover(файл.name):
            continue
        найдено = _ID.search(файл.name)
        уже_скачан = bool(найдено) and найдено.group(1) in downloaded
        if уже_скачан or файл.modified < граница:
            итог.append(файл)
    return sorted(итог, key=lambda ф: ф.name)


def total_size(files: list[FileInfo]) -> int:
    return sum(файл.size for файл in files)
