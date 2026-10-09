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
#: Дата в переписи: восемь цифр или NA, когда yt-dlp её не знает.
_ДАТА_ИЛИ_ПУСТО = re.compile(r"^(\d{8}|NA|None)$")


@dataclass(frozen=True)
class Video:
    video_id: str
    title: str
    seconds: float = 0.0
    #: Дата выхода, ГГГГММДД. Примерная и не у всех роликов есть: перепись
    #: берёт её из надписи «3 года назад». Пусто — неизвестна.
    upload_date: str = ""

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

        части = очищенная.split(SEPARATOR, 3)
        if len(части) < 2 or not VIDEO_ID.match(части[0].strip()):
            плохие.append(очищенная.strip()[:160])
            continue

        # Третьим полем идёт дата — с тех пор, как появились правила отбора.
        # Строку без неё тоже понимаем: тогда всё после длительности —
        # название, как и было. Иначе табуляция в названии старого образца
        # отрезала бы от него начало.
        дата = ""
        if len(части) == 4 and _ДАТА_ИЛИ_ПУСТО.match(части[2].strip()):
            дата = части[2].strip() if части[2].strip().isdigit() else ""
            части = [части[0], части[1], части[3]]
        elif len(части) == 4:
            части = [части[0], части[1], SEPARATOR.join(части[2:])]

        try:
            секунды = float(части[1])
        except ValueError:
            секунды = 0.0  # NA у трансляций — законно, это не повод терять ролик

        название = части[2].strip() if len(части) > 2 else ""
        видео.append(
            Video(
                video_id=части[0].strip(),
                title=название or части[0].strip(),
                seconds=секунды,
                upload_date=дата,
            )
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


# --- дата ролика ---

#: Имя скачанного файла начинается с точной даты выхода и несёт идентификатор:
#: `2024-04-11 - Название [oxd5IAl-o3Q].mkv`. Шаблон имени задаём мы сами.
_ДАТА_В_ИМЕНИ = re.compile(r"^(\d{4})-(\d{2})-(\d{2}) - .*\[([A-Za-z0-9_-]{11})\]\.[A-Za-z0-9]+$")

#: Чем отмечается примерная дата. Знак, а не слово: переводить нечего.
ПРИМЕРНО = "≈ "


def date_from_filename(name: str) -> tuple[str, str] | None:
    """Идентификатор и точная дата (ГГГГММДД) из имени скачанного файла."""
    найдено = _ДАТА_В_ИМЕНИ.match(name)
    if not найдено:
        return None
    год, месяц, день, ролик = найдено.groups()
    return ролик, f"{год}{месяц}{день}"


def _дней_между(раньше: str, позже: str) -> int | None:
    from datetime import date

    try:
        а = date(int(раньше[:4]), int(раньше[4:6]), int(раньше[6:8]))
        б = date(int(позже[:4]), int(позже[4:6]), int(позже[6:8]))
    except ValueError:
        return None
    return (б - а).days


def date_text(upload_date: str, *, exact: bool, today: str = "") -> str:
    """Дата ролика для показа.

    Точная дата есть только у скачанного ролика — она стоит в имени файла.
    У остальных дата взята из переписи, а там YouTube пишет «3 года назад»:
    показать такую с точностью до дня значит соврать. Поэтому примерная дата
    показывается ровно с той точностью, какую имеет: свежая — днём, в пределах
    года — месяцем, старше — годом, и всегда со знаком «≈».
    """
    if len(upload_date) != 8 or not upload_date.isdigit():
        return "—"
    день = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    if exact:
        return день
    возраст = _дней_между(upload_date, today) if today else None
    if возраст is None:
        return ПРИМЕРНО + день[:4]
    if возраст <= 31:
        return ПРИМЕРНО + день
    if возраст <= 365:
        return ПРИМЕРНО + день[:7]
    return ПРИМЕРНО + день[:4]


_ЧИСТОЕ_НАЗВАНИЕ = re.compile(
    r"^(?:\d{4}-\d{2}-\d{2} - )?(?P<название>.+?)(?: \[[A-Za-z0-9_-]{11}\])?(?:\.f\d+)?\.[A-Za-z0-9]+$"
)


def title_from_filename(name: str) -> str:
    """Название ролика из имени качаемого файла.

    `2024-04-11 - BMW E87 [oxd5IAl-o3Q].f299.mp4` → `BMW E87`. Дата,
    идентификатор и номер формата нужны программе, а человеку мешают
    прочесть, что именно сейчас качается. Не разобралось — имя как есть:
    странное имя лучше пустого места.
    """
    найдено = _ЧИСТОЕ_НАЗВАНИЕ.match(name)
    return найдено.group("название") if найдено else name
