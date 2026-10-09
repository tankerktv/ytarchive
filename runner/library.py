"""Библиотека на диске: обход папок, отметки о пропавших, описания.

Решения — в `core.library`, `core.gone` и `core.nfo`. Здесь только то, что
трогает диск и зовёт ffprobe.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from core.gone import Verdict, all_gone, from_text, judge, to_text, update
from core.library import Item, build, description_from_tags
from core.nfo import episode_nfo, episode_numbers, missing_nfo, nfo_name, show_nfo
from core.verify import id_of

#: Отметки о пропавших с YouTube роликах. Рядом с учётом скачанного.
GONE_FILE = "gone.json"

#: Сколько ждём ffprobe на один файл. Он читает только заголовок и отвечает
#: за доли секунды; дольше — значит, диск уснул или файл битый.
FFPROBE_TIMEOUT = 30


def channel_folders(base: Path) -> list[Path]:
    """Папки с роликами: всё в папке архива, кроме служебного."""
    try:
        return sorted(
            папка for папка in base.iterdir()
            if папка.is_dir() and not папка.name.startswith(("_", "."))
        )
    except OSError:
        return []


def scan(base: Path) -> list[tuple[str, str, int]]:
    """Все файлы папок каналов: (канал, имя, размер)."""
    итог = []
    for папка in channel_folders(base):
        try:
            содержимое = list(папка.iterdir())
        except OSError:
            continue
        for путь in содержимое:
            try:
                if путь.is_file():
                    итог.append((папка.name, путь.name, путь.stat().st_size))
            except OSError:
                continue
    return итог


def ids_on_disk(folder: Path) -> frozenset[str]:
    """Идентификаторы целых роликов в папке канала."""
    try:
        имена = [путь.name for путь in folder.iterdir()]
    except OSError:
        return frozenset()
    return frozenset(id_of(имя) for имя in имена) - {""}


def read_marks(tools_dir: Path) -> dict[str, frozenset[str]]:
    try:
        return from_text((tools_dir / GONE_FILE).read_text(encoding="utf-8"))
    except OSError:
        return {}


def mark_gone(
    tools_dir: Path, channel: str, on_disk: frozenset[str], listed: frozenset[str]
) -> frozenset[str]:
    """Сравнить диск с переписью и записать отметки. Возвращает пропавшее впервые.

    Не записалось — не беда: отметки восстановятся следующим проходом,
    а выкачка важнее.
    """
    приговор: Verdict = judge(on_disk, listed)
    if not приговор.reliable:
        return frozenset()
    прежние = read_marks(tools_dir)
    новые, впервые = update(прежние, channel, приговор)
    if новые != прежние:
        try:
            (tools_dir / GONE_FILE).write_text(to_text(новые), encoding="utf-8", newline="\n")
        except OSError:
            return frozenset()
    return впервые


def library(base: Path, tools_dir: Path) -> list[Item]:
    return build(scan(base), all_gone(read_marks(tools_dir)))


def read_description(path: Path) -> str:
    """Описание ролика из меток файла. Пусто — нет описания или нет ffprobe."""
    доводы = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
    try:
        ответ = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format_tags", "-of", "json", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL, timeout=FFPROBE_TIMEOUT, **доводы,
        )
        метки = json.loads(ответ.stdout or "{}").get("format", {}).get("tags", {})
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return ""
    return description_from_tags(метки) if isinstance(метки, dict) else ""


def nfo_todo(base: Path) -> tuple[list[Item], list[str]]:
    """Чему не хватает описаний: ролики без .nfo и каналы без tvshow.nfo."""
    файлы = scan(base)
    записи = build(файлы)
    есть = frozenset(f"{канал}/{имя}" for канал, имя, _размер in файлы if имя.lower().endswith(".nfo"))
    каналы = sorted({з.channel for з in записи if f"{з.channel}/tvshow.nfo" not in есть})
    return missing_nfo(записи, есть), каналы


def write_nfo(
    base: Path,
    on_progress: Callable[[int, int], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> tuple[int, int]:
    """Дописать недостающие описания. Возвращает (записано, не вышло).

    Существующие .nfo не трогаются никогда: описание могло быть поправлено
    человеком или самим медиасервером.
    """
    роликам, каналам = nfo_todo(base)
    записано = не_вышло = 0

    for канал in каналам:
        try:
            (base / канал / "tvshow.nfo").write_text(show_nfo(канал), encoding="utf-8", newline="\n")
            записано += 1
        except OSError:
            не_вышло += 1

    # Номера серий считаются по всем роликам канала, а не только по новым:
    # иначе второй ролик того же дня получил бы номер первого.
    все = build(scan(base))
    номера: dict[str, dict[str, int]] = {}
    for канал in {з.channel for з in все}:
        номера[канал] = episode_numbers([з for з in все if з.channel == канал])

    for порядок, запись in enumerate(роликам, start=1):
        if should_stop is not None and should_stop():
            break
        if on_progress is not None:
            on_progress(порядок, len(роликам))
        путь = base / запись.path
        текст = episode_nfo(
            запись, номера.get(запись.channel, {}).get(запись.video_id, 0), read_description(путь)
        )
        try:
            (base / nfo_name(запись.path)).write_text(текст, encoding="utf-8", newline="\n")
            записано += 1
        except OSError:
            не_вышло += 1
    return записано, не_вышло
