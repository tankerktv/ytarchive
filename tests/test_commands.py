"""Проверки команд как таковых.

Их долго не было, и это вышло боком: `probe_channel` стал возвращать пару
(решение и диагноз), а `check` продолжал обращаться с ней как с одним
значением. Тесты ядра были зелёными — они этой склейки не касались, — и
команда падала бы на первом же канале.

Сеть сюда не заходит: проверка канала подменяется.
"""

import pytest

from app import main as app_main
from core.channels import Channel, ParseResult
from core.flow import Action, Decision


class ПоддельныйАрхив:
    unreadable = ()

    def __len__(self) -> int:
        return 0


@pytest.fixture
def стенд(monkeypatch, tmp_path):
    """Настройки и состояние подменены; остаётся сама команда."""
    from core.config import loads, parse_config

    config = parse_config(loads(f'[paths]\nbase = "{tmp_path.as_posix()}"\n'))
    monkeypatch.setattr(app_main, "load_config", lambda путь: (config, путь))
    monkeypatch.setattr(
        app_main,
        "_state",
        lambda session: (
            ParseResult(
                channels=(
                    Channel(name="SoyuzUS", url="https://youtube.com/@SoyuzUS/videos"),
                    Channel(name="MurkPOWER", url="https://youtube.com/@MurkPOWER/videos"),
                ),
                problems=(),
            ),
            ПоддельныйАрхив(),
        ),
    )
    return config


class Аргументы:
    config = "ytarchive.toml"


def test_проверка_каналов_разбирает_ответ_разведки(стенд, monkeypatch):
    """Настоящий случай 02.09: разведка стала возвращать пару, а команда
    читала её как одно значение — и падала на первом же канале.
    """
    monkeypatch.setattr(
        app_main,
        "probe_channel",
        lambda channel, session, **kwargs: (Decision(action=Action.PROCEED), None),
    )
    assert app_main.cmd_check(Аргументы()) == 0


def test_отказ_канала_виден_кодом_возврата(стенд, monkeypatch, capsys):
    """Ноль при отказе означал бы «всё хорошо» в любом скрипте, который
    зовёт проверку.
    """
    monkeypatch.setattr(
        app_main,
        "probe_channel",
        lambda channel, session, **kwargs: (
            Decision(action=Action.STOP, reason="нужен вход в аккаунт"),
            None,
        ),
    )
    код = app_main.cmd_check(Аргументы())
    вывод = capsys.readouterr().out

    assert код == 1
    assert "нужен вход в аккаунт" in вывод


def test_образец_настроек_не_содержит_чужих_путей(tmp_path, capsys):
    """В образце стоит метка, а не рабочий путь автора: чужой не подойдёт
    никому и расскажет о прежнем владельце больше, чем нужно.
    """
    from core.config import HOME_MARK

    class Свои:
        config = str(tmp_path / "ytarchive.toml")
        force = False
        dry_run = False

    assert app_main.cmd_init(Свои()) == 0
    текст = (tmp_path / "ytarchive.toml").read_text(encoding="utf-8")

    assert HOME_MARK not in текст, "метка осталась неподставленной"
    assert "Movies" not in текст
