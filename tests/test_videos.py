"""Проверки разбора переписи канала с названиями.

Названия приходят от людей и содержат что угодно — табуляции, кавычки,
вертикальные черты. Разбор, который на них спотыкается, теряет ролик молча:
он просто не скачается, и никто этого не заметит.
"""

from core.videos import Listing, Video, parse_listing, search

ПЕРЕПИСЬ = (
    "rbYUHA9ZOg8\t10171\tС домом на колёсах по каньонам США.\n"
    "aRbfazQ_Cns\t2796\tКак пиратили 8 и 16 бит | Dendy и Super Nintendo\n"
    "QY_rRuA0E04\t1686\tRTX 5060Ti 16Gb в 2025г. и вот почему!\n"
)


def test_обычный_разбор():
    итог = parse_listing(ПЕРЕПИСЬ)
    assert len(итог) == 3
    assert итог.unreadable == ()
    assert итог.videos[0].video_id == "rbYUHA9ZOg8"
    assert итог.videos[0].seconds == 10171.0


def test_название_с_вертикальной_чертой_не_рвётся():
    # В названиях каналов и роликов черта встречается постоянно.
    итог = parse_listing(ПЕРЕПИСЬ)
    assert "Dendy и Super Nintendo" in итог.videos[1].title


def test_табуляция_внутри_названия_остаётся_в_названии():
    """Название идёт последним намеренно: всё лишнее достаётся ему,
    а не ломает разбор.
    """
    итог = parse_listing("rbYUHA9ZOg8\t600\tчасть\tвторая\n")
    assert итог.unreadable == ()
    assert итог.videos[0].title == "часть\tвторая"


def test_без_длительности_ролик_не_теряется():
    # NA бывает у трансляций и премьер — это законно.
    итог = parse_listing("rbYUHA9ZOg8\tNA\tПрямой эфир\n")
    assert len(итог) == 1
    assert итог.videos[0].seconds == 0.0


def test_без_названия_показываем_идентификатор():
    # Пустая строка в списке выглядела бы как поломка окна.
    итог = parse_listing("rbYUHA9ZOg8\t600\t\n")
    assert итог.videos[0].title == "rbYUHA9ZOg8"


def test_непонятая_строка_не_теряется():
    итог = parse_listing("rbYUHA9ZOg8\t600\tхороший\nсовсем не то\n")
    assert len(итог) == 1
    assert итог.unreadable == ("совсем не то",)


def test_пустая_перепись():
    итог = parse_listing("")
    assert len(итог) == 0
    assert итог.unreadable == ()


def test_суммарная_длительность():
    assert parse_listing(ПЕРЕПИСЬ).total_seconds == 10171.0 + 2796.0 + 1686.0


# --- показ человеку ---------------------------------------------------------


def test_длительность_с_часами():
    assert Video("rbYUHA9ZOg8", "x", 10171).duration_text() == "2:49:31"


def test_длительность_без_часов():
    assert Video("rbYUHA9ZOg8", "x", 2796).duration_text() == "46:36"


def test_отсутствующая_длительность_показывается_прочерком():
    # Ноль выглядел бы как «ролик нулевой длины», а это разные вещи.
    assert Video("rbYUHA9ZOg8", "x", 0).duration_text() == "—"


def test_адрес_ролика_и_миниатюры():
    """Адрес миниатюры собирается по идентификатору, без обращения к сети:
    у YouTube он предсказуем, и лишний запрос ради него не нужен.
    """
    видео = Video("rbYUHA9ZOg8", "x")
    assert видео.url.endswith("watch?v=rbYUHA9ZOg8")
    assert "rbYUHA9ZOg8" in видео.thumbnail_url


# --- поиск по списку --------------------------------------------------------


def test_поиск_не_различает_регистр():
    # Человек ищет «dendy», а не «Dendy».
    итог = search(parse_listing(ПЕРЕПИСЬ).videos, "dendy")
    assert len(итог) == 1
    assert "Dendy" in итог[0].title


def test_поиск_по_куску_слова():
    итог = search(parse_listing(ПЕРЕПИСЬ).videos, "каньон")
    assert len(итог) == 1


def test_пустой_запрос_показывает_всё():
    """«Поиск ничего не ищет» — это не «ничего не нашлось».
    Спрятать весь список при пустом поле значит напугать на ровном месте.
    """
    видео = parse_listing(ПЕРЕПИСЬ).videos
    assert len(search(видео, "")) == 3
    assert len(search(видео, "   ")) == 3


def test_ничего_не_нашлось():
    assert search(parse_listing(ПЕРЕПИСЬ).videos, "такого нет") == []


def test_поиск_сохраняет_порядок():
    # Порядок переписи — от новых к старым, и поиск его менять не должен.
    видео = parse_listing(ПЕРЕПИСЬ).videos
    итог = search(видео, "о")
    assert [v.video_id for v in итог] == [v.video_id for v in видео if "о" in v.title.casefold()]
