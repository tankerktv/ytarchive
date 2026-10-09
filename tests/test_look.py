"""Проверки нового вида окна и того, что за ним стоит в ядре.

Красоту проверить нельзя, а смысл — можно: что дата не врёт о своей точности,
что окно не говорит «не запущена» про работающий обход и что из двух кнопок
видна та, что сейчас имеет смысл.
"""

import json
import os

import pytest

from core.status import Hint, RunState, build_status, next_hint, size_parts
from core.videos import ПРИМЕРНО, date_from_filename, date_text, title_from_filename

# --- дата ролика -------------------------------------------------------------


def test_точная_дата_показывается_днём():
    assert date_text("20240411", exact=True) == "2024-04-11"


@pytest.mark.parametrize(
    "дата, ожидаем",
    [
        ("20261006", "≈ 2026-10-06"),  # три дня назад — «3 дня назад» точно до дня
        ("20260301", "≈ 2026-03"),  # «7 месяцев назад» — точно до месяца
        ("20230101", "≈ 2023"),  # «3 года назад» — точно до года
    ],
)
def test_примерная_дата_показывается_с_той_точностью_какую_имеет(дата, ожидаем):
    """YouTube в списке канала пишет «3 года назад». Показать такое с точностью
    до дня значит соврать — и человек отсечёт правилом не те ролики."""
    assert date_text(дата, exact=False, today="20261009") == ожидаем


def test_примерная_дата_всегда_помечена():
    for дата in ("20261006", "20260301", "20230101"):
        assert date_text(дата, exact=False, today="20261009").startswith(ПРИМЕРНО)
    assert not date_text("20261006", exact=True).startswith(ПРИМЕРНО)


@pytest.mark.parametrize("дата", ["", "NA", "2024", "2024041x"])
def test_неизвестная_дата_это_прочерк(дата):
    assert date_text(дата, exact=False, today="20261009") == "—"
    assert date_text(дата, exact=True) == "—"


def test_без_сегодняшнего_дня_примерная_дата_до_года():
    assert date_text("20261006", exact=False) == "≈ 2026"


def test_точная_дата_берётся_из_имени_скачанного_файла():
    assert date_from_filename("2024-04-11 - BMW E87 [oxd5IAl-o3Q].mkv") == ("oxd5IAl-o3Q", "20240411")


@pytest.mark.parametrize(
    "имя",
    [
        "2024-04-11 - BMW E87 [oxd5IAl-o3Q].f299.mp4.part",  # обломок — ролик не скачан
        "BMW E87 [oxd5IAl-o3Q].mkv",  # без даты
        "2024-04-11 - без идентификатора.mkv",
    ],
)
def test_из_чужого_имени_дата_не_выдумывается(имя):
    assert date_from_filename(имя) is None


@pytest.mark.parametrize(
    "имя, название",
    [
        ("2024-04-11 - BMW E87 - МЕЧТА [oxd5IAl-o3Q].f299.mp4", "BMW E87 - МЕЧТА"),
        ("2024-04-11 - Название [oxd5IAl-o3Q].mkv", "Название"),
        ("Название [в скобках] [oxd5IAl-o3Q].webm", "Название [в скобках]"),
        ("без расширения", "без расширения"),
    ],
)
def test_название_качаемого_ролика_без_служебного(имя, название):
    assert title_from_filename(имя) == название


# --- состояние ---------------------------------------------------------------


def test_живой_обход_между_проходами_не_называется_незапущенным():
    """Настоящий случай: окно писало «не запущена», а рядом — «обход работает».
    Человек, видя первое, шёл нажимать «Запустить»."""
    assert build_status(process_running=False, worker_running=True).state is RunState.WAITING
    assert build_status(process_running=False, worker_running=False).state is RunState.IDLE


def test_ждущий_обход_не_считается_качающим():
    """Иначе окно показывало бы полосы загрузки, которой нет."""
    assert not RunState.WAITING.is_working


def test_беда_перевешивает_ожидание():
    from core.livestate import LiveState

    снимок = build_status(
        process_running=False, worker_running=True, live=LiveState(stopped_reason="истекли куки")
    )
    assert снимок.state is RunState.NEEDS_HUMAN


def test_заголовок_окна_короткий_и_с_заглавной():
    from core.livestate import LiveState

    снимок = build_status(process_running=True, live=LiveState(file_name="2024 - Ролик [aaaaaaaaaaa].mkv"))
    assert снимок.title() == "Качает", "имя файла показано рядом, в заголовке ему не место"


def test_причина_беды_в_заголовке_переведена():
    """Причина хранится по-русски как ключ. Без перевода английское окно
    говорило бы «stopped, needs you: нужен вход в аккаунт»."""
    from core.livestate import LiveState

    снимок = build_status(process_running=False, live=LiveState(stopped_reason="истекли куки"))
    перевод = {"истекли куки": "cookies expired", RunState.NEEDS_HUMAN.value: "stopped"}.get
    assert снимок.title(lambda строка: перевод(строка, строка)) == "Stopped: cookies expired"
    assert снимок.headline(lambda строка: перевод(строка, строка)) == "stopped: cookies expired"


# --- подсказка новичку -------------------------------------------------------


def test_сначала_каналы_потом_куки():
    """Одна подсказка за раз и в порядке, в котором это делают."""
    assert next_hint(channels=0, has_cookies=False) is Hint.NO_CHANNELS
    assert next_hint(channels=2, has_cookies=False) is Hint.NO_COOKIES


def test_у_обжитой_программы_подсказок_нет():
    """Подсказка, висящая у работающей программы, превращается в шум."""
    assert next_hint(channels=5, has_cookies=True) is None


# --- объём -------------------------------------------------------------------


def test_большой_объём_в_терабайтах():
    """«1331,2 ГБ» читается хуже, чем «1,30 ТБ»."""
    assert size_parts(1331.2 * 1024**3) == (pytest.approx(1.3), "tb")
    assert size_parts(512 * 1024**3) == (512.0, "gb")
    assert size_parts(1024**4)[1] == "tb"


# --- окно --------------------------------------------------------------------

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
    двери.show()
    yield двери
    двери._дождаться_потоков()
    двери.трей.hide()
    двери.hide()
    настроить("ru")


@pytest.mark.slow
def test_пустой_программе_подсказывают_добавить_канал(окно):
    assert окно.карта_подсказки.isVisible()
    assert "Каналов пока нет" in окно.текст_подсказки.text()
    окно._по_подсказке()
    assert окно.вкладки.currentIndex() == 1, "кнопка подсказки ведёт туда, где она исполняется"


@pytest.mark.slow
def test_подсказка_сменяется_и_уходит_сама(окно, tmp_path):
    """Человек кладёт файл, глядя на подсказку, — она должна исчезнуть без
    перезапуска окна."""
    (tmp_path / "_tools" / "channels.txt").write_text(
        "Канал|https://www.youtube.com/@x/videos\n", encoding="utf-8"
    )
    окно._перечитать_каналы()
    окно.обновить()
    assert "без входа" in окно.текст_подсказки.text()

    (tmp_path / "_tools" / "cookies.txt").write_text("x", encoding="utf-8")
    окно.обновить()
    assert not окно.карта_подсказки.isVisible()


@pytest.mark.slow
def test_видна_одна_кнопка_та_что_имеет_смысл(окно):
    """Две кнопки рядом, из которых одна всегда серая, заставляли каждый раз
    читать обе."""
    окно.source.worker_running = lambda: False
    окно.обновить()
    assert окно.кнопка_пуск.isVisible() and not окно.кнопка_стоп.isVisible()

    окно.source.worker_running = lambda: True
    окно.обновить()
    assert окно.кнопка_стоп.isVisible() and not окно.кнопка_пуск.isVisible()
    assert окно.заголовок.text() == "Ждёт следующего прохода"


@pytest.mark.slow
def test_полосы_спрятаны_пока_нечего_показывать(окно, tmp_path):
    окно.обновить()
    assert not окно.карта_сейчас.isVisible()

    окно.source.download_running = lambda: True
    (tmp_path / "_tools" / "live.json").write_text(
        json.dumps({
            "file_name": "2024-04-11 - BMW E87 [oxd5IAl-o3Q].f299.mp4",
            "percent": 62.0, "item_index": 3, "item_total": 10, "channel": "К",
        }),
        encoding="utf-8",
    )
    окно.обновить()
    assert окно.карта_сейчас.isVisible()
    assert окно.подпись_файла.text().startswith("BMW E87 · 62%"), "название без даты и идентификатора"


@pytest.mark.slow
def test_папка_не_из_списка_называется_словами(окно, tmp_path):
    """Так выглядел расколотый архив: рядом с `SoyuzUS` молча вырос `Soyuz`.
    Таблицы папок в окне больше нет — значит, сказать об этом надо иначе."""
    (tmp_path / "_tools" / "channels.txt").write_text(
        "SoyuzUS|https://www.youtube.com/@x/videos\n", encoding="utf-8"
    )
    for папка in ("SoyuzUS", "Soyuz"):
        (tmp_path / папка).mkdir()
        (tmp_path / папка / "2024-01-01 - Ролик [aaaaaaaaaaa].mkv").write_text("x", encoding="utf-8")
    окно._перечитать_каналы()
    окно.обновить()
    # Не isVisible: надпись лежит на вкладке «Каналы», а открыта «Обзор».
    assert not окно.чужие_папки.isHidden()
    assert "Soyuz" in окно.чужие_папки.text() and "SoyuzUS" not in окно.чужие_папки.text()


@pytest.mark.slow
def test_журнал_прячется_и_возвращается(окно):
    assert окно.журнал.isVisible()
    окно._переключить_журнал()
    assert not окно.журнал.isVisible() and окно.кнопка_журнал.text() == "Показать"
    окно._переключить_журнал()
    assert окно.журнал.isVisible() and окно.кнопка_журнал.text() == "Скрыть"


@pytest.mark.slow
def test_точные_даты_скачанных_читаются_с_диска(окно, tmp_path):
    канал = tmp_path / "Канал"
    канал.mkdir()
    (канал / "2024-04-11 - BMW E87 [oxd5IAl-o3Q].mkv").write_text("x", encoding="utf-8")
    (канал / "2025-01-01 - Обломок [aaaaaaaaaaa].f299.mp4.part").write_text("x", encoding="utf-8")
    assert окно.source.file_dates("Канал") == {"oxd5IAl-o3Q": "20240411"}
    assert окно.source.file_dates("нет такой папки") == {}


@pytest.mark.slow
def test_в_окне_роликов_дата_точная_у_скачанных_и_примерная_у_остальных(приложение, tmp_path):
    from core.videos import Listing, Video
    from gui.videos import СТОЛБЕЦ_ДАТА, СТОЛБЕЦ_СОСТОЯНИЕ, ОкноРоликов

    (tmp_path / "_tools").mkdir()
    (tmp_path / "Канал").mkdir()
    (tmp_path / "Канал" / "2024-04-11 - Первый [aaaaaaaaaaa].mkv").write_text("x", encoding="utf-8")
    (tmp_path / "_tools" / "downloaded.txt").write_text("youtube aaaaaaaaaaa\n", encoding="utf-8")
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
    двери = ОкноРоликов(источник, "Канал", фоновые=False)
    двери._перепись_готова(Listing(videos=(
        # В переписи дата примерная и отличается от настоящей на два дня.
        Video("aaaaaaaaaaa", "Первый", 600, "20240409"),
        Video("bbbbbbbbbbb", "Второй", 600, "20190101"),
        Video("ccccccccccc", "Третий", 600, ""),
    )))
    даты = [двери.таблица.item(строка, СТОЛБЕЦ_ДАТА).text() for строка in range(3)]
    assert даты == ["2024-04-11", "≈ 2019", "—"], "у скачанного — дата с диска, а не из переписи"
    assert двери.таблица.item(1, СТОЛБЕЦ_ДАТА).toolTip(), "примерная дата объяснена"
    assert двери.таблица.item(0, СТОЛБЕЦ_СОСТОЯНИЕ).text() == "скачан"

    двери.таблица.selectRow(0)
    assert "2024-04-11" in двери.подпись.text()
    двери._дождаться_потоков()
