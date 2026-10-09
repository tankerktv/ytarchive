"""Одно окно на один архив.

Настоящий случай: закрытое окно прячется в трей, человек открывает ярлык
снова — и на машине автора нашлось три окна программы разом.
"""

import os

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("PySide6", reason="окно проверяется только там, где есть Qt")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# QtNetwork на Linux тянет системную библиотеку Kerberos; где её нет, защиты
# от второго окна нет вовсе, и проверять нечего.
pytest.importorskip("PySide6.QtNetwork", exc_type=ImportError, reason="нет QtNetwork или его системных библиотек")

from PySide6.QtWidgets import QApplication  # noqa: E402

from gui.single import имя_соединения, попросить_показаться, слушать  # noqa: E402


@pytest.fixture(scope="module")
def приложение():
    return QApplication.instance() or QApplication([])


def test_имя_одно_для_одних_настроек_и_разное_для_разных(tmp_path):
    первые = tmp_path / "a" / "ytarchive.toml"
    вторые = tmp_path / "b" / "ytarchive.toml"
    assert имя_соединения(первые) == имя_соединения(tmp_path / "a" / "." / "ytarchive.toml")
    assert имя_соединения(первые) != имя_соединения(вторые), "окна разных архивов друг другу не мешают"


def test_когда_окна_нет_просить_некого(приложение, tmp_path):
    assert попросить_показаться(имя_соединения(tmp_path / "никого.toml")) is False


def test_второй_запуск_просит_первое_окно_показаться(приложение, tmp_path):
    имя = имя_соединения(tmp_path / "ytarchive.toml")
    показов = []
    сервер = слушать(имя, lambda: показов.append(1))
    assert сервер is not None
    try:
        assert попросить_показаться(имя) is True
        приложение.processEvents()
        assert показов == [1], "первое окно получило просьбу"
    finally:
        сервер.close()


def test_след_упавшего_окна_не_мешает_открыться(приложение, tmp_path):
    """На Linux и macOS соединение — файл, и после аварийного выхода он
    остаётся. Новое окно обязано открыться поверх следа."""
    имя = имя_соединения(tmp_path / "ytarchive.toml")
    первый = слушать(имя, lambda: None)
    assert первый is not None
    первый.close()
    второй = слушать(имя, lambda: None)
    assert второй is not None
    второй.close()
