"""Логотипы каналов: узнать адрес, скачать, положить в кэш.

Кэш обязателен. Окно обновляется каждые две секунды, и тянуть картинки
из сети на каждое обновление — это тысячи запросов в час ради того, что
не меняется месяцами.

Ни одна беда здесь не должна ничего ронять: логотип — украшение, а не смысл.
Нет сети, нет картинки, испорченный файл — окно просто рисует пустую ячейку.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from core.search import Candidate, pick_avatar
from core.supervisor import WatchdogPolicy
from core.ytdlp_args import DownloadSettings
from runner.process import run_watched

#: Перепись канала ради одной картинки — дело не срочное, но и не вечное.
AVATAR_WATCHDOG = WatchdogPolicy(silence_limit=45.0, total_limit=180.0)

#: Больше этого картинка быть не должна: аватар YouTube — сотня-другая
#: килобайт, а всё крупное означает, что мы скачиваем не то.
MAX_BYTES = 4 * 1024 * 1024


def cache_path(cache_dir: Path, channel_id: str) -> Path:
    return cache_dir / f"{channel_id}.img"


def fetch_avatar_url(
    candidate: Candidate,
    settings: DownloadSettings,
    *,
    ytdlp: tuple[str, ...] = ("yt-dlp",),
) -> str:
    """Узнать адрес логотипа канала.

    Берём через `-J`: обычный `--print %(playlist_thumbnails...)s` на живом
    канале вернул NA, а в JSON картинки лежат все девять — проверено.
    """
    args: list[str] = []
    if settings.cookies_file:
        args += ["--cookies", settings.cookies_file]
    elif settings.cookies_browser:
        args += ["--cookies-from-browser", settings.cookies_browser]
    args += [
        "--js-runtimes", "node",
        "--extractor-args", "youtubetab:skip=authcheck",
        "--flat-playlist", "--playlist-items", "1", "-J",
        "--no-warnings",
        candidate.url,
    ]

    outcome = run_watched([*ytdlp, *args], AVATAR_WATCHDOG)
    try:
        данные = json.loads(outcome.text[outcome.text.index("{"):])
    except (ValueError, json.JSONDecodeError):
        return ""
    return pick_avatar(данные.get("thumbnails") or [])


def ensure_avatar(cache_dir: Path, channel_id: str, url: str) -> Path | None:
    """Положить логотип в кэш и вернуть путь. `None` — не вышло, и это не беда.

    Уже лежащий файл не перекачиваем: аватары не меняются месяцами.
    """
    if not channel_id or not url:
        return None

    путь = cache_path(cache_dir, channel_id)
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


def cached_avatar(cache_dir: Path, channel_id: str) -> Path | None:
    """Логотип, если он уже скачан. В сеть не ходим — зовётся из отрисовки."""
    путь = cache_path(cache_dir, channel_id)
    try:
        return путь if путь.exists() and путь.stat().st_size > 0 else None
    except OSError:
        return None
