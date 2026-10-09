"""Проверки поиска канала.

Главное свойство: объём известен до добавления. Ошибка здесь стоит дорого —
на живом поиске «alex m» выдал канал на 2111 роликов и до 1,9 ТБ вперемешку
с нужным на 37. Добавить не тот значит занять терабайт не тем.
"""

import pytest

from core.search import Candidate, fits, parse_search_output, with_measurement

ВЫДАЧА = [
    "Alex M|UCZ0DJ1UBmS1sEjDBr2OABAw",
    "ALEX M techno|UCafxwwWt4VgDrug4s1OQIFA",
    "Alex M|UCZ0DJ1UBmS1sEjDBr2OABAw",
    "Alex M|UCZ0DJ1UBmS1sEjDBr2OABAw",
    "ALEX M techno|UCafxwwWt4VgDrug4s1OQIFA",
]


# --- разбор выдачи ----------------------------------------------------------


def test_каналы_схлопываются_и_считаются():
    """Поиск возвращает ролики, а не каналы, поэтому один канал приходит
    несколько раз. Показывать его столько же раз — мусор в глазах человека.
    """
    кандидаты = parse_search_output(ВЫДАЧА)

    assert len(кандидаты) == 2
    assert кандидаты[0].name == "Alex M"
    assert кандидаты[0].hits == 3
    assert кандидаты[1].hits == 2


def test_чаще_встреченный_идёт_первым():
    # Чем больше попаданий, тем вероятнее, что искали именно его.
    assert parse_search_output(ВЫДАЧА)[0].channel_id == "UCZ0DJ1UBmS1sEjDBr2OABAw"


def test_строки_без_разделителя_пропускаются():
    assert parse_search_output(["мусор без разделителя"]) == []


def test_негодный_идентификатор_отвергается():
    # Иначе в список попадёт строка, по которой канал не открыть.
    assert parse_search_output(["Канал|не-идентификатор"]) == []
    assert parse_search_output(["Канал|UCкороткий"]) == []


def test_имя_NA_отвергается():
    """yt-dlp печатает NA, когда названия в выдаче нет. Показать «NA»
    в списке — значит предложить человеку выбрать вслепую.
    """
    assert parse_search_output(["NA|UCZ0DJ1UBmS1sEjDBr2OABAw"]) == []


def test_имя_с_разделителем_внутри_не_рвётся():
    # Названия каналов бывают с вертикальной чертой.
    кандидаты = parse_search_output(["Канал | про железо|UCZ0DJ1UBmS1sEjDBr2OABAw"])
    assert кандидаты[0].name == "Канал | про железо"


def test_пустая_выдача():
    assert parse_search_output([]) == []


# --- адрес и перепись -------------------------------------------------------


def test_адрес_собирается_по_идентификатору():
    """Именно по идентификатору, а не по хендлу: у «Уютного подвальчика»
    хендл не угадывался ни в одном из трёх вариантов, все дали 404.
    """
    кандидат = Candidate(name="X", channel_id="UCeemTTAKVjHucKYFmc8V3Ug")
    assert кандидат.url.endswith("/channel/UCeemTTAKVjHucKYFmc8V3Ug/videos")


def test_пока_не_измерено_так_и_говорим():
    # Ноль выглядел бы как «пустой канал» — а это разные вещи.
    кандидат = Candidate(name="X", channel_id="UC" + "a" * 22)
    assert not кандидат.measured
    assert "меряю" in кандидат.describe()
    assert кандидат.size_range() is None


def test_перепись_дополняет_кандидата():
    кандидат = with_measurement(Candidate("X", "UC" + "a" * 22), [600.0, 1200.0])
    assert кандидат.videos == 2
    assert кандидат.seconds == 1800.0
    assert кандидат.measured


def test_ролики_без_длительности_не_считаются():
    """Обычно это трансляции и премьеры, у которых её ещё нет.
    Посчитать их нулями значит занизить оценку объёма.
    """
    кандидат = with_measurement(Candidate("X", "UC" + "a" * 22), [600.0, 0.0, None, 600.0])
    assert кандидат.videos == 2
    assert кандидат.seconds == 1200.0


def test_настоящий_случай_2026_09_02_разница_видна_до_добавления():
    """Поиск «alex m» дал канал на 2111 роликов и 1158,7 часа рядом с нужным
    на 37 роликов и 17,3 часа. Разница — два порядка, и увидеть её надо
    при выборе, а не утром по забитому диску.
    """
    большой = with_measurement(Candidate("Alex M", "UC" + "a" * 22), [1158.7 * 3600])
    маленький = with_measurement(Candidate("ALEX M", "UC" + "b" * 22), [17.3 * 3600])

    _, верх_большого = большой.size_range()
    _, верх_маленького = маленький.size_range()

    assert верх_большого / верх_маленького > 50
    assert "ГБ" in большой.describe()


# --- влезет ли --------------------------------------------------------------


def test_пока_не_измерено_ответа_нет():
    assert fits(Candidate("X", "UC" + "a" * 22), free_bytes=10**12) is None


def test_маленький_влезает():
    кандидат = with_measurement(Candidate("X", "UC" + "a" * 22), [17.3 * 3600])
    assert fits(кандидат, free_bytes=2_300 * 1024**3) is True


def test_судим_по_верхней_границе():
    """Ошибиться в сторону «влезет» хуже, чем в сторону «не влезет»:
    первое кончается забитым диском посреди ночи, второе — лишним вопросом.
    """
    кандидат = with_measurement(Candidate("X", "UC" + "a" * 22), [1158.7 * 3600])
    низ, верх = кандидат.size_range()
    свободно = int(низ * 1.2)  # нижней границы хватило бы, верхней — нет

    assert fits(кандидат, free_bytes=свободно, reserve=0) is False


@pytest.mark.parametrize("свободно", [0, 10 * 1024**3])
def test_на_пустом_диске_не_влезает_ничего(свободно):
    кандидат = with_measurement(Candidate("X", "UC" + "a" * 22), [100 * 3600])
    assert fits(кандидат, free_bytes=свободно) is False


# --- аватар канала ----------------------------------------------------------


def test_аватар_берётся_по_метке():
    """Проверено на живом канале: из девяти картинок первые шесть — широкий
    баннер (2560x424), и только у одной метка avatar_uncropped.
    """
    from core.search import pick_avatar

    картинки = [
        {"id": "0", "width": 1060, "height": 175, "url": "баннер"},
        {"id": "5", "width": 2560, "height": 424, "url": "баннер-большой"},
        {"id": "7", "width": 900, "height": 900, "url": "квадрат"},
        {"id": "avatar_uncropped", "width": 0, "height": 0, "url": "аватар"},
    ]
    assert pick_avatar(картинки) == "аватар"


def test_без_метки_берётся_самая_крупная_квадратная():
    from core.search import pick_avatar

    картинки = [
        {"id": "0", "width": 2560, "height": 424, "url": "баннер"},
        {"id": "7", "width": 176, "height": 176, "url": "мелкий"},
        {"id": "8", "width": 900, "height": 900, "url": "крупный"},
    ]
    assert pick_avatar(картинки) == "крупный"


def test_баннер_в_аватары_не_годится():
    """В маленькой ячейке списка от баннера осталась бы полоска неба."""
    from core.search import pick_avatar

    assert pick_avatar([{"id": "0", "width": 2560, "height": 424, "url": "баннер"}]) == ""


def test_нет_картинок_нет_аватара():
    from core.search import pick_avatar

    assert pick_avatar([]) == ""
    assert pick_avatar([{"id": "x", "width": 0, "height": 0}]) == ""


def test_настоящий_случай_большой_канал_измеряется_целиком(monkeypatch):
    """Перепись для оценки объёма шла через тот же предел журнала в 400 строк,
    что и перепись для выкачки. Канал на две тысячи роликов измерялся как
    канал на четыреста — и окно обещало «влезет» про впятеро больший объём."""
    from core.search import Candidate
    from core.supervisor import Verdict
    from core.ytdlp_args import DownloadSettings
    from runner import search as поиск
    from runner.process import RunOutcome

    доводы = {}

    def подделка(argv, policy, **kwargs):
        доводы.update(kwargs)
        строки = ["600"] * 2000
        return RunOutcome(verdict=Verdict.OK, exit_code=0, lines=строки[-400:], stdout_lines=строки)

    monkeypatch.setattr(поиск, "run_watched", подделка)
    кандидат, ответ = поиск.measure_channel(
        Candidate(name="Большой", channel_id="UC" + "x" * 22), DownloadSettings("a", "o")
    )
    assert доводы.get("keep_all_stdout") is True, "перепись просят хранить целиком"
    assert кандидат.videos == 2000, ответ
