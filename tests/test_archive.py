"""Проверки учёта скачанного.

Половина проверок — на отказ: что функция НЕ делает при непонятных данных.
Цена ошибки здесь несимметрична. Не распознали строку — увидим её в журнале
и починим. Распознали неверно — сочли ролик скачанным, и он не заберётся
уже никогда, причём молча.
"""

from core.archive import ArchiveContents, format_line, missing, parse_archive

import pytest


def test_пустой_архив_это_не_ошибка():
    # Ничего ещё не скачано — законное состояние при первом запуске.
    result = parse_archive("")
    assert len(result) == 0
    assert result.unreadable == ()


def test_обычный_разбор():
    result = parse_archive("youtube rbYUHA9ZOg8\nyoutube aRbfazQ_Cns\n")
    assert result.video_ids == {"rbYUHA9ZOg8", "aRbfazQ_Cns"}
    assert result.unreadable == ()


def test_пустые_строки_пропускаются_молча():
    # Пустая строка — не мусор, а обычное дело в конце файла.
    result = parse_archive("\n\nyoutube rbYUHA9ZOg8\n\n")
    assert len(result) == 1
    assert result.unreadable == ()


def test_непонятная_строка_не_теряется():
    # Ничего не выбрасывается молча: строку вернём, чтобы она попала в журнал.
    result = parse_archive("youtube rbYUHA9ZOg8\nчто это вообще\n")
    assert result.video_ids == {"rbYUHA9ZOg8"}
    assert result.unreadable == ("что это вообще",)


def test_чужой_экстрактор_не_считается_скачанным():
    # Тот же идентификатор от другого источника — другой ролик.
    result = parse_archive("vimeo rbYUHA9ZOg8\n")
    assert len(result) == 0
    assert len(result.unreadable) == 1


@pytest.mark.parametrize(
    "bad",
    [
        "youtube короткий",
        "youtube rbYUHA9ZOg8x",  # 12 символов
        "youtube rbYUHA9ZOg",  # 10 символов
        "youtube rbYUHA9ZO!8",  # недопустимый символ
        "youtube",  # обрезанная строка
        "youtube rbYUHA9ZOg8 лишнее",
    ],
)
def test_отказ_на_испорченном_идентификаторе(bad):
    result = parse_archive(bad + "\n")
    assert len(result) == 0, f"строка {bad!r} принята, а не должна была"
    assert result.unreadable == (bad,)


def test_format_line_отказывается_писать_мусор():
    # Лучше упасть здесь, чем испортить файл, который потом читает yt-dlp.
    with pytest.raises(ValueError):
        format_line("не идентификатор")


def test_format_line_и_разбор_совместимы():
    line = format_line("rbYUHA9ZOg8")
    assert parse_archive(line).video_ids == {"rbYUHA9ZOg8"}


def test_missing_сохраняет_порядок():
    # Очередь должна быть предсказуемой: прерванный проход продолжается
    # с того же места, а не с произвольного.
    known = ["aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"]
    archive = ArchiveContents(video_ids=frozenset({"bbbbbbbbbbb"}))
    assert missing(known, archive) == ["aaaaaaaaaaa", "ccccccccccc"]


def test_missing_схлопывает_повторы_переписи():
    # Канал иногда отдаёт один и тот же ролик дважды — качать его дважды незачем.
    known = ["aaaaaaaaaaa", "aaaaaaaaaaa"]
    assert missing(known, ArchiveContents()) == ["aaaaaaaaaaa"]


def test_настоящий_случай_2026_08_27_упавший_ролик_берётся_снова():
    """За неделю выкачки 964 ролика упали с «Sign in to confirm you're not a bot».

    Ни один не потерялся: упавший в архив не записывается, поэтому следующий
    проход берёт его заново. Это свойство и проверяем — на нём держится
    вся устойчивость к перемежающимся сбоям сети и блокировкам DNS.
    """
    перепись = ["rbYUHA9ZOg8", "G02jtMoGy2g", "IMyAvT64D8g"]
    # Скачался только первый, два других упали и в архив не попали.
    archive = parse_archive("youtube rbYUHA9ZOg8\n")

    assert missing(перепись, archive) == ["G02jtMoGy2g", "IMyAvT64D8g"]


def test_настоящий_случай_2026_08_29_обрезанный_архив_не_теряет_роликов():
    """Если файл архива обрежется на середине строки, недописанная строка
    не должна быть принята за скачанный ролик — иначе он не заберётся никогда.
    """
    archive = parse_archive("youtube rbYUHA9ZOg8\nyoutube aRbfaz")
    assert archive.video_ids == {"rbYUHA9ZOg8"}
    assert archive.unreadable == ("youtube aRbfaz",)
