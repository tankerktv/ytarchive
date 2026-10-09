"""Описания для медиасерверов: файлы .nfo рядом с роликами.

Jellyfin, Kodi и Plex показывают папку с роликами как сериал, если рядом
лежат описания: канал становится сериалом, год — сезоном, ролик — серией.
Без них сервер видит шестьсот файлов с датой в названии и пытается угадать,
что это за кино.

Здесь только сборка текста. Пишет файлы обёртка, и только те, которых нет:
описание, поправленное человеком, перезаписывать нельзя.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from core.library import Item

ШАПКА = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'


def nfo_name(video_name: str) -> str:
    """Имя файла описания: то же, что у ролика, с расширением .nfo."""
    основа, _точка, _расширение = video_name.rpartition(".")
    return f"{основа or video_name}.nfo"


def episode_numbers(items: list[Item]) -> dict[str, int]:
    """Номер серии каждому ролику канала.

    Номер — месяц, день и порядковый номер в этот день: 11 апреля, второй
    ролик → 4111. Так серии внутри сезона-года идут по дате, а два ролика
    одного дня не получают один номер — сервер склеил бы их в одну серию.

    Порядок внутри дня — по идентификатору: он произвольный, но устойчивый.
    Возьми мы порядок файлов на диске, номера менялись бы от прогона к прогону.
    """
    по_дням: dict[str, list[Item]] = {}
    for запись in items:
        по_дням.setdefault(запись.date, []).append(запись)
    номера = {}
    for дата, записи in по_дням.items():
        месяц_день = int(дата[4:8]) if len(дата) == 8 else 0
        for порядок, запись in enumerate(sorted(записи, key=lambda з: з.video_id)):
            номера[запись.video_id] = месяц_день * 10 + порядок
    return номера


def episode_nfo(item: Item, episode: int, plot: str = "") -> str:
    """Описание одного ролика как серии."""
    год = item.date[:4] if len(item.date) == 8 else "0"
    строки = [
        "<episodedetails>",
        f"  <title>{escape(item.title)}</title>",
        f"  <showtitle>{escape(item.channel)}</showtitle>",
        f"  <season>{int(год)}</season>",
        f"  <episode>{episode}</episode>",
    ]
    if len(item.date) == 8:
        строки.append(f"  <aired>{item.date_text}</aired>")
    if plot:
        строки.append(f"  <plot>{escape(plot)}</plot>")
    строки += [
        f"  <studio>{escape(item.channel)}</studio>",
        f'  <uniqueid type="youtube" default="true">{item.video_id}</uniqueid>',
        "</episodedetails>",
    ]
    return ШАПКА + "\n".join(строки) + "\n"


def show_nfo(channel: str) -> str:
    """Описание канала как сериала — файл `tvshow.nfo` в его папке."""
    return (
        ШАПКА
        + "<tvshow>\n"
        + f"  <title>{escape(channel)}</title>\n"
        + f"  <studio>{escape(channel)}</studio>\n"
        + "</tvshow>\n"
    )


def missing_nfo(items: list[Item], existing: frozenset[str]) -> list[Item]:
    """Ролики, у которых описания ещё нет.

    `existing` — пути уже лежащих .nfo относительно папки архива. Сравнение
    по пути, а не по идентификатору: описание лежит рядом с файлом, и у
    ролика в двух папках их должно быть два.
    """
    return [запись for запись in items if nfo_name(запись.path) not in existing]
