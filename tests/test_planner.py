"""Проверки очереди и оценок.

Отдельно плотно покрыт `is_incremental_safe`: включённый не вовремя быстрый
проход обрывает выкачку на первом же скачанном ролике и остальное не забирает.
Ошибка тихая — архив просто перестаёт пополняться.
"""

import pytest

from core.archive import ArchiveContents, parse_archive
from core.planner import (
    BITRATE_HIGH_MBPS,
    BITRATE_LOW_MBPS,
    ChannelListing,
    build_queue,
    enough_space,
    estimate_bytes,
    estimate_range,
    is_incremental_safe,
)

ПУСТОЙ = ArchiveContents()


def архив(*ids):
    return ArchiveContents(video_ids=frozenset(ids))


# --- очередь ----------------------------------------------------------------


def test_очередь_идёт_по_порядку_каналов_и_роликов():
    listings = [
        ChannelListing("Первый", ("aaaaaaaaaaa", "bbbbbbbbbbb")),
        ChannelListing("Второй", ("ccccccccccc",)),
    ]
    queue = build_queue(listings, ПУСТОЙ)
    assert [(w.channel, w.video_id) for w in queue] == [
        ("Первый", "aaaaaaaaaaa"),
        ("Первый", "bbbbbbbbbbb"),
        ("Второй", "ccccccccccc"),
    ]


def test_скачанное_в_очередь_не_попадает():
    listings = [ChannelListing("Канал", ("aaaaaaaaaaa", "bbbbbbbbbbb"))]
    queue = build_queue(listings, архив("aaaaaaaaaaa"))
    assert [w.video_id for w in queue] == ["bbbbbbbbbbb"]


def test_ролик_в_двух_каналах_качается_один_раз():
    # Один и тот же ролик может попасть в перепись двух каналов.
    listings = [
        ChannelListing("Первый", ("aaaaaaaaaaa",)),
        ChannelListing("Второй", ("aaaaaaaaaaa", "bbbbbbbbbbb")),
    ]
    queue = build_queue(listings, ПУСТОЙ)
    assert [(w.channel, w.video_id) for w in queue] == [
        ("Первый", "aaaaaaaaaaa"),
        ("Второй", "bbbbbbbbbbb"),
    ]


def test_пустая_очередь_когда_всё_скачано():
    listings = [ChannelListing("Канал", ("aaaaaaaaaaa",))]
    assert build_queue(listings, архив("aaaaaaaaaaa")) == []


# --- быстрый проход ---------------------------------------------------------


def test_быстрый_проход_безопасен_когда_не_хватает_только_новых():
    # Классический случай: вышло два свежих ролика, остальное скачано.
    ids = ("новый1новый", "новый2новый", "ccccccccccc", "ddddddddddd")
    assert is_incremental_safe(ids, архив("ccccccccccc", "ddddddddddd")) is True


def test_быстрый_проход_опасен_при_дыре_в_середине():
    # Между скачанными есть незабранный — быстрый проход оборвётся раньше
    # и эту дыру не заметит уже никогда.
    ids = ("aaaaaaaaaaa", "дыра_дыра1", "ccccccccccc")
    assert is_incremental_safe(ids, архив("aaaaaaaaaaa", "ccccccccccc")) is False


def test_быстрый_проход_безопасен_на_полностью_скачанном():
    ids = ("aaaaaaaaaaa", "bbbbbbbbbbb")
    assert is_incremental_safe(ids, архив(*ids)) is True


def test_быстрый_проход_безопасен_на_пустой_переписи():
    assert is_incremental_safe((), ПУСТОЙ) is True


def test_настоящий_случай_2026_08_27_на_недособранном_архиве_быстрый_проход_нельзя():
    """27.08 MurkPOWER был скачан на 61%: 351 ролик из 573.

    Если бы быстрый проход включили тогда, он оборвался бы на первом же
    знакомом ролике, и оставшиеся 222 не забрались бы никогда. Ровно поэтому
    решение о нём принимает код, а не человек по настроению.
    """
    # Новые скачаны, старые ещё нет — типичная середина сбора.
    ids = tuple(f"видео{n:06d}" for n in range(10))
    архив_середины = архив(*ids[:4])

    assert is_incremental_safe(ids, архив_середины) is False


def test_настоящий_случай_2026_08_29_упавший_ролик_делает_дыру():
    """IMyAvT64D8g упал на срыве DNS и остался незабранным, а роликам вокруг него
    повезло больше — они скачались.

    Порядок здесь решает всё. Перепись идёт новыми вперёд, и раз более новый
    ролик уже в архиве, а этот нет — образовалась дыра, до которой быстрый
    проход не доберётся: он оборвётся на первом же знакомом, то есть раньше.
    """
    ids = ("rbYUHA9ZOg8", "IMyAvT64D8g", "aRbfazQ_Cns")
    состояние = parse_archive("youtube rbYUHA9ZOg8\nyoutube aRbfazQ_Cns\n")
    assert is_incremental_safe(ids, состояние) is False


# --- оценка объёма ----------------------------------------------------------


def test_битрейт_в_мегабитах_а_не_мегабайтах():
    # Перепутать эти единицы — ошибиться в восемь раз.
    assert estimate_bytes(8.0, 1.0) == 1_000_000


def test_оценка_растёт_с_битрейтом():
    assert estimate_bytes(100.0, 3.7) > estimate_bytes(100.0, 1.4)


@pytest.mark.parametrize("плохой", [0, -1])
def test_отказ_на_неположительном_битрейте(плохой):
    with pytest.raises(ValueError):
        estimate_bytes(100.0, плохой)


def test_отказ_на_отрицательной_длительности():
    with pytest.raises(ValueError):
        estimate_bytes(-1.0, 1.4)


def test_настоящий_случай_2026_08_16_вилка_на_928_часов():
    """Перепись четырёх каналов дала 1872 ролика и 928 часов.

    Фактически собралось около 1,3 ТБ. Вилка обязана его накрывать —
    иначе оценка «сколько нужно места», ради которой всё начиналось,
    вводила бы в заблуждение.
    """
    секунд = 928.1 * 3600
    низ, верх = estimate_range(секунд)
    факт = int(1.3 * 1000**4)  # 1,3 ТБ в байтах по десятичной шкале

    assert низ < факт < верх, f"вилка {низ}..{верх} не накрывает факт {факт}"
    assert BITRATE_LOW_MBPS < BITRATE_HIGH_MBPS


# --- место на диске ---------------------------------------------------------


def test_места_хватает_с_запасом():
    assert enough_space(needed=10, free=100, reserve=20) is True


def test_места_не_хватает_если_съедает_запас():
    # Запас нужен под слияние: во время него на диске лежат и потоки, и результат.
    assert enough_space(needed=85, free=100, reserve=20) is False


def test_на_границе_запаса_место_ещё_есть():
    assert enough_space(needed=80, free=100, reserve=20) is True


def test_отказ_на_отрицательных_объёмах():
    with pytest.raises(ValueError):
        enough_space(needed=-1, free=100)
