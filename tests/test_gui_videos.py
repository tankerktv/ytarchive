"""Проверки окна выбора роликов.

Окно строится вхолостую (offscreen), с поддельным источником: ни сети,
ни файлов, ни экрана. Проверяется не рисование, а то, чем окно может
навредить, — что оно запишет в общий файл выбора.

Сюда же вынесена ловушка поиска: «снять показанные» при непустом запросе
обязано касаться только показанного. Ошибись здесь — и человек, искавший
«стрим», лишится всего канала одним нажатием.
"""

import os

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("PySide6", reason="окно проверяется только там, где есть Qt")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core.exclusions import Exclusions, parse_exclusions  # noqa: E402
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

    def write_exclusions(self, video_ids) -> str:
        self.записано = set(video_ids)
        return "выбор сохранён"

    def listing(self, channel_name):
        return ПЕРЕПИСЬ


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
    assert двери.таблица.item(1, 4).text() == "снят"
    двери._дождаться_потоков()


def test_скачанное_видно_в_списке(приложение, tmp_path):
    """Иначе снятие галочки выглядит как удаление уже скачанного."""
    источник = ПоддельныйИсточник(tmp_path, архив="youtube aaaaaaaaaaa\n")
    двери = ОкноРоликов(источник, "канал", фоновые=False)
    двери._перепись_готова(ПЕРЕПИСЬ)

    assert двери.таблица.item(0, 4).text() == "скачан"
    двери._дождаться_потоков()


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
