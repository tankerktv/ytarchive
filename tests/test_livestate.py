"""Проверки живого состояния.

Файл читается окном на ходу, поэтому здесь плотно покрыты две вещи:
арифметика доли (полоса не должна дёргаться и врать) и живучесть чтения
(окно обязано пережить попадание на середину записи, а не упасть).
"""

import pytest

from core.livestate import (
    LiveState,
    apply_event,
    from_text,
    should_write,
    start_channel,
    to_text,
)
from core.progress import parse_line

ЧАС = 3600.0


def применить(state, строка, now=ЧАС):
    return apply_event(state, parse_line(строка), now=now)


# --- складывание событий ----------------------------------------------------


def test_начало_файла_обнуляет_проценты():
    было = LiveState(percent=87.0, speed_bps=1000.0, eta="00:12")
    стало = применить(было, "[download] Destination: F:/архив/канал/ролик.f399.mp4")

    assert стало.file_name == "ролик.f399.mp4"
    assert стало.percent == 0.0
    assert стало.speed_bps == 0.0
    assert стало.eta == ""


def test_идущая_загрузка():
    стало = применить(LiveState(), "[download]  45.2% of  756.17MiB at 2.87MiB/s ETA 00:23")

    assert стало.percent == 45.2
    assert стало.size_bytes == int(756.17 * 1024**2)
    assert стало.speed_bps == pytest.approx(2.87 * 1024**2)
    assert стало.eta == "00:23"


def test_оценочный_размер_с_тильдой():
    # В начале сервер ещё не сказал точный размер, и yt-dlp ставит тильду.
    стало = применить(LiveState(), "[download]   0.5% of ~1.23GiB at 1.10MiB/s ETA 12:34")
    assert стало.percent == 0.5
    assert стало.size_bytes == int(1.23 * 1024**3)


def test_неизвестные_скорость_и_остаток_законны():
    """В самом начале их неоткуда взять. Считать это поломкой значит
    показывать человеку тревогу на ровном месте.
    """
    стало = применить(LiveState(), "[download]   0.0% of ~1.23GiB at  Unknown B/s ETA Unknown")

    assert стало.percent == 0.0
    assert стало.speed_bps == 0.0
    assert стало.eta == ""


def test_завершение_ставит_сто_процентов():
    стало = применить(LiveState(percent=87.0), "[download] 100% of  462.12MiB in 00:01:46 at 4.35MiB/s")
    assert стало.percent == 100.0
    assert стало.eta == ""


def test_переход_к_ролику():
    стало = применить(LiveState(), "[download] Downloading item 4 of 206")
    assert (стало.item_index, стало.item_total) == (4, 206)


def test_неизвестная_строка_не_портит_состояние():
    было = LiveState(file_name="ролик.mp4", percent=50.0)
    assert применить(было, "[info] Video Thumbnail 39 does not exist") == было


def test_смена_канала_обнуляет_счётчики_роликов():
    было = LiveState(channel="SoyuzUS", item_index=206, item_total=206, file_name="старый.mp4")
    стало = start_channel(было, "MurkPOWER", 2, 4, now=ЧАС)

    assert стало.channel == "MurkPOWER"
    assert (стало.channel_index, стало.channel_total) == (2, 4)
    assert стало.item_index == 0
    assert стало.file_name == ""


# --- доля пройденного -------------------------------------------------------


def test_доля_без_переписи_равна_нулю():
    # Пока неизвестно, сколько всего роликов, врать про долю нельзя.
    assert LiveState(item_index=5).item_fraction() == 0.0


def test_доля_учитывает_процент_текущего_ролика():
    """Иначе полоса стояла бы неподвижно два часа сорок девять минут,
    пока качается один большой ролик, и дёргалась скачком.
    """
    начало = LiveState(item_index=1, item_total=10, percent=0.0).item_fraction()
    середина = LiveState(item_index=1, item_total=10, percent=50.0).item_fraction()

    assert начало == 0.0
    assert середина == pytest.approx(0.05)


def test_доля_не_превышает_единицы():
    # Канал иногда отдаёт больше роликов, чем обещал переписью.
    assert LiveState(item_index=250, item_total=206, percent=100.0).item_fraction() == 1.0


def test_доля_на_последнем_ролике():
    assert LiveState(item_index=10, item_total=10, percent=100.0).item_fraction() == 1.0


# --- запись и чтение --------------------------------------------------------


def test_запись_и_чтение_обратимы():
    было = LiveState(
        channel="SoyuzUS", channel_index=1, channel_total=4,
        item_index=7, item_total=206, file_name="ролик.mp4",
        percent=42.5, size_bytes=123456, speed_bps=3.3, eta="01:02", updated_at=ЧАС,
    )
    assert from_text(to_text(было)) == было


def test_русские_имена_переживают_запись():
    было = LiveState(channel="Уютный подвальчик", file_name="Как пиратили 8 и 16 бит.mkv")
    assert from_text(to_text(было)) == было


@pytest.mark.parametrize("мусор", ["", "не json", "[1,2,3]", '{"percent": "много"}', "{"])
def test_испорченный_файл_читается_как_отсутствие(мусор):
    """Окно читает файл на ходу и может попасть на середину записи.
    Падать при этом нельзя — это окно наблюдения, а не выкачка.
    """
    assert from_text(мусор) is None


def test_лишние_поля_не_мешают():
    # Файл мог быть записан более новой версией программы.
    assert from_text('{"channel": "X", "чего-то-новое": 1}').channel == "X"


# --- частота записи ---------------------------------------------------------


def test_чаще_положенного_не_пишем():
    # Иначе на один ролик выйдут тысячи обращений к диску.
    assert should_write(last_write=100.0, now=100.5, interval=1.0) is False


def test_по_истечении_промежутка_пишем():
    assert should_write(last_write=100.0, now=101.0, interval=1.0) is True


def test_отказ_на_неположительном_промежутке():
    with pytest.raises(ValueError):
        should_write(0.0, 1.0, interval=0)


def test_логическое_значение_не_сходит_за_число():
    """В Python bool — подвид int, и без отдельной проверки `true`
    молча стал бы единицей.
    """
    assert from_text('{"item_index": true}') is None


def test_целое_годится_там_где_ждали_дробное():
    # JSON не различает 3 и 3.0, и отвергать такое было бы придиркой.
    состояние = from_text('{"percent": 42}')
    assert состояние is not None
    assert состояние.percent == 42.0


def test_дробное_не_годится_там_где_ждали_целое():
    assert from_text('{"item_index": 1.5}') is None
