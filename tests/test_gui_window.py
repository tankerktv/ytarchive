"""Проверки главного окна: пересборка на новом языке.

Смена языка сделана пересборкой окна, а не переписыванием подписей по одной.
Переписывание неизбежно что-нибудь пропускает, и пропущенное молча остаётся
на прежнем языке. Здесь и сторожится главное свойство пересборки — что после
неё на прежнем языке не осталось ничего.

Окно строится вхолостую (offscreen) на пустом каталоге: ни сети, ни выкачки.
"""

import os

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("PySide6", reason="окно проверяется только там, где есть Qt")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from gui.source import ArchiveSource  # noqa: E402
from runner.language import настроить  # noqa: E402


@pytest.fixture(scope="module")
def приложение():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def окно(приложение, tmp_path):
    """Окно на пустом каталоге. Фоновую работу не заводим: она полезла бы
    в сеть за логотипами."""
    from gui.window import Window

    (tmp_path / "_tools").mkdir()
    (tmp_path / "ytarchive.toml").write_text(
        f'[paths]\nbase = "{tmp_path.as_posix()}"\n[interface]\nlanguage = "ru"\n',
        encoding="utf-8",
    )
    источник = ArchiveSource(
        base=tmp_path,
        archive_path=tmp_path / "_tools" / "downloaded.txt",
        logs_dir=tmp_path / "_logs",
        lock_path=tmp_path / "_tools" / "ytarchive.lock",
        channels_path=tmp_path / "_tools" / "channels.txt",
        config_path=tmp_path / "ytarchive.toml",
        live_path=tmp_path / "_tools" / "live.json",
    )
    настроить("ru")
    двери = Window(источник, фоновые=False)
    yield двери
    двери._дождаться_потоков()
    двери.трей.hide()
    настроить("ru")


def вкладки(двери) -> list[str]:
    return [двери.вкладки.tabText(i) for i in range(двери.вкладки.count())]


def test_окно_строится_по_русски(окно):
    assert вкладки(окно) == ["Обзор", "Каналы", "Библиотека", "Настройки"]


def test_язык_меняется_без_перезапуска(окно):
    """Ради этого пересборка и написана: программа не перезапускается,
    меняется только нутро окна.
    """
    настроить("en")
    окно.перестроить()

    assert вкладки(окно) == ["Overview", "Channels", "Library", "Settings"]
    assert окно.windowTitle() == "YouTube Archive"


def test_после_пересборки_не_осталось_прежнего_языка(окно):
    """Главная беда переписывания подписей — забытый виджет. Проверяем не
    отдельные надписи, а что кириллицы в окне не осталось вовсе.
    """
    from PySide6.QtWidgets import QAbstractButton, QLabel

    настроить("de")
    окно.перестроить()

    подписи = [
        в.text()
        for вид in (QLabel, QAbstractButton)
        for в in окно.findChildren(вид)
        if в.text().strip()
    ]
    кириллица = [т for т in подписи if any("а" <= с.lower() <= "я" for с in т)]
    assert not кириллица, f"остались надписи на прежнем языке: {кириллица[:5]}"


def test_выбранная_вкладка_переживает_пересборку(окно):
    # Иначе смена языка выбрасывала бы человека на первую вкладку.
    окно.вкладки.setCurrentIndex(2)
    настроить("es")
    окно.перестроить()

    assert окно.вкладки.currentIndex() == 2


def test_меню_трея_тоже_пересобирается(окно):
    """Забыть про трей легко: он не на виду. И тогда программа наполовину
    говорит на новом языке, наполовину на старом.
    """
    настроить("fr")
    окно.перестроить()

    пункты = [д.text() for д in окно.трей.contextMenu().actions() if д.text()]
    assert "Afficher la fenêtre" in пункты
    assert "Quitter" in пункты


def test_окно_узнаёт_об_остановке_из_снимка_а_не_из_журнала(окно, tmp_path):
    """Ради этой развязки всё и делалось: журнал переводится, а окно должно
    понимать состояние независимо от того, на каком языке он написан.
    """
    import json

    (tmp_path / "_tools" / "live.json").write_text(
        json.dumps({"stopped_reason": "нужен вход в аккаунт YouTube", "errors": 2}),
        encoding="utf-8",
    )
    окно.обновить()

    assert "вход в аккаунт" in окно.заголовок.text()


def test_журнал_на_чужом_языке_не_сбивает_окно(окно, tmp_path):
    """Раньше окно искало в журнале «остановлено — ». Английский журнал
    оставил бы его в неведении — молча.
    """
    журналы = tmp_path / "_logs"
    журналы.mkdir(exist_ok=True)
    (журналы / "2026-09-03_1200.log").write_text(
        "12:00:00  SoyuzUS: stopped — sign-in required\n", encoding="utf-8"
    )
    окно.обновить()

    # Ничего не выдумываем: снимка нет, значит про остановку мы не знаем.
    assert "нужен человек" not in окно.заголовок.text()
