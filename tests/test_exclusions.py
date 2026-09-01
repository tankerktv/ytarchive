"""Проверки списка исключений.

Главное свойство: исключение обратимо. Снял галочку — ролик снова качается.
Если перепутать исключения со скачанным, обратимость пропадёт молча:
ролик будет числиться скачанным, а на диске его нет.
"""

import pytest

from core.archive import parse_archive
from core.exclusions import (
    Exclusions,
    apply_to,
    format_exclusions,
    parse_exclusions,
    toggle,
)


def test_пустой_список_это_не_ошибка():
    # По умолчанию не исключено ничего — берутся все ролики.
    итог = parse_exclusions("")
    assert len(итог) == 0
    assert итог.unreadable == ()


def test_обычный_разбор():
    итог = parse_exclusions("rbYUHA9ZOg8\naRbfazQ_Cns\n")
    assert итог.video_ids == {"rbYUHA9ZOg8", "aRbfazQ_Cns"}


def test_комментарии_и_пустые_строки_пропускаются():
    итог = parse_exclusions("# заметка\n\nrbYUHA9ZOg8\n\n")
    assert len(итог) == 1
    assert итог.unreadable == ()


def test_непонятая_строка_не_теряется():
    """Молча потерянное исключение означает, что ролик вдруг начнёт
    качаться, и человек не поймёт почему.
    """
    итог = parse_exclusions("rbYUHA9ZOg8\nчто это такое\n")
    assert итог.video_ids == {"rbYUHA9ZOg8"}
    assert итог.unreadable == ("что это такое",)


@pytest.mark.parametrize("плохой", ["короткий", "rbYUHA9ZOg8x", "rbYUHA9ZO!8"])
def test_испорченный_идентификатор_не_принимается(плохой):
    assert len(parse_exclusions(плохой + "\n")) == 0


# --- отметить и снять -------------------------------------------------------


def test_отметить_добавляет():
    стало = toggle(Exclusions(), "rbYUHA9ZOg8", excluded=True)
    assert "rbYUHA9ZOg8" in стало


def test_снять_убирает():
    было = Exclusions(video_ids=frozenset({"rbYUHA9ZOg8"}))
    assert "rbYUHA9ZOg8" not in toggle(было, "rbYUHA9ZOg8", excluded=False)


def test_повторная_отметка_ничего_не_ломает():
    было = Exclusions(video_ids=frozenset({"rbYUHA9ZOg8"}))
    assert len(toggle(было, "rbYUHA9ZOg8", excluded=True)) == 1


def test_снятие_отсутствующего_безопасно():
    assert len(toggle(Exclusions(), "rbYUHA9ZOg8", excluded=False)) == 0


def test_отказ_на_мусоре_вместо_идентификатора():
    with pytest.raises(ValueError):
        toggle(Exclusions(), "не идентификатор", excluded=True)


# --- запись и чтение --------------------------------------------------------


def test_запись_и_чтение_обратимы():
    было = {"rbYUHA9ZOg8", "aRbfazQ_Cns"}
    assert parse_exclusions(format_exclusions(было)).video_ids == было


def test_пустой_список_записывается_без_поломки():
    assert len(parse_exclusions(format_exclusions(set()))) == 0


def test_порядок_записи_устойчив():
    # Иначе каждая правка перемешивала бы файл и diff читать было бы нельзя.
    первый = format_exclusions({"bbbbbbbbbbb", "aaaaaaaaaaa"})
    второй = format_exclusions({"aaaaaaaaaaa", "bbbbbbbbbbb"})
    assert первый == второй


# --- применение к очереди ---------------------------------------------------


def test_исключённые_выпадают_из_очереди():
    перепись = ["aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"]
    исключения = Exclusions(video_ids=frozenset({"bbbbbbbbbbb"}))
    assert apply_to(перепись, исключения) == ["aaaaaaaaaaa", "ccccccccccc"]


def test_порядок_остальных_сохраняется():
    # Порядок — это очередь обхода, и трогать его исключения не должны.
    перепись = ["ccccccccccc", "aaaaaaaaaaa", "bbbbbbbbbbb"]
    итог = apply_to(перепись, Exclusions(video_ids=frozenset({"aaaaaaaaaaa"})))
    assert итог == ["ccccccccccc", "bbbbbbbbbbb"]


def test_без_исключений_очередь_не_меняется():
    перепись = ["aaaaaaaaaaa", "bbbbbbbbbbb"]
    assert apply_to(перепись, Exclusions()) == перепись


def test_исключения_и_скачанное_живут_врозь():
    """Соблазн держать их в одном файле велик — yt-dlp пропустил бы и то
    и другое. Но тогда снятие галочки уже ничего не вернёт: ролик будет
    числиться скачанным, хотя на диске его нет.
    """
    архив = parse_archive("youtube rbYUHA9ZOg8\n")
    исключения = parse_exclusions("aRbfazQ_Cns\n")

    assert "rbYUHA9ZOg8" in архив
    assert "rbYUHA9ZOg8" not in исключения
    assert "aRbfazQ_Cns" in исключения
    assert "aRbfazQ_Cns" not in архив

    # И снятие исключения возвращает ролик в очередь — в отличие от архива.
    снято = toggle(исключения, "aRbfazQ_Cns", excluded=False)
    assert apply_to(["aRbfazQ_Cns"], снято) == ["aRbfazQ_Cns"]
