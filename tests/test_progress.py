"""Проверки разбора прогресса.

Все образцы строк — дословно из журналов выкачки за 16–29.08.2026.
Проверяем на том, что yt-dlp печатает на самом деле, а не на том,
что я про него помню.
"""

import pytest

from core.progress import EventKind, parse_duration, parse_line, parse_size


def test_начало_файла():
    строка = r"[download] Destination: D:\Video\YouTube Archive\SoyuzUS\ролик.f399.mp4"
    событие = parse_line(строка)
    assert событие.kind is EventKind.DESTINATION
    assert событие.path.endswith("ролик.f399.mp4")


def test_файл_докачан():
    событие = parse_line("[download] 100% of  462.12MiB in 00:01:46 at 4.35MiB/s")
    assert событие.kind is EventKind.COMPLETED
    assert событие.size_bytes == int(462.12 * 1024**2)
    assert событие.seconds == 106.0
    assert событие.speed_bps == pytest.approx(4.35 * 1024**2)


def test_докачан_гигабайтный():
    событие = parse_line("[download] 100% of    1.53GiB in 00:08:45 at 2.97MiB/s")
    assert событие.size_bytes == int(1.53 * 1024**3)
    assert событие.seconds == 525.0


def test_переход_к_следующему_ролику():
    событие = parse_line("[download] Downloading item 4 of 206")
    assert событие.kind is EventKind.ITEM
    assert (событие.index, событие.total) == (4, 206)


def test_слияние_потоков():
    строка = r'[Merger] Merging formats into "D:\Video\Archive\ролик.mkv"'
    событие = parse_line(строка)
    assert событие.kind is EventKind.MERGING
    assert событие.path.endswith("ролик.mkv")


def test_пауза_между_роликами():
    событие = parse_line("[download] Sleeping 26.78 seconds ...")
    assert событие.kind is EventKind.SLEEPING
    assert событие.seconds == 26.78


def test_пауза_между_запросами():
    assert parse_line("[youtube] Sleeping 2.0 seconds ...").kind is EventKind.SLEEPING


def test_отказ():
    строка = "ERROR: [youtube] rbYUHA9ZOg8: Sign in to confirm you're not a bot."
    событие = parse_line(строка)
    assert событие.kind is EventKind.ERROR
    assert событие.is_error


def test_неопознанная_строка_не_теряется():
    # Молчаливое отбрасывание однажды стоило месяца незамеченной потери данных.
    событие = parse_line("[info] Video Thumbnail 39 does not exist")
    assert событие.kind is EventKind.OTHER
    assert событие.text == "[info] Video Thumbnail 39 does not exist"


# --- единицы ----------------------------------------------------------------


def test_двоичные_приставки_а_не_десятичные():
    """yt-dlp печатает MiB, а не MB. Спутать — ошибиться на 5% на мегабайтах
    и на 7% на гигабайтах, что незаметно портит любую оценку остатка.
    """
    assert parse_size("1", "MiB") == 1024**2
    assert parse_size("1", "GiB") == 1024**3
    assert parse_size("1", "MiB") != 1_000_000


def test_отказ_на_неизвестной_единице():
    with pytest.raises(ValueError):
        parse_size("1", "попугаев")


@pytest.mark.parametrize(
    "строка,секунд",
    [("00:01:46", 106.0), ("01:46", 106.0), ("46", 46.0), ("01:00:00", 3600.0)],
)
def test_длительность(строка, секунд):
    assert parse_duration(строка) == секунд


def test_отказ_на_непохожей_длительности():
    with pytest.raises(ValueError):
        parse_duration("1:2:3:4")


# --- настоящие случаи -------------------------------------------------------


def test_настоящий_случай_2026_08_16_первый_скачанный_ролик():
    """Первый ролик архива: 462 МБ видео и 43 МБ звука, 4,35 и 2,42 МБ/с.
    По этим числам считалась скорость выкачки и все сроки.
    """
    видео = parse_line("[download] 100% of  462.12MiB in 00:01:46 at 4.35MiB/s")
    звук = parse_line("[download] 100% of   43.14MiB in 00:00:17 at 2.42MiB/s")

    всего = видео.size_bytes + звук.size_bytes
    assert 0.49 * 1024**3 < всего < 0.51 * 1024**3, "не сходится с реальными 0,49 ГБ"
    assert видео.speed_bps > звук.speed_bps


def test_настоящий_случай_2026_08_29_счётчик_роликов_канала():
    """По строке «item N of M» интерфейс показывает, где идёт проход.
    У SoyuzUS было ровно 206 роликов — на этом числе сверялась перепись.
    """
    событие = parse_line("[download] Downloading item 206 of 206")
    assert (событие.index, событие.total) == (206, 206)
