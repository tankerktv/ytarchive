"""Картинки в кэше: логотипы каналов и миниатюры роликов.

Кэш обязателен. Окно обновляется каждые две секунды, а в списке роликов
картинок бывает шестьсот; тянуть их из сети на каждое обновление — это
тысячи запросов в час ради того, что не меняется месяцами.

Ни одна беда здесь не должна ничего ронять: картинка — украшение, а не смысл.
Нет сети, нет файла, испорченный ответ — окно просто рисует пустую ячейку.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

#: Больше этого картинка быть не должна: логотип YouTube — сотня-другая
#: килобайт, миниатюра и того меньше. Всё крупное означает, что мы качаем
#: не то, и класть это в кэш не надо.
MAX_BYTES = 4 * 1024 * 1024


def cache_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}.img"


def ensure_image(cache_dir: Path, key: str, url: str) -> Path | None:
    """Положить картинку в кэш и вернуть путь. `None` — не вышло, и это не беда.

    Уже лежащий файл не перекачиваем: ни логотипы, ни миниатюры не меняются.
    """
    if not key or not url:
        return None

    путь = cache_path(cache_dir, key)
    if путь.exists() and путь.stat().st_size > 0:
        return путь

    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        запрос = urllib.request.Request(url, headers={"User-Agent": "ytarchive"})
        with urllib.request.urlopen(запрос, timeout=15) as ответ:
            данные = ответ.read(MAX_BYTES + 1)
    except (urllib.error.URLError, OSError, ValueError):
        return None

    if not данные or len(данные) > MAX_BYTES:
        return None

    try:
        путь.write_bytes(данные)
    except OSError:
        return None
    return путь


def cached_image(cache_dir: Path, key: str) -> Path | None:
    """Картинка, если она уже скачана. В сеть не ходим — зовётся из отрисовки."""
    путь = cache_path(cache_dir, key)
    try:
        return путь if путь.exists() and путь.stat().st_size > 0 else None
    except OSError:
        return None
