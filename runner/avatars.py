"""Логотипы каналов: узнать адрес, скачать, положить в кэш.

Само хранение картинок вынесено в `runner.images`: миниатюрам роликов нужно
ровно то же самое, и держать два одинаковых кэша незачем. Здесь остаётся то,
что свойственно именно логотипу, — как узнать его адрес.
"""

from __future__ import annotations

import json

from core.search import Candidate, pick_avatar
from core.supervisor import WatchdogPolicy
from core.ytdlp_args import DownloadSettings
from runner.images import cache_path, cached_image, ensure_image
from runner.process import run_watched

#: Перепись канала ради одной картинки — дело не срочное, но и не вечное.
AVATAR_WATCHDOG = WatchdogPolicy(silence_limit=45.0, total_limit=180.0)

#: Логотип — та же картинка в кэше. Имена оставлены прежними: по месту вызова
#: «положить логотип» читается лучше, чем «положить картинку».
ensure_avatar = ensure_image
cached_avatar = cached_image


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
