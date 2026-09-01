"""Ролики канала: разбор переписи с названиями.

Нужен в двух местах сразу — выкачке, чтобы знать, что качать, и окну выбора,
чтобы человек видел, с чего снимает галочку. По одному идентификатору
он этого не поймёт.

Формат строки задан нами же в `--print`: идентификатор, длительность,
название через табуляцию. Название идёт последним намеренно: в нём бывает
что угодно, включая табуляцию, и всё лишнее просто останется в названии,
а не сломает разбор.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
SEPARATOR = "\t"


@dataclass(frozen=True)
class Video:
    video_id: str
    title: str
    seconds: float = 0.0

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    @property
    def thumbnail_url(self) -> str:
        """Миниатюра. Адрес собирается по идентификатору, без обращения к сети —
        у YouTube он предсказуем, и лишний запрос ради него не нужен."""
        return f"https://i.ytimg.com/vi/{self.video_id}/mqdefault.jpg"

    def duration_text(self) -> str:
        if self.seconds <= 0:
            return "—"  # трансляции и премьеры: длительности ещё нет
        часы, остаток = divmod(int(self.seconds), 3600)
        минуты, секунды = divmod(остаток, 60)
        if часы:
            return f"{часы}:{минуты:02d}:{секунды:02d}"
        return f"{минуты}:{секунды:02d}"


@dataclass(frozen=True)
class Listing:
    videos: tuple[Video, ...] = ()
    unreadable: tuple[str, ...] = ()

    def __len__(self) -> int:
        return len(self.videos)

    @property
    def total_seconds(self) -> float:
        return sum(v.seconds for v in self.videos)


def parse_listing(text: str) -> Listing:
    """Разобрать перепись канала.

    Непонятая строка возвращается отдельно: молча пропав, ролик просто
    не скачается, и никто этого не заметит.
    """
    видео: list[Video] = []
    плохие: list[str] = []

    for строка in text.splitlines():
        очищенная = строка.rstrip("\n")
        if not очищенная.strip():
            continue

        части = очищенная.split(SEPARATOR, 2)
        if len(части) < 2 or not VIDEO_ID.match(части[0].strip()):
            плохие.append(очищенная.strip()[:160])
            continue

        try:
            секунды = float(части[1])
        except ValueError:
            секунды = 0.0  # NA у трансляций — законно, это не повод терять ролик

        название = части[2].strip() if len(части) > 2 else ""
        видео.append(
            Video(video_id=части[0].strip(), title=название or части[0].strip(), seconds=секунды)
        )

    return Listing(videos=tuple(видео), unreadable=tuple(плохие))


def search(videos: tuple[Video, ...] | list[Video], query: str) -> list[Video]:
    """Отобрать по подстроке в названии.

    Регистр не важен: человек ищет «дендy», а не «Дендy». Пустой запрос
    возвращает всё — это «поиск ничего не ищет», а не «ничего не нашлось».
    """
    запрос = query.strip().casefold()
    if not запрос:
        return list(videos)
    return [v for v in videos if запрос in v.title.casefold()]
