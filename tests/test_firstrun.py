"""Проверки разговора при первом запуске.

Это первое, что видит человек, скачавший программу. Ошибка здесь не в том,
что он увидит кривую надпись, а в том, что он не увидит ничего работающего
и уйдёт.
"""

import os

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("PySide6", reason="мастер проверяется только там, где есть Qt")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.config import loads, parse_config  # noqa: E402
from gui.firstrun import ОкноПервогоЗапуска, настройки_для  # noqa: E402
from runner.language import настроить  # noqa: E402


@pytest.fixture(scope="module")
def приложение():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def мастер(приложение):
    настроить("ru")
    окно = ОкноПервогоЗапуска()
    yield окно
    окно.deleteLater()
    настроить("ru")


# --- что записывается --------------------------------------------------------


def test_настройки_разбираются(tmp_path):
    """Написать негодные настройки значит встретить человека отказом
    сразу после разговора, в котором он всё сделал правильно.
    """
    config = parse_config(loads(настройки_для(tmp_path, "ru")))
    assert config.paths.base == tmp_path.as_posix()
    assert config.language == "ru"


def test_выбранный_язык_попадает_в_настройки(tmp_path):
    assert parse_config(loads(настройки_для(tmp_path, "de"))).language == "de"


def test_системный_язык_тоже_годится(tmp_path):
    # «Взять у системы» — законный ответ, а не отсутствие ответа.
    assert parse_config(loads(настройки_для(tmp_path, "system"))).language == "system"


def test_путь_записывается_в_переносимом_виде(tmp_path):
    r"""Обратные слэши Windows в TOML — знак экранирования. Незакавыченный
    `C:\Users` превратился бы при чтении в мусор, и молча.
    """
    текст = настройки_для(tmp_path, "ru")
    assert "\\\\" not in текст or "/" in parse_config(loads(текст)).paths.base


# --- сам разговор ------------------------------------------------------------


def test_без_папки_готово_недоступно(мастер):
    """Согласиться, не выбрав папку, — значит записать настройки, по которым
    качать некуда.
    """
    assert not мастер.кнопка_готово.isEnabled()


def test_спрашиваем_ровно_то_чего_не_угадать(мастер):
    """Язык и папка. Всё остальное имеет разумные умолчания, и спрашивать
    про паузы человека, который ещё ничего не скачал, незачем.
    """
    assert мастер.поле_язык is not None
    assert мастер.поле_папка is not None
    assert мастер.поле_папка.text() == ""


def test_язык_меняется_прямо_в_разговоре(мастер):
    """Человек с чужим языком системы должен суметь прочитать этот же экран,
    а не гадать, что от него хотят.
    """
    место = мастер.поле_язык.findData("de")
    assert место > 0
    мастер.поле_язык.setCurrentIndex(место)

    assert мастер.язык == "de"
    assert мастер.windowTitle() == "YouTube-Archiv — erster Start"
    assert мастер.кнопка_готово.text() == "Fertig"


def test_после_смены_языка_прежнее_нутро_не_копится(мастер):
    """Та же беда, что в главном окне: само оно не удаляется, а остаётся
    ребёнком — и накапливается на каждой смене.
    """
    from PySide6.QtWidgets import QLabel

    было = len(мастер.findChildren(QLabel))
    for код in ("de", "es", "fr", "en"):
        мастер.поле_язык.setCurrentIndex(мастер.поле_язык.findData(код))
        QApplication.processEvents()

    стало = len(мастер.findChildren(QLabel))
    assert стало <= было, f"нутро копится: было {было}, стало {стало}"


def test_негодная_папка_не_принимается(мастер, tmp_path):
    """Несуществующую папку принять — значит согласиться на архив, которого
    не будет.
    """
    from gui.source import осмотреть_папку

    осмотр = осмотреть_папку(tmp_path / "нет-такой", учёт="_tools/downloaded.txt")
    assert not осмотр.ok
    assert мастер.папка is None


# --- склейка с запуском окна -------------------------------------------------


def test_после_разговора_настройки_на_месте(приложение, tmp_path, monkeypatch, capsys):
    """Разговор без записи — это разговор впустую: следующий запуск снова
    спросит то же самое.
    """
    import app.main as app_main
    import gui.firstrun as мастер_модуль

    папка = tmp_path / "Архив"
    monkeypatch.setattr(мастер_модуль, "спросить", lambda parent=None: (папка, "ru"))
    настройки = tmp_path / "ytarchive.toml"

    assert app_main.первый_запуск(настройки) == 0
    assert настройки.exists()
    assert папка.is_dir(), "папку надо создать, а не только записать её имя"

    config, _ = app_main.load_config(настройки)
    assert config.paths.base == папка.as_posix()
    assert config.language == "ru"


def test_отказ_не_считается_бедой(приложение, tmp_path, monkeypatch, capsys):
    """Передумать — право человека. Ненулевой код тут означал бы поломку
    в любом скрипте, который зовёт программу.
    """
    import app.main as app_main
    import gui.firstrun as мастер_модуль

    monkeypatch.setattr(мастер_модуль, "спросить", lambda parent=None: None)
    настройки = tmp_path / "ytarchive.toml"

    assert app_main.первый_запуск(настройки) == 0
    assert not настройки.exists()
