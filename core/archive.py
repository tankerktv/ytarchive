"""Учёт уже скачанного.

Формат файла задан не нами, а yt-dlp (`--download-archive`): по строке на ролик,
`<экстрактор> <идентификатор>`. Мы его только читаем и дописываем.

Главное свойство, ради которого всё это существует: **упавший ролик в архив
не попадает**. Благодаря этому следующий проход берёт его снова, и потери
не накапливаются — проверено на 964 сбоях, из которых забраны все.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: Ключ хранения. НЕ ПЕРЕИМЕНОВЫВАТЬ и не «нормализовать»: строку читает и пишет
#: сам yt-dlp. Смена значения молча обнулит учёт — программа не упадёт, просто
#: сочтёт весь архив нескачанным и полезет качать заново тысячу роликов.
EXTRACTOR_KEY = "youtube"

#: Идентификатор ролика YouTube — ровно 11 символов. Проверка нужна не для
#: красоты: перепись однажды вернула мусор вместо списка, и без этой проверки
#: он молча уехал бы в очередь.
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


@dataclass(frozen=True)
class ArchiveContents:
    """Разобранный архив.

    `unreadable` существует, чтобы ничего не выбрасывалось молча: строки,
    которые мы не поняли, должны попасть в журнал, а не исчезнуть.
    """

    video_ids: frozenset[str] = frozenset()
    unreadable: tuple[str, ...] = ()

    def __contains__(self, video_id: str) -> bool:
        return video_id in self.video_ids

    def __len__(self) -> int:
        return len(self.video_ids)


def parse_archive(text: str) -> ArchiveContents:
    """Разобрать содержимое файла архива.

    Пустой архив — это законный результат (ничего ещё не скачано), а не ошибка.
    Отличать «пусто» от «не смог прочитать» обязан вызывающий: файла нет — это
    его забота, а не наша.
    """
    ids: set[str] = set()
    bad: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        parts = stripped.split()
        # Ждём ровно две части. Одна — обрезанная строка, три и больше —
        # неизвестный формат; и то и другое лучше показать, чем проглотить.
        if len(parts) != 2 or parts[0] != EXTRACTOR_KEY or not VIDEO_ID.match(parts[1]):
            bad.append(stripped)
            continue

        ids.add(parts[1])

    return ArchiveContents(video_ids=frozenset(ids), unreadable=tuple(bad))


def format_line(video_id: str) -> str:
    """Собрать строку для дописывания в архив."""
    if not VIDEO_ID.match(video_id):
        raise ValueError(f"не похоже на идентификатор ролика: {video_id!r}")
    return f"{EXTRACTOR_KEY} {video_id}"


def missing(known_ids: list[str], archive: ArchiveContents) -> list[str]:
    """Что из переписи ещё не скачано, в исходном порядке.

    Порядок сохраняется намеренно: очередь должна быть предсказуемой, чтобы
    прерванный проход продолжался с того же места, а не с произвольного.
    Повторы в переписи схлопываются — канал иногда отдаёт ролик дважды.
    """
    seen: set[str] = set()
    result: list[str] = []
    for video_id in known_ids:
        if video_id in archive.video_ids or video_id in seen:
            continue
        seen.add(video_id)
        result.append(video_id)
    return result
