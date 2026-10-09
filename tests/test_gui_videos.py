"""Проверки окна выбора роликов.

Окно строится вхолостую (offscreen), с поддельным источником: ни сети,
ни файлов, ни экрана. Проверяется не рисование, а то, чем окно может
навредить, — что оно запишет в общий файл выбора.

Сюда же вынесена ловушка поиска: «снять показанные» при непустом запросе
обязано касаться только показанного. Ошибись здесь — и человек, искавший
«стрим», лишится всего канала одним нажатием.
"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("PySide6", reason="окно проверяется только там, где есть Qt")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core.exclusions import Exclusions, parse_exclusions  # noqa: E402
from gui.source import Записано  # noqa: E402
from core.videos import Listing, Video  # noqa: E402
from gui.videos import ОкноРоликов  # noqa: E402

ПЕРЕПИСЬ = Listing(
    videos=(
        Video("aaaaaaaaaaa", "Первый про железо", 2796),
        Video("bbbbbbbbbbb", "Второй про стримы", 600),
        Video("ccccccccccc", "Третий про стримы", 900),
    )
)


class ПоддельныйИсточник:
    """Всё, что окно спрашивает у мира, — и ничего больше."""

    def __init__(self, tmp_path, исключения: str = "", архив: str = ""):
        self.thumbs_dir = tmp_path / "thumbs"
        self._исключения = исключения
        self._архив = архив
        self.записано = None

    def archive_text(self) -> str:
        return self._архив

    def exclusions(self) -> Exclusions:
        return parse_exclusions(self._исключения)

    def write_exclusions(self, video_ids):
        self.записано = set(video_ids)
        return Записано(True, "выбор сохранён")

    def listing(self, channel_name, should_stop=None):
        return ПЕРЕПИСЬ

    def file_dates(self, channel_name):
        return {"aaaaaaaaaaa": "20240411"}


@pytest.fixture(scope="module")
def приложение():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def окно(приложение, tmp_path):
    источник = ПоддельныйИсточник(tmp_path)
    окно = ОкноРоликов(источник, "канал", фоновые=False)
    окно._перепись_готова(ПЕРЕПИСЬ)
    yield окно, источник
    окно._дождаться_потоков()


def test_по_умолчанию_отмечено_всё(окно):
    """Иначе архив пришлось бы набирать галочками с нуля."""
    двери, _ = окно
    assert двери.таблица.rowCount() == 3
    for строка in range(3):
        assert двери.таблица.item(строка, 0).checkState() == Qt.CheckState.Checked


def test_снятая_галочка_попадает_в_запись(окно):
    двери, источник = окно
    двери.таблица.item(0, 0).setCheckState(Qt.CheckState.Unchecked)
    двери._сохранить()

    assert источник.записано == {"aaaaaaaaaaa"}


def test_снять_показанные_не_трогает_спрятанное_поиском(окно):
    """Ловушка поиска: человек ищет «стрим», жмёт «снять» — и не должен
    лишиться роликов, которых в этот момент не видел.
    """
    двери, источник = окно
    двери.поиск.setText("стрим")
    двери._всем_галочку(False)
    двери.поиск.setText("")
    двери._сохранить()

    assert источник.записано == {"bbbbbbbbbbb", "ccccccccccc"}


def test_выбор_чужого_канала_переживает_запись(приложение, tmp_path):
    """Файл общий на все каналы. Записав только увиденное, окно стёрло бы
    выбор по остальным — молча.
    """
    источник = ПоддельныйИсточник(tmp_path, исключения="zzzzzzzzzzz\n")
    двери = ОкноРоликов(источник, "канал", фоновые=False)
    двери._перепись_готова(ПЕРЕПИСЬ)
    двери.таблица.item(0, 0).setCheckState(Qt.CheckState.Unchecked)
    двери._сохранить()
    двери._дождаться_потоков()

    assert источник.записано == {"zzzzzzzzzzz", "aaaaaaaaaaa"}


def test_снятое_ранее_показано_снятым(приложение, tmp_path):
    источник = ПоддельныйИсточник(tmp_path, исключения="bbbbbbbbbbb\n")
    двери = ОкноРоликов(источник, "канал", фоновые=False)
    двери._перепись_готова(ПЕРЕПИСЬ)

    assert двери.таблица.item(1, 0).checkState() == Qt.CheckState.Unchecked
    assert двери.таблица.item(1, 5).text() == "снят"
    двери._дождаться_потоков()


def test_скачанное_видно_в_списке(приложение, tmp_path):
    """Иначе снятие галочки выглядит как удаление уже скачанного."""
    источник = ПоддельныйИсточник(tmp_path, архив="youtube aaaaaaaaaaa\n")
    двери = ОкноРоликов(источник, "канал", фоновые=False)
    двери._перепись_готова(ПЕРЕПИСЬ)

    assert двери.таблица.item(0, 5).text() == "скачан"
    двери._дождаться_потоков()


# --- закрытие окна во время работы ------------------------------------------

#: Проверяется отдельным запуском, и иначе никак: Qt на живом потоке в момент
#: разрушения окна не бросает исключение, а обрывает процесс — без сообщения
#: и без кода возврата. Внутри своего же процесса это не поймать.
СЦЕНАРИЙ = textwrap.dedent(
    """
    import sys, time, pathlib
    from PySide6.QtWidgets import QApplication
    from core.exclusions import Exclusions
    from core.videos import Listing, Video

    app = QApplication(sys.argv)
    слышит = sys.argv[2] == 'уступчивый'

    class Источник:
        def __init__(self, tmp):
            self.thumbs_dir = pathlib.Path(tmp) / 'thumbs'
        def archive_text(self): return ''
        def exclusions(self): return Exclusions()
        def write_exclusions(self, ids): return 'выбор сохранён'
        def file_dates(self, name): return {}
        def listing(self, name, should_stop=None):
            # Глухой не слышит просьбы прекратить — как urlopen с таймаутом.
            for _ in range(40):
                if слышит and should_stop and should_stop():
                    break
                time.sleep(0.2)
            return Listing(videos=(Video('aaaaaaaaaaa', 'ролик', 60),))

    from gui.videos import ОкноРоликов, дождаться_доживающих
    окно = ОкноРоликов(Источник(sys.argv[1]), 'канал')
    окно.show()
    app.processEvents()
    time.sleep(0.5)
    окно.close()
    окно.deleteLater()
    app.processEvents()
    дождаться_доживающих()
    """
)


@pytest.mark.parametrize("поведение", ["уступчивый", "глухой"])
def test_закрытие_во_время_переписи_не_обрывает_программу(tmp_path, поведение):
    """Настоящий случай 02.09: окно, открытое человеком, ушло с кодом 127
    без единой строки вывода. Перепись ещё шла, а Qt разрушал окно.

    Проверяются оба исхода: работа, услышавшая просьбу прекратить, и та,
    что не слышит, — вторую нельзя бросать, её надо дожидаться.
    """
    сценарий = tmp_path / "закрытие.py"
    сценарий.write_text(СЦЕНАРИЙ, encoding="utf-8")

    окружение = dict(os.environ)
    окружение["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    окружение["QT_QPA_PLATFORM"] = "offscreen"

    итог = subprocess.run(
        [sys.executable, str(сценарий), str(tmp_path), поведение],
        capture_output=True,
        text=True,
        timeout=120,
        env=окружение,
    )
    assert итог.returncode == 0, (
        f"процесс оборвался ({итог.returncode}) — живой поток при разрушении окна;"
        f" вывод: {итог.stderr[-400:]!r}"
    )


def test_неудавшаяся_перепись_не_даёт_сохранить(приложение, tmp_path):
    """Пустой список — это «не смогли посмотреть», а не «снято всё».
    Дай тут сохранить — и выбор по каналу будет стёрт подчистую.
    """
    источник = ПоддельныйИсточник(tmp_path, исключения="bbbbbbbbbbb\n")
    двери = ОкноРоликов(источник, "канал", фоновые=False)
    двери._перепись_готова(Listing())

    assert not двери.кнопка_сохранить.isEnabled()
    assert источник.записано is None
    двери._дождаться_потоков()
