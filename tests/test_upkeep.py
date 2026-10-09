"""Уход за архивом: уборка старого, сверка учёта с диском, обновление yt-dlp,
часы работы и новые настройки.

За месяц работы набралось 1858 журналов и 21 обломок загрузки, а в учёте —
39 повторных строк. Ничто из этого не ломало выкачку, и именно поэтому
копилось незамеченным.
"""

import pytest

from core.cleanup import KEEP_NEWEST, FileInfo, is_leftover, old_logs, stale_leftovers, total_size
from core.config import ConfigError, dump_config, loads, parse_config
from core.flow import ChannelResult, SessionSummary
from core.schedule import (
    Hours,
    Rhythm,
    format_hours,
    is_open,
    minutes_until_open,
    parse_hours,
)
from core.update import update_command
from core.verify import compare, id_of, without_duplicates
from core.ytdlp_args import DownloadSettings, build_args, build_batch_args
from runner.daemon import ask_stop, run_forever

СУТКИ = 86400.0
СЕЙЧАС = 1_000 * СУТКИ

# --- старые журналы ----------------------------------------------------------


def журналы(возрасты_в_сутках):
    return [
        FileInfo(name=f"{номер:04d}.log", modified=СЕЙЧАС - возраст * СУТКИ, size=100)
        for номер, возраст in enumerate(возрасты_в_сутках)
    ]


def test_старые_журналы_отбираются():
    файлы = журналы([1] * 30 + [40] * 10)
    assert len(old_logs(файлы, СЕЙЧАС, keep_days=30)) == 10


def test_нулевой_срок_значит_хранить_всё():
    assert old_logs(журналы([400] * 50), СЕЙЧАС, keep_days=0) == []


def test_самые_свежие_не_трогаем_даже_старые():
    """Программа простояла выключенной полгода: вернувшись, человек должен
    найти журналы последних проходов, а не пустую папку."""
    файлы = журналы([200 + номер for номер in range(50)])
    убрать = old_logs(файлы, СЕЙЧАС, keep_days=30)
    assert len(убрать) == 50 - KEEP_NEWEST
    свежие = {файл.name for файл in sorted(файлы, key=lambda ф: ф.modified)[-KEEP_NEWEST:]}
    assert not свежие & {файл.name for файл in убрать}


def test_журнал_ровно_на_границе_срока_остаётся():
    файлы = журналы([1] * KEEP_NEWEST + [30])
    assert old_logs(файлы, СЕЙЧАС, keep_days=30) == []


# --- обломки -----------------------------------------------------------------


@pytest.mark.parametrize(
    "имя, обломок",
    [
        ("2024 - Ролик [oxd5IAl-o3Q].f299.mp4.part", True),
        ("2024 - Ролик [oxd5IAl-o3Q].f299.mp4.ytdl", True),
        ("2020 - Ролик [7GNL3V-uX4k].mp4.part-Frag327.part", True),
        ("2020 - Ролик [7GNL3V-uX4k].mp4.part-Frag327", True),
        ("2024 - Ролик [oxd5IAl-o3Q].mkv", False),
        ("2024 - Первая часть [oxd5IAl-o3Q].mkv", False),
    ],
)
def test_обломок_опознаётся_по_имени(имя, обломок):
    assert is_leftover(имя) is обломок


def test_свежий_обломок_нескачанного_ролика_не_трогаем():
    """Это продолжение, которое yt-dlp подхватит следующим проходом. Удалив
    его, заставили бы качать гигабайты заново."""
    файл = FileInfo("К/Ролик [aaaaaaaaaaa].f299.mp4.part", СЕЙЧАС - 3600, 10**9)
    assert stale_leftovers([файл], СЕЙЧАС, frozenset()) == []


def test_обломок_уже_скачанного_ролика_убирается_сразу():
    файл = FileInfo("К/Ролик [aaaaaaaaaaa].f299.mp4.part", СЕЙЧАС - 3600, 10**9)
    assert stale_leftovers([файл], СЕЙЧАС, frozenset({"aaaaaaaaaaa"})) == [файл]


def test_давно_брошенный_обломок_убирается():
    файл = FileInfo("К/Ролик [aaaaaaaaaaa].f299.mp4.part", СЕЙЧАС - 8 * СУТКИ, 10**9)
    assert stale_leftovers([файл], СЕЙЧАС, frozenset()) == [файл]


def test_целый_ролик_обломком_не_считается_никогда():
    """Сколько бы ему ни было лет и что бы ни стояло в учёте."""
    файл = FileInfo("К/Ролик [aaaaaaaaaaa].mkv", СЕЙЧАС - 900 * СУТКИ, 10**9)
    assert stale_leftovers([файл], СЕЙЧАС, frozenset({"aaaaaaaaaaa"})) == []


def test_объём_считается():
    assert total_size([FileInfo("a", 0, 10), FileInfo("b", 0, 32)]) == 42


# --- сверка учёта с диском ---------------------------------------------------

УЧЁТ = "youtube aaaaaaaaaaa\nyoutube bbbbbbbbbbb\nyoutube aaaaaaaaaaa\nyoutube ccccccccccc\n"


def test_сходящийся_архив_чист():
    отчёт = compare(
        "youtube aaaaaaaaaaa\n", ["К/2024 - Ролик [aaaaaaaaaaa].mkv", "К/обложка [aaaaaaaaaaa].jpg"]
    )
    assert отчёт.clean and отчёт.records == 1 and отчёт.files == 1


def test_в_учёте_есть_файла_нет():
    """Такой ролик заново не скачается никогда — программа считает его забранным."""
    отчёт = compare(УЧЁТ, ["К/Ролик [aaaaaaaaaaa].mkv", "К/Ролик [bbbbbbbbbbb].mkv"])
    assert отчёт.missing_files == ("ccccccccccc",)


def test_файл_есть_в_учёте_нет():
    отчёт = compare("youtube aaaaaaaaaaa\n", ["К/А [aaaaaaaaaaa].mkv", "К/Б [ddddddddddd].mp4"])
    assert отчёт.unrecorded == (("ddddddddddd", "К/Б [ddddddddddd].mp4"),)


def test_повторные_строки_считаются():
    отчёт = compare(УЧЁТ, [])
    assert отчёт.duplicates == (("aaaaaaaaaaa", 2),)
    assert отчёт.extra_lines == 1 and отчёт.records == 4


def test_ролик_в_двух_папках_виден():
    """Так выглядел расколотый архив: один ролик в `Soyuz` и в `SoyuzUS`."""
    отчёт = compare("youtube aaaaaaaaaaa\n", ["Soyuz/Р [aaaaaaaaaaa].mkv", "SoyuzUS/Р [aaaaaaaaaaa].mkv"])
    assert отчёт.twins == (("aaaaaaaaaaa", ("Soyuz/Р [aaaaaaaaaaa].mkv", "SoyuzUS/Р [aaaaaaaaaaa].mkv")),)


@pytest.mark.parametrize(
    "имя",
    [
        "Ролик [aaaaaaaaaaa].jpg",
        "Ролик [aaaaaaaaaaa].ru.vtt",
        "Ролик [aaaaaaaaaaa].f299.mp4.part",
        "Ролик без идентификатора.mkv",
    ],
)
def test_субтитры_обложки_и_обломки_роликом_не_считаются(имя):
    """Наличие `.jpg` не значит, что видео на месте."""
    assert id_of(имя) == ""


def test_повторы_убираются_порядок_и_непонятое_остаются():
    """Непонятую строку не выбрасываем: формат чужой, и «почистив» то,
    смысла чего не знаем, можно обнулить учёт."""
    текст = "youtube aaaaaaaaaaa\nчто-то чужое\nyoutube bbbbbbbbbbb\nyoutube aaaaaaaaaaa\n"
    assert without_duplicates(текст) == "youtube aaaaaaaaaaa\nчто-то чужое\nyoutube bbbbbbbbbbb\n"
    assert without_duplicates("") == ""


def test_чистка_повторов_не_теряет_ни_одного_ролика():
    assert compare(without_duplicates(УЧЁТ), []).missing_files == compare(УЧЁТ, []).missing_files


# --- чем обновлять yt-dlp ----------------------------------------------------


def test_свой_yt_dlp_обновляется_через_pip_окружения():
    команда = update_command(
        r"C:\yta\.venv\Scripts\yt-dlp.EXE", r"C:\yta\.venv\scripts", r"C:\yta\.venv\Scripts\python.exe"
    )
    assert команда == (r"C:\yta\.venv\Scripts\python.exe", "-m", "pip", "install", "--upgrade", "yt-dlp")


def test_чужой_yt_dlp_обновляет_себя_сам():
    """Чем его ставил человек, мы не знаем; его собственный ответ точнее
    любой нашей догадки."""
    assert update_command("/usr/bin/yt-dlp", "/opt/yta/.venv/bin", "/opt/yta/.venv/bin/python") == (
        "/usr/bin/yt-dlp", "-U",
    )


def test_нет_yt_dlp_нет_команды():
    assert update_command(None, "/opt/yta/.venv/bin", "python") == ()


# --- часы работы -------------------------------------------------------------


def test_пустые_часы_значат_всегда():
    assert parse_hours("") is None
    assert is_open(None, 3 * 60) and minutes_until_open(None, 3 * 60) == 0


@pytest.mark.parametrize(
    "текст, ожидаем",
    [("23-7", Hours(23 * 60, 7 * 60)), ("23:00-07:30", Hours(23 * 60, 7 * 60 + 30)), (" 9 - 18 ", Hours(540, 1080))],
)
def test_часы_разбираются(текст, ожидаем):
    assert parse_hours(текст) == ожидаем


@pytest.mark.parametrize("текст", ["ночью", "23", "25-7", "23:61-7", "7-7", "23-"])
def test_непонятные_часы_это_отказ(текст):
    with pytest.raises(ValueError):
        parse_hours(текст)


def test_ночные_часы_переходят_через_полночь():
    ночь = Hours(23 * 60, 7 * 60)
    assert is_open(ночь, 23 * 60 + 30)
    assert is_open(ночь, 3 * 60)
    assert not is_open(ночь, 12 * 60)
    assert not is_open(ночь, 7 * 60), "конец в отрезок не входит"


def test_дневные_часы():
    день = Hours(9 * 60, 18 * 60)
    assert is_open(день, 9 * 60) and is_open(день, 17 * 60 + 59)
    assert not is_open(день, 18 * 60) and not is_open(день, 3 * 60)


def test_сколько_ждать_до_открытия():
    ночь = Hours(23 * 60, 7 * 60)
    assert minutes_until_open(ночь, 22 * 60) == 60
    assert minutes_until_open(ночь, 7 * 60) == 16 * 60
    assert minutes_until_open(Hours(9 * 60, 18 * 60), 20 * 60) == 13 * 60


def test_часы_переживают_запись():
    assert parse_hours(format_hours(Hours(23 * 60, 7 * 60 + 30))) == Hours(23 * 60, 7 * 60 + 30)
    assert format_hours(None) == ""


class Часы:
    def __init__(self, минута: float) -> None:
        self.сейчас = 0.0
        self.начало = минута

    def __call__(self) -> float:
        return self.сейчас

    def спать(self, сколько: float) -> None:
        self.сейчас += max(сколько, 0.001)

    def минута_суток(self) -> float:
        return (self.начало + self.сейчас / 60) % (24 * 60)


def _обход(tmp_path, часы, проход, **kwargs):
    return run_forever(
        проход,
        tools_dir=tmp_path,
        rhythm=Rhythm(idle=1800.0, busy=60.0, trouble=3600.0),
        sleep=часы.спать,
        clock=часы,
        minute_of_day=часы.минута_суток,
        **kwargs,
    )


def test_вне_часов_обход_ждёт_открытия(tmp_path):
    часы = Часы(минута=20 * 60)
    начались: list[float] = []

    def проход(should_stop):
        начались.append(часы.минута_суток())
        return SessionSummary(results=(ChannelResult(channel="X"),))

    _обход(tmp_path, часы, проход, hours=Hours(23 * 60, 7 * 60), passes=1)
    assert len(начались) == 1
    assert 23 * 60 <= начались[0] < 23 * 60 + 2, "проход начался с открытием, не раньше"


def test_конец_часов_прерывает_загрузку_но_не_останавливает_обход(tmp_path):
    """Конец часов — не просьба остановиться: обход ждёт следующего открытия."""
    часы = Часы(минута=6 * 60 + 59)
    ответы: list[bool] = []
    сообщения: list[str] = []

    def проход(should_stop):
        ответы.append(should_stop())
        часы.спать(120)  # за время прохода часы работы кончились
        ответы.append(should_stop())
        return SessionSummary(results=(ChannelResult(channel="X", downloaded=1),))

    сделано = _обход(
        tmp_path, часы, проход, hours=Hours(23 * 60, 7 * 60), passes=2, on_message=сообщения.append
    )
    assert ответы[:2] == [False, True]
    assert сделано == 2, "после закрытия обход дождался открытия и пошёл снова"


def test_просьба_остановиться_слышна_и_во_время_ожидания_открытия(tmp_path):
    часы = Часы(минута=12 * 60)
    спать = часы.спать

    def сон_с_просьбой(сколько):
        спать(сколько)
        if часы.сейчас > 30:
            ask_stop(tmp_path)

    сделано = run_forever(
        lambda should_stop: SessionSummary(),
        tools_dir=tmp_path,
        sleep=сон_с_просьбой,
        clock=часы,
        minute_of_day=часы.минута_суток,
        hours=Hours(23 * 60, 7 * 60),
    )
    assert сделано == 0
    assert часы.сейчас < 120, "ушёл сразу, а не досидел одиннадцать часов"


# --- настройки ---------------------------------------------------------------

ОСНОВА = {"paths": {"base": "/a"}}


def настройки(**разделы):
    return parse_config({**ОСНОВА, **разделы})


def test_новые_настройки_по_умолчанию_ничего_не_меняют():
    config = настройки()
    assert config.cookies_browser == "" and config.rate_limit == 0 and config.hours is None
    assert config.limits.crawl_speed == 100 and config.limits.crawl_minutes == 10


def test_новые_настройки_переживают_запись():
    config = настройки(
        download={"cookies_browser": "firefox", "rate_limit": 2048},
        schedule={"hours": "23-7"},
        limits={"crawl_speed": 50, "crawl_minutes": 15, "keep_logs_days": 7},
    )
    assert parse_config(loads(dump_config(config))) == config


def test_неизвестный_браузер_это_отказ():
    """Опечатку лучше поймать при чтении настроек, чем увидеть ночью отказом
    на каждом канале."""
    with pytest.raises(ConfigError):
        настройки(download={"cookies_browser": "firefoks"})


def test_потолок_скорости_ниже_порога_ползания_это_отказ():
    """Иначе надзорщик снимал бы ровно то, что человек попросил качать
    помедленнее."""
    with pytest.raises(ConfigError):
        настройки(download={"rate_limit": 150}, limits={"crawl_speed": 100})


def test_потолок_скорости_с_выключенной_проверкой_годится():
    assert настройки(download={"rate_limit": 150}, limits={"crawl_speed": 0}).rate_limit == 150


def test_непонятные_часы_в_настройках_это_отказ():
    with pytest.raises(ConfigError):
        настройки(schedule={"hours": "ночью"})


# --- ключи yt-dlp ------------------------------------------------------------


def test_потолок_скорости_уходит_в_yt_dlp():
    доводы = build_args(DownloadSettings("a", "o", rate_limit=2048), "u")
    assert доводы[доводы.index("--limit-rate") + 1] == "2048K"
    assert "--limit-rate" in build_batch_args(DownloadSettings("a", "o", rate_limit=2048), "b.txt")


def test_без_потолка_ключа_нет():
    assert "--limit-rate" not in build_args(DownloadSettings("a", "o"), "u")


def test_куки_из_браузера_уходят_в_yt_dlp():
    доводы = build_args(DownloadSettings("a", "o", cookies_browser="firefox"), "u")
    assert доводы[доводы.index("--cookies-from-browser") + 1] == "firefox"
    assert "--cookies" not in доводы
