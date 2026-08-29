"""Очередь работ: что качать, в каком порядке и хватит ли места.

Перепись канала приходит в порядке выдачи YouTube — **новые первыми**.
Этот порядок значим: на нём держится решение о быстром проходе (см. ниже),
поэтому переворачивать его нельзя.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.archive import ArchiveContents

#: Измеренные суммарные битрейты (видео + звук) при потолке 1080p с предпочтением AV1.
#: 1,4 Мбит/с — ролик «Уютного подвальчика» на 46,6 мин и 0,49 ГБ.
#: 3,7 Мбит/с — ролик SoyuzUS на 169 мин и 4,7 ГБ (съёмка в высоком качестве).
#: Оценка объёма без этих чисел была бы гаданием, поэтому они здесь, а не в интерфейсе.
BITRATE_LOW_MBPS = 1.4
BITRATE_HIGH_MBPS = 3.7


@dataclass(frozen=True)
class ChannelListing:
    """Перепись одного канала: идентификаторы в порядке выдачи, новые первыми."""

    channel: str
    video_ids: tuple[str, ...]


@dataclass(frozen=True)
class WorkItem:
    channel: str
    video_id: str


def build_queue(listings: list[ChannelListing], archive: ArchiveContents) -> list[WorkItem]:
    """Собрать очередь: что из переписи ещё не скачано.

    Каналы обходятся в том порядке, в каком их перечислил человек, а ролики —
    в порядке выдачи. Предсказуемость важнее оптимальности: прерванный проход
    должен продолжаться с того же места, иначе разобраться в происходящем нельзя.

    Повторы схлопываются по всей очереди, а не внутри канала: один ролик может
    попасть в перепись двух каналов, и качать его дважды незачем.
    """
    queue: list[WorkItem] = []
    seen: set[str] = set()

    for listing in listings:
        for video_id in listing.video_ids:
            if video_id in archive.video_ids or video_id in seen:
                continue
            seen.add(video_id)
            queue.append(WorkItem(channel=listing.channel, video_id=video_id))

    return queue


def is_incremental_safe(video_ids: tuple[str, ...], archive: ArchiveContents) -> bool:
    """Можно ли обойтись быстрым проходом — остановкой на первом знакомом ролике.

    Быстрый проход (`--break-on-existing` у yt-dlp) перечисляет канал, пока не
    встретит уже скачанное, и обрывается. Ночной проход тогда занимает секунды,
    а не минуты — но **только если пропущено ровно начало списка**.

    Условие: недостающие идентификаторы образуют непрерывное начало переписи.
    Если дальше по списку есть дыра — упавший когда-то ролик, ролик, снятый
    с приватности, — быстрый проход её не заметит уже никогда.

    Поэтому включать его на недособранном архиве нельзя: он оборвётся
    на первом же скачанном и остальное не заберёт.
    """
    if not video_ids:
        return True

    # Ищем границу: сколько первых роликов отсутствует в архиве.
    boundary = 0
    while boundary < len(video_ids) and video_ids[boundary] not in archive.video_ids:
        boundary += 1

    # Всё, что после границы, обязано быть скачано — иначе дыра.
    return all(video_id in archive.video_ids for video_id in video_ids[boundary:])


def estimate_bytes(total_seconds: float, mbps: float) -> int:
    """Сколько займёт материал такой длительности при таком битрейте.

    Мегабит в секунду, не мегабайт: битрейт принято мерить в битах, и
    перепутать эти две единицы — ошибиться в восемь раз.
    """
    if total_seconds < 0:
        raise ValueError("длительность не может быть отрицательной")
    if mbps <= 0:
        raise ValueError("битрейт должен быть положительным")
    return int(total_seconds * mbps * 1_000_000 / 8)


def estimate_range(total_seconds: float) -> tuple[int, int]:
    """Вилка объёма по измеренным крайним битрейтам."""
    return (
        estimate_bytes(total_seconds, BITRATE_LOW_MBPS),
        estimate_bytes(total_seconds, BITRATE_HIGH_MBPS),
    )


def enough_space(needed: int, free: int, reserve: int = 20 * 1024**3) -> bool:
    """Хватит ли места с запасом.

    Запас нужен не из осторожности вообще, а потому что во время слияния
    видео и звука на диске одновременно лежат исходные потоки и результат.
    Забить диск под ноль — значит уронить не только выкачку, но и всё
    остальное, что на нём живёт.
    """
    if needed < 0 or free < 0 or reserve < 0:
        raise ValueError("объёмы не могут быть отрицательными")
    return free - reserve >= needed
