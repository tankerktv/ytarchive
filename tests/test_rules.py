"""Правила отбора роликов канала и их место в списке каналов.

Правило отсекает ролики, которых человек не хочет. Ошибок тут две, и обе
молчаливые: отсечь нужное — ролик не скачается никогда; не отсечь ненужное —
диск забьётся тем, от чего отказались.
"""

from pathlib import Path

import pytest

from core.channels import Channel, format_channels, parse_channels, rename_channel, set_rules
from core.rules import Rules, RulesError, allows, format_rules, parse_rules
from core.supervisor import Verdict
from core.videos import parse_listing
from core.ytdlp_args import LISTING_FORMAT, DownloadSettings, build_enumerate_args
from runner import session
from runner.process import RunOutcome
from runner.session import SessionConfig, download_channel

# --- разбор ------------------------------------------------------------------


def test_пустое_поле_значит_без_правил():
    assert parse_rules("") == Rules()
    assert not parse_rules("  ")


def test_все_три_правила_разбираются():
    правила = parse_rules("min=60; max=7200 ;after=2024-01-01")
    assert правила == Rules(min_seconds=60, max_seconds=7200, after="20240101")


@pytest.mark.parametrize(
    "текст",
    [
        "mни=60",  # опечатка в ключе
        "min",  # без значения
        "min=минута",
        "after=01.01.2024",
        "after=2024-13-01",
        "after=2024-02-30",  # такого дня нет
        "min=7200;max=60",  # под такое не подойдёт ни один ролик
    ],
)
def test_непонятое_правило_не_проходит_молча(текст):
    """Опечатка значила бы, что человек считает короткие ролики отсечёнными,
    а они качаются."""
    with pytest.raises(RulesError):
        parse_rules(текст)


def test_запись_и_чтение_обратимы():
    правила = Rules(min_seconds=61, max_seconds=3600, after="20231231")
    assert parse_rules(format_rules(правила)) == правила
    assert format_rules(Rules()) == ""


# --- решение -----------------------------------------------------------------


def test_короткий_ролик_отсекается():
    assert not allows(Rules(min_seconds=60), 45, "")
    assert allows(Rules(min_seconds=60), 60, "")


def test_длинный_ролик_отсекается():
    assert not allows(Rules(max_seconds=3600), 3601, "")
    assert allows(Rules(max_seconds=3600), 3600, "")


def test_старый_ролик_отсекается():
    assert not allows(Rules(after="20240101"), 600, "20231231")
    assert allows(Rules(after="20240101"), 600, "20240101")


def test_неизвестная_длительность_проходит():
    """У трансляций и премьер длительности нет. Потерять ролик молча хуже,
    чем скачать лишний."""
    assert allows(Rules(min_seconds=60, max_seconds=3600), 0, "")


def test_неизвестная_дата_проходит():
    assert allows(Rules(after="20240101"), 600, "")


def test_без_правил_проходит_всё():
    assert allows(Rules(), 1, "19990101")


# --- в списке каналов --------------------------------------------------------


def test_строка_прежнего_вида_значит_то_же_что_значила():
    разбор = parse_channels("Канал|https://www.youtube.com/@x/videos\n")
    assert разбор.channels == (Channel(name="Канал", url="https://www.youtube.com/@x/videos"),)
    assert not разбор.problems


def test_правила_третьим_полем():
    разбор = parse_channels("Канал|https://www.youtube.com/@x/videos|min=60;after=2024-01-01\n")
    assert разбор.channels[0].rules == Rules(min_seconds=60, after="20240101")


def test_канал_с_непонятым_правилом_пропускается_целиком():
    """Качать его «на всякий случай» без правил нельзя: человек отсёк короткие
    ролики и узнал бы об этом по забитому диску."""
    разбор = parse_channels("Канал|https://www.youtube.com/@x/videos|короче=60\n")
    assert not разбор.channels
    assert len(разбор.problems) == 1


def test_правила_переживают_запись_списка():
    каналы = (
        Channel("А", "https://www.youtube.com/@a/videos", Rules(min_seconds=60)),
        Channel("Б", "https://www.youtube.com/@b/videos"),
    )
    assert parse_channels(format_channels(каналы)).channels == каналы


def test_переименование_не_теряет_правил():
    каналы = (Channel("А", "https://www.youtube.com/@a/videos", Rules(max_seconds=600)),)
    assert rename_channel(каналы, 0, "Б")[0].rules == Rules(max_seconds=600)


def test_правила_задаются_и_снимаются():
    каналы = (Channel("А", "https://www.youtube.com/@a/videos"),)
    с_правилом = set_rules(каналы, 0, Rules(min_seconds=60))
    assert с_правилом[0].rules == Rules(min_seconds=60)
    assert set_rules(с_правилом, 0, Rules())[0].rules == Rules()
    assert set_rules(каналы, 5, Rules(min_seconds=60)) == каналы


@pytest.mark.parametrize(
    "адрес",
    [
        "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "https://www.youtube.com/watch?v=rbYUHA9ZOg8",
        "https://youtu.be/rbYUHA9ZOg8",
    ],
)
def test_плейлист_и_отдельный_ролик_годятся_как_источник(адрес):
    разбор = parse_channels(f"Подборка|{адрес}\n")
    assert разбор.channels and разбор.channels[0].url == адрес


# --- перепись ----------------------------------------------------------------


def test_перепись_просит_дату():
    """Без approximate_date перепись даты не отдаёт вовсе — проверено на
    живом канале: в поле приходит NA."""
    доводы = build_enumerate_args(DownloadSettings(archive_path="a", output_template="o"), "u")
    assert "youtubetab:skip=authcheck;approximate_date" in доводы
    assert LISTING_FORMAT in доводы
    assert "%(upload_date)s" in LISTING_FORMAT


def test_строка_с_датой_разбирается():
    перепись = parse_listing("DEjRk12G0eo\t2948\t20261008\t2026 Ram 3500 First Service\n")
    ролик = перепись.videos[0]
    assert (ролик.seconds, ролик.upload_date, ролик.title) == (
        2948.0, "20261008", "2026 Ram 3500 First Service",
    )


def test_неизвестная_дата_это_пустая_строка():
    assert parse_listing("DEjRk12G0eo\t2948\tNA\tНазвание\n").videos[0].upload_date == ""


def test_строка_прежнего_вида_без_даты_читается():
    ролик = parse_listing("DEjRk12G0eo\t2948\tНазвание ролика\n").videos[0]
    assert ролик.title == "Название ролика" and ролик.upload_date == ""


def test_табуляция_в_названии_не_съедает_его_начало():
    ролик = parse_listing("DEjRk12G0eo\t2948\t20261008\tДо\tпосле\n").videos[0]
    assert ролик.title == "До\tпосле"
    старый = parse_listing("DEjRk12G0eo\t2948\tДо\tпосле\tещё\n").videos[0]
    assert старый.title == "До\tпосле\tещё"


# --- в очереди ---------------------------------------------------------------


def test_правила_вычёркивают_из_очереди_и_об_этом_сказано(tmp_path: Path, monkeypatch):
    архив = tmp_path / "downloaded.txt"
    архив.write_text("", encoding="utf-8")
    очереди: list[list[str]] = []
    сообщения: list[str] = []

    def подделка(argv, policy, **kwargs):
        if "--flat-playlist" in argv:
            строки = [
                "aaaaaaaaaaa\t30\t20260101\tКороткий",
                "bbbbbbbbbbb\t900\t20260102\tОбычный",
                "ccccccccccc\t900\t20190101\tСтарый",
                "ddddddddddd\tNA\tNA\tТрансляция",
            ]
            return RunOutcome(verdict=Verdict.OK, exit_code=0, lines=строки, stdout_lines=строки)
        очереди.append(Path(argv[argv.index("--batch-file") + 1]).read_text(encoding="utf-8").split())
        return RunOutcome(verdict=Verdict.OK, exit_code=0)

    monkeypatch.setattr(session, "run_watched", подделка)
    config = SessionConfig(
        base_dir=tmp_path,
        channels_file=tmp_path / "channels.txt",
        settings=DownloadSettings(archive_path=str(архив), output_template="x"),
    )
    канал = Channel("К", "https://youtube.com/@x/videos", Rules(min_seconds=60, after="20240101"))
    download_channel(канал, config, on_message=сообщения.append)

    assert очереди == [["bbbbbbbbbbb", "ddddddddddd"]]
    assert any("2" in строка and "правилам" in строка for строка in сообщения), (
        "отсечённое не должно пропадать молча"
    )
