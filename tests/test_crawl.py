"""Загрузка, которая говорит, но не продвигается.

Настоящий случай: 19.09.2026 ролик на полтора гигабайта тянулся пять часов.
yt-dlp всё это время печатал строки прогресса, поэтому надзор по молчанию
его не тронул, а остальные каналы простояли в очереди до вечера.

Обратная ошибка не лучше: снять здоровую загрузку значит качать её заново.
Поэтому половина проверок здесь — про то, когда снимать НЕЛЬЗЯ.
"""

from pathlib import Path

import pytest

from core.channels import Channel
from core.crawl import (
    CrawlPolicy,
    done_bytes,
    is_crawling,
    line_is_slow,
    observe,
    video_id_from_path,
)
from core.supervisor import Verdict
from core.ytdlp_args import DownloadSettings
from runner import session
from runner.process import RunOutcome
from runner.session import SessionConfig, download_channel

МБ = 1024 * 1024
ПОЛИТИКА = CrawlPolicy(window=600.0, min_speed=100 * 1024)


def отметки(шаги, политика=ПОЛИТИКА):
    """Собрать отметки из пар (время, байт), как это делает цикл выкачки."""
    итог = ()
    for когда, сколько in шаги:
        итог = observe(итог, когда, сколько, политика.window)
    return итог


# --- когда снимать ----------------------------------------------------------


def test_случай_19_сентября_опознаётся():
    """Полтора гигабайта за пять часов — около 83 КиБ/с. Ниже порога."""
    скорость = 1.5 * 1024 * МБ / (5 * 3600)
    шаги = [(t, скорость * t) for t in range(0, 601, 5)]
    assert is_crawling(отметки(шаги), 600.0, ПОЛИТИКА)


def test_стоящая_на_месте_загрузка_ползёт():
    шаги = [(t, 50 * МБ) for t in range(0, 700, 5)]
    assert is_crawling(отметки(шаги), 700.0, ПОЛИТИКА)


def test_замолчавший_прогресс_тоже_ползание():
    """yt-dlp перестал печатать проценты и только повторяет запросы: отметок
    нет, но и прироста нет. Судим по времени, а не по числу отметок."""
    шаги = [(0.0, 10 * МБ), (5.0, 11 * МБ)]
    assert is_crawling(отметки(шаги), 700.0, ПОЛИТИКА)


# --- когда снимать нельзя ---------------------------------------------------


def test_здоровая_загрузка_не_ползёт():
    шаги = [(t, 4 * МБ * t) for t in range(0, 700, 5)]
    assert not is_crawling(отметки(шаги), 700.0, ПОЛИТИКА)


def test_пока_наблюдаем_меньше_окна_не_судим():
    """В начале файла скорость ещё неизвестна; приговор по первым секундам
    снимал бы каждую загрузку, едва она началась."""
    шаги = [(t, 0.0) for t in range(0, 500, 5)]
    assert not is_crawling(отметки(шаги), 599.0, ПОЛИТИКА)


def test_без_отметок_не_судим():
    assert not is_crawling((), 10_000.0, ПОЛИТИКА)


def test_ровно_на_пороге_ещё_не_ползёт():
    шаги = [(0.0, 0.0), (600.0, 100 * 1024 * 600.0)]
    assert not is_crawling(отметки(шаги), 600.0, ПОЛИТИКА)


def test_нулевой_порог_выключает_проверку():
    """На медленной линии порог пришлось бы подбирать. Выключить честнее."""
    выключено = CrawlPolicy(window=600.0, min_speed=0)
    шаги = [(t, 0.0) for t in range(0, 2000, 5)]
    assert not выключено.enabled
    assert not is_crawling(отметки(шаги, выключено), 2000.0, выключено)


def test_медленное_начало_не_приговор_если_потом_разогналась():
    """Мерится последнее окно, а не вся жизнь файла."""
    шаги = [(t, 1024.0 * t) for t in range(0, 600, 5)]
    шаги += [(t, 600 * 1024.0 + 5 * МБ * (t - 600)) for t in range(600, 1300, 5)]
    assert not is_crawling(отметки(шаги), 1300.0, ПОЛИТИКА)


def test_быстрое_начало_не_спасает_если_встала():
    шаги = [(t, 5 * МБ * t) for t in range(0, 300, 5)]
    шаги += [(t, 5 * МБ * 300) for t in range(300, 1000, 5)]
    assert is_crawling(отметки(шаги), 1000.0, ПОЛИТИКА)


def test_шаг_назад_в_оценке_размера_не_ломает_счёт():
    """Оценка размера у yt-dlp плавает, и «скачано» может уменьшиться."""
    шаги = [(0.0, 500 * МБ), (300.0, 480 * МБ), (600.0, 470 * МБ)]
    assert is_crawling(отметки(шаги), 600.0, ПОЛИТИКА)


def test_окно_не_копит_отметки_бесконечно():
    """Строк прогресса на большом ролике десятки тысяч."""
    шаги = [(float(t), float(t)) for t in range(0, 20_000)]
    assert len(отметки(шаги)) <= 602


def test_одна_отметка_старше_окна_остаётся():
    """По ней считается прирост за ПОЛНОЕ окно. Без неё мерили бы отрезок
    короче окна и снимали здоровую загрузку."""
    итог = отметки([(0.0, 0.0), (100.0, 1.0), (650.0, 2.0)])
    assert итог[0][0] <= 650.0 - 600.0


# --- разбор ------------------------------------------------------------------


def test_скачано_считается_из_процента_и_размера():
    assert done_bytes(50.0, 200) == 100.0
    assert done_bytes(None, 200) is None
    assert done_bytes(50.0, None) is None


@pytest.mark.parametrize(
    "путь, ожидаем",
    [
        (r"F:\Архив\MurkPOWER\2024-04-11 - BMW E87 [oxd5IAl-o3Q].f299.mp4", "oxd5IAl-o3Q"),
        ("/srv/a/2020-01-01 - Название [abcdefghijk].mkv", "abcdefghijk"),
        ("/srv/a/Название [в скобках] и ещё [abcdefghijk].webm", "abcdefghijk"),
        ("/srv/a/без идентификатора.mkv", ""),
    ],
)
def test_идентификатор_из_имени_файла(путь, ожидаем):
    assert video_id_from_path(путь) == ожидаем


def test_два_подряд_значит_дело_в_линии():
    assert not line_is_slow(1)
    assert line_is_slow(2)


# --- цикл выкачки ------------------------------------------------------------


def _стенд(tmp_path: Path, monkeypatch, ответы):
    """Канал из трёх роликов и подставной запуск, отвечающий по списку.

    Каждый ответ — (приговор, какой ролик «качался», какие дописать в учёт).
    Возвращает сообщения и очереди, с которыми звали загрузку.
    """
    архив = tmp_path / "downloaded.txt"
    архив.write_text("", encoding="utf-8")
    очереди: list[list[str]] = []
    сообщения: list[str] = []
    остаток = list(ответы)

    def подделка(argv, policy, *, on_line=None, **kwargs):
        if "--flat-playlist" in argv:
            строки = [
                "aaaaaaaaaaa\t600\t20260101\tПервый",
                "bbbbbbbbbbb\t600\t20260102\tВторой",
                "ccccccccccc\t600\t20260103\tТретий",
            ]
            return RunOutcome(verdict=Verdict.OK, exit_code=0, lines=строки, stdout_lines=строки)
        список = Path(argv[argv.index("--batch-file") + 1]).read_text(encoding="utf-8").split()
        очереди.append(список)
        приговор, качался, готовые = остаток.pop(0)
        if качался and on_line is not None:
            on_line(f"[download] Destination: /a/2026 - Ролик [{качался}].f299.mp4")
        with архив.open("a", encoding="utf-8") as fh:
            for ролик in готовые:
                fh.write(f"youtube {ролик}\n")
        return RunOutcome(verdict=приговор, exit_code=0 if приговор is Verdict.OK else None)

    monkeypatch.setattr(session, "run_watched", подделка)
    config = SessionConfig(
        base_dir=tmp_path,
        channels_file=tmp_path / "channels.txt",
        settings=DownloadSettings(archive_path=str(архив), output_template="x"),
    )
    итог = download_channel(
        Channel(name="Канал", url="https://youtube.com/@x/videos"),
        config,
        on_message=сообщения.append,
    )
    return итог, очереди, сообщения


def test_ползущий_ролик_откладывается_а_очередь_идёт_дальше(tmp_path, monkeypatch):
    """Главное: один ролик больше не держит остальные."""
    итог, очереди, сообщения = _стенд(
        tmp_path,
        monkeypatch,
        [
            (Verdict.CRAWLING, "bbbbbbbbbbb", ["aaaaaaaaaaa"]),
            (Verdict.OK, "", ["ccccccccccc"]),
        ],
    )
    assert очереди == [["aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"], ["ccccccccccc"]]
    assert итог[0] == 2, "скачаны оба здоровых ролика"
    assert any("bbbbbbbbbbb" in строка for строка in сообщения), "отложенный назван по имени"


def test_отложенный_ролик_в_этом_проходе_больше_не_берётся(tmp_path, monkeypatch):
    _итог, очереди, _сообщения = _стенд(
        tmp_path,
        monkeypatch,
        [
            (Verdict.CRAWLING, "aaaaaaaaaaa", []),
            (Verdict.OK, "", ["bbbbbbbbbbb", "ccccccccccc"]),
        ],
    )
    assert "aaaaaaaaaaa" not in очереди[1]


def test_два_ползущих_подряд_проверка_выключается(tmp_path, monkeypatch):
    """Ползёт всё подряд — дело в линии. Снимать дальше значит терять по
    десять минут на каждом ролике и не скачать ничего."""
    _итог, очереди, сообщения = _стенд(
        tmp_path,
        monkeypatch,
        [
            (Verdict.CRAWLING, "aaaaaaaaaaa", []),
            (Verdict.CRAWLING, "bbbbbbbbbbb", []),
            (Verdict.OK, "", []),
        ],
    )
    assert очереди[2] == ["aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"], (
        "после вывода о медленной линии отложенные возвращаются в очередь"
    )
    assert any("crawl_speed" in строка for строка in сообщения), "человеку сказано, что поправить"


def test_ползущий_после_удачного_не_считается_вторым_подряд(tmp_path, monkeypatch):
    """Между двумя ползущими что-то скачалось — значит линия жива, а не
    повезло только этим двоим."""
    _итог, очереди, сообщения = _стенд(
        tmp_path,
        monkeypatch,
        [
            (Verdict.CRAWLING, "aaaaaaaaaaa", []),
            (Verdict.CRAWLING, "ccccccccccc", ["bbbbbbbbbbb"]),
        ],
    )
    assert len(очереди) == 2
    assert not any("crawl_speed" in строка for строка in сообщения)


def test_неопознанный_ползущий_не_зацикливает(tmp_path, monkeypatch):
    """Если не знаем, кого откладывать, проверку выключаем: иначе один и тот
    же ролик снимался бы снова и снова."""
    _итог, очереди, _сообщения = _стенд(
        tmp_path,
        monkeypatch,
        [
            (Verdict.CRAWLING, "", []),
            (Verdict.OK, "", []),
        ],
    )
    assert len(очереди) == 2
