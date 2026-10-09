"""Знак программы: файлы не отстают от описания и годятся системе.

Знак задан числами в `core/logo.py`, а в `assets/` лежат его копии для того,
что рисовать не умеет. Копии — это то, что расходится молча: форму поправили
в коде, а ярлык и README остались со старой.
"""

import struct
import sys
from pathlib import Path

import pytest

from core.install import WINDOWS_SHORTCUT_SCRIPT, desktop_entry
from core.logo import ЛОТОК, СЕТКА, ТРЕУГОЛЬНИК, ФИРМЕННЫЙ, svg

КОРЕНЬ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(КОРЕНЬ / "tools"))

from make_icon import ICO, РАЗМЕРЫ_ICO, SVG, собрать_ico  # noqa: E402


def test_svg_в_репозитории_совпадает_с_описанием():
    """Иначе README показывал бы один знак, а окно — другой."""
    assert SVG.read_text(encoding="utf-8") == svg(), "пересоберите: python tools/make_icon.py"


def test_знак_помещается_в_плитку_с_полями():
    """Линии имеют толщину; точка на самом краю дала бы обрезанный знак."""
    for x, y in (*ТРЕУГОЛЬНИК, *ЛОТОК):
        assert 20 <= x <= СЕТКА - 20 and 20 <= y <= СЕТКА - 20


def test_svg_несёт_фирменный_цвет_и_годится_как_файл():
    текст = svg()
    assert текст.startswith("<svg xmlns=") and текст.rstrip().endswith("</svg>")
    assert ФИРМЕННЫЙ in текст
    assert ФИРМЕННЫЙ not in svg("#2ea043"), "цвет плитки задаётся доводом"


def test_ico_в_репозитории_настоящий_и_со_всеми_размерами():
    """Windows берёт из .ico ближайший размер. С одним размером значок в
    трее был бы сжатой кашей, а в проводнике — растянутым пятном."""
    данные = ICO.read_bytes()
    зарезервировано, вид, сколько = struct.unpack_from("<HHH", данные, 0)
    assert (зарезервировано, вид) == (0, 1), "заголовок .ico"
    assert сколько == len(РАЗМЕРЫ_ICO)

    стороны = []
    for номер in range(сколько):
        ширина, высота, _ц, _р, _пл, глубина, размер, смещение = struct.unpack_from(
            "<BBBBHHII", данные, 6 + 16 * номер
        )
        assert ширина == высота and глубина == 32
        assert данные[смещение : смещение + 8] == b"\x89PNG\r\n\x1a\n", "внутри лежит PNG"
        assert смещение + размер <= len(данные), "запись не выходит за файл"
        стороны.append(ширина or 256)
    assert tuple(стороны) == РАЗМЕРЫ_ICO


def test_сборка_ico_размер_256_пишет_нулём():
    """Поле размера в .ico однобайтовое, и 256 в него не влезает."""
    данные = собрать_ico([(256, b"\x89PNG\r\n\x1a\n" + b"x")])
    assert данные[6] == 0 and данные[7] == 0


def test_ярлык_windows_получает_значок_переменной_а_не_подстановкой():
    """Путь к значку идёт тем же способом, что и остальные значения: каталог
    пользователя с апострофом в имени иначе стал бы исполняемым кодом."""
    assert "$link.IconLocation = $env:YTA_ICON" in WINDOWS_SHORTCUT_SCRIPT


def test_значок_в_desktop_файле():
    с_значком = desktop_entry("Имя", "Описание", ("/a/python", "gui"), "/a/assets/logo.svg")
    assert "Icon=/a/assets/logo.svg\n" in с_значком
    assert "Icon=" not in desktop_entry("Имя", "Описание", ("/a/python", "gui"))


@pytest.mark.slow
def test_значок_рисуется_во_всех_размерах_и_цветах():
    import os

    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QApplication

    _приложение = QApplication.instance() or QApplication([])
    from gui.logo import РАЗМЕРЫ, значок, нарисовать

    assert sorted(размер.width() for размер in значок().availableSizes()) == sorted(РАЗМЕРЫ)

    картинка = нарисовать(160, "#2ea043").toImage()
    assert картинка.pixelColor(80, 20) == QColor("#2ea043"), "плитка — заданного цвета"
    assert картинка.pixelColor(70, 68) == QColor("white"), "внутри треугольника"
    assert картинка.pixelColor(80, 122) == QColor("white"), "на дне лотка"
    assert картинка.pixelColor(2, 2).alpha() == 0, "углы плитки скруглены"
