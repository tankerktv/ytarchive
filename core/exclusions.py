"""Ролики, которые качать не надо.

По умолчанию берутся все — человек отмечает лишние, а не нужные. Так задумано:
архив собирается сам, и требовать отметить две тысячи роликов, чтобы получить
то же самое, было бы издевательством.

**Исключение — не то же самое, что скачанное.** Держать их в одном файле было бы
заманчиво (yt-dlp пропустил бы и те и другие), но тогда снятие галочки уже
ничего не вернуло бы: ролик числился бы скачанным. Поэтому файл отдельный.

Хранится по идентификатору ролика, без имени канала: идентификатор на YouTube
уникален, а имя канала человек может переименовать — и связь порвётся.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Идентификатор ролика — ровно 11 символов, как и в учёте скачанного.
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")

COMMENT_PREFIX = "#"

HEADER = (
    "# Ролики, которые качать не надо — по одному идентификатору в строке.\n"
    "# Это НЕ список скачанного: сняв строку отсюда, ролик снова заберут.\n"
    "# Правится из окна, но можно и руками.\n"
)


@dataclass(frozen=True)
class Exclusions:
    video_ids: frozenset[str] = frozenset()
    unreadable: tuple[str, ...] = ()

    def __contains__(self, video_id: str) -> bool:
        return video_id in self.video_ids

    def __len__(self) -> int:
        return len(self.video_ids)


def parse_exclusions(text: str) -> Exclusions:
    """Разобрать список исключений.

    Непонятая строка возвращается отдельно, а не отбрасывается: молча
    потерянное исключение означает, что ролик вдруг начнёт качаться,
    и человек не поймёт почему.
    """
    ids: set[str] = set()
    bad: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIX):
            continue
        if VIDEO_ID.match(stripped):
            ids.add(stripped)
        else:
            bad.append(stripped)

    return Exclusions(video_ids=frozenset(ids), unreadable=tuple(bad))


def format_exclusions(video_ids: set[str] | frozenset[str]) -> str:
    """Собрать текст файла. Порядок задаётся сортировкой — так правки
    в файле дают понятный diff, а не перемешанные строки."""
    строки = sorted(video_ids)
    return HEADER + "\n".join(строки) + ("\n" if строки else "")


def toggle(exclusions: Exclusions, video_id: str, excluded: bool) -> Exclusions:
    """Отметить или снять отметку с ролика.

    Снятая галочка означает «качать», то есть удаление из этого файла.
    """
    if not VIDEO_ID.match(video_id):
        raise ValueError(f"не похоже на идентификатор ролика: {video_id!r}")
    ids = set(exclusions.video_ids)
    if excluded:
        ids.add(video_id)
    else:
        ids.discard(video_id)
    return Exclusions(video_ids=frozenset(ids), unreadable=exclusions.unreadable)


def apply_to(video_ids: list[str], exclusions: Exclusions) -> list[str]:
    """Убрать исключённые, сохранив порядок остальных."""
    return [v for v in video_ids if v not in exclusions.video_ids]
