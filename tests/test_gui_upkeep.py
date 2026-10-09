"""Проверки того, что окно получило в этой версии: новые настройки,
правила канала, добавление по адресу и сообщение о беде.

Окно строится вхолостую (offscreen) на пустом каталоге: ни сети, ни выкачки.
"""

import json
import os

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("PySide6", reason="окно проверяется только там, где есть Qt")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.channels import parse_channels  # noqa: E402
from core.config import loads, parse_config  # noqa: E402
from core.rules import Rules  # noqa: E402
from core.schedule import Hours  # noqa: E402
from core.status import is_new_trouble  # noqa: E402
from gui.source import ArchiveSource  # noqa: E402
from runner.language import настроить  # noqa: E402


@pytest.fixture(scope="module")
def приложение():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def окно(приложение, tmp_path):
    from gui.window import Window

    (tmp_path / "_tools").mkdir()
    (tmp_path / "ytarchive.toml").write_text(
        f'[paths]\nbase = "{tmp_path.as_posix()}"\n[interface]\nlanguage = "ru"\n',
        encoding="utf-8",
    )
    (tmp_path / "_tools" / "channels.txt").write_text(
        "Канал|https://www.youtube.com/@x/videos\n", encoding="utf-8"
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


def настройки(двери):
    return parse_config(loads(двери.source.config_text()))


# --- настройки ---------------------------------------------------------------


def test_новые_настройки_сохраняются_из_окна(окно):
    окно.поле_куки.setCurrentIndex(окно.поле_куки.findData("firefox"))
    окно.поле_скорость.setValue(2048)
    окно.поле_ползёт.setValue(50)
    окно.поле_часы.setText("23-7")
    окно._сохранить_настройки()

    config = настройки(окно)
    assert config.cookies_browser == "firefox"
    assert config.rate_limit == 2048
    assert config.limits.crawl_speed == 50
    assert config.hours == Hours(23 * 60, 7 * 60)


def test_сохранение_прочего_не_сбрасывает_новые_настройки(окно):
    """Окно пишет файл целиком. Забудь оно про поле, которого не показывает,
    настройка молча вернулась бы к умолчанию при первом же сохранении."""
    путь = окно.source.config_path
    путь.write_text(
        путь.read_text(encoding="utf-8")
        + '[limits]\ncrawl_minutes = 25\nkeep_logs_days = 7\n',
        encoding="utf-8",
    )
    окно._перечитать_настройки()
    окно.поле_av1.setChecked(False)
    окно._сохранить_настройки()

    config = настройки(окно)
    assert config.limits.crawl_minutes == 25 and config.limits.keep_logs_days == 7


def test_непонятные_часы_не_сохраняются(окно, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    окно.поле_часы.setText("ночью")
    окно._сохранить_настройки()
    assert настройки(окно).hours is None
    assert окно.настройки_ответ.text() == "не сохранено"


def test_потолок_ниже_порога_ползания_не_сохраняется(окно, monkeypatch):
    """Иначе выкачка снимала бы сама себя; отказ должен случиться в окне,
    а не ночью."""
    from PySide6.QtWidgets import QMessageBox

    сказано = []
    monkeypatch.setattr(QMessageBox, "warning", lambda _окно, _заголовок, текст: сказано.append(текст))
    окно.поле_скорость.setValue(120)
    окно.поле_ползёт.setValue(100)
    окно._сохранить_настройки()
    assert настройки(окно).rate_limit == 0
    assert сказано and "crawl_speed" in сказано[0]


# --- правила и добавление ----------------------------------------------------


def test_правила_записываются_в_список(окно):
    ответ = окно.source.set_rules(0, Rules(min_seconds=60, after="20240101"))
    assert ответ.ok
    канал = parse_channels(окно.source.channels_text()).channels[0]
    assert канал.rules == Rules(min_seconds=60, after="20240101")


def test_правило_видно_в_списке_каналов(окно):
    """Правило невидимо, пока не откроешь окно; без пометки человек будет
    гадать, почему у канала качается не всё."""
    окно.source.set_rules(0, Rules(max_seconds=600))
    окно._перечитать_каналы()
    ячейка = окно.список_каналов.item(0, 1)
    assert "⚙" in ячейка.text() and "max=600" in ячейка.toolTip()


def test_окно_правил_собирает_то_же_что_понимает_файл(приложение):
    from gui.upkeep import ОкноПравил

    окно_правил = ОкноПравил("Канал", Rules())
    окно_правил.поле_мин.setValue(90)
    окно_правил.поле_дата.setText("2024-06-01")
    assert окно_правил.собрать() == Rules(min_seconds=90, after="20240601")


def test_окно_правил_не_принимает_кривую_дату(приложение):
    from gui.upkeep import ОкноПравил

    окно_правил = ОкноПравил("Канал", Rules())
    окно_правил.поле_дата.setText("01.06.2024")
    окно_правил._принять()
    assert окно_правил.ответ.text(), "причина отказа показана"
    assert окно_правил.правила == Rules()


def test_плейлист_добавляется_по_адресу(окно):
    адрес = "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    окно.source.add_channel("Подборка", адрес)
    каналы = parse_channels(окно.source.channels_text()).channels
    assert [к.url for к in каналы][-1] == адрес


@pytest.mark.parametrize(
    "имя, адрес",
    [("Имя: с двоеточием", "https://youtu.be/rbYUHA9ZOg8"), ("Имя", "youtu.be/rbYUHA9ZOg8")],
)
def test_негодная_строка_не_портит_список(окно, имя, адрес):
    """Запиши мы её — файл получил бы «непонятую строку», и окно отказалось
    бы править список вовсе."""
    ответ = окно.source.add_channel(имя, адрес)
    разбор = parse_channels(окно.source.channels_text())
    assert "не добавлен" in ответ
    assert not разбор.problems and len(разбор.channels) == 1


# --- сообщение о беде --------------------------------------------------------


def test_о_новой_беде_говорим_о_прежней_молчим():
    assert is_new_trouble("", "истекли куки")
    assert not is_new_trouble("истекли куки", "истекли куки")
    assert is_new_trouble("истекли куки", "не найден node")
    assert not is_new_trouble("истекли куки", "")


def test_окно_говорит_о_беде_один_раз(окно, tmp_path):
    """Окно обновляется каждые две секунды. Повторяй оно сообщение с той же
    частотой, человек научился бы закрывать их не читая."""
    сказано = []
    окно.трей.showMessage = lambda *доводы: сказано.append(доводы[1])

    (tmp_path / "_tools" / "live.json").write_text(
        json.dumps({"stopped_reason": "нужен вход в аккаунт YouTube — куки истекли или их нет"}),
        encoding="utf-8",
    )
    окно.обновить()
    окно.обновить()
    assert len(сказано) == 1 and "куки" in сказано[0]

    (tmp_path / "_tools" / "live.json").write_text(json.dumps({"stopped_reason": ""}), encoding="utf-8")
    окно.обновить()
    (tmp_path / "_tools" / "live.json").write_text(
        json.dumps({"stopped_reason": "нужен вход в аккаунт YouTube — куки истекли или их нет"}),
        encoding="utf-8",
    )
    окно.обновить()
    assert len(сказано) == 2, "беда прошла и вернулась — это новая беда"
