"""Собрать файлы знака из его описания в `gui/logo.py`.

    python tools/make_icon.py            записать assets/logo.svg и assets/ytarchive.ico
    python tools/make_icon.py --check    проверить, что logo.svg не отстал от описания

Сам знак рисуется программой и файлов не требует. Файлы нужны тому, что
рисовать не умеет: ярлыку Windows (`.ico`) и README (`.svg`). Хранить их
приходится в репозитории — установщик работает на голом Python, без Qt,
и собрать значок на месте ему нечем.

Проверка сторожит только SVG: он — текст и обязан совпадать до знака.
ICO — растр, и его байты зависят от версии Qt; сравнивать их значило бы
получать ложную тревогу на каждом обновлении.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(КОРЕНЬ))

ПАПКА = КОРЕНЬ / "assets"
SVG = ПАПКА / "logo.svg"
ICO = ПАПКА / "ytarchive.ico"

#: Размеры внутри .ico. 256 — предел формата и то, что проводник берёт
#: для крупных значков.
РАЗМЕРЫ_ICO = (16, 24, 32, 48, 64, 128, 256)


def собрать_ico(картинки: list[tuple[int, bytes]]) -> bytes:
    """Склеить PNG разных размеров в один .ico.

    Формат простой: заголовок, по записи на картинку, затем сами картинки.
    PNG внутри .ico понимает Windows начиная с Vista. Пишем руками, потому
    что Qt умеет сохранить в .ico только одну картинку, а нужен набор.
    """
    заголовок = struct.pack("<HHH", 0, 1, len(картинки))
    записи = b""
    данные = b""
    смещение = len(заголовок) + 16 * len(картинки)
    for размер, png in картинки:
        # Размер 256 записывается нулём: поле однобайтовое.
        сторона = 0 if размер >= 256 else размер
        записи += struct.pack("<BBBBHHII", сторона, сторона, 0, 0, 1, 32, len(png), смещение)
        данные += png
        смещение += len(png)
    return заголовок + записи + данные


def нарисовать_png(размер: int) -> bytes:
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice

    from gui.logo import нарисовать

    хранилище = QByteArray()
    буфер = QBuffer(хранилище)
    буфер.open(QIODevice.OpenModeFlag.WriteOnly)
    нарисовать(размер).save(буфер, "PNG")
    буфер.close()
    return bytes(хранилище)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="только проверить logo.svg")
    args = parser.parse_args(argv)

    from core.logo import svg

    if args.check:
        if not SVG.exists() or SVG.read_text(encoding="utf-8") != svg():
            print(f"{SVG} отстал от gui/logo.py — пересоберите: python tools/make_icon.py")
            return 1
        print("logo.svg совпадает с описанием знака")
        return 0

    # Рисовать нужно Qt, а ему — приложение. Экран при этом не нужен.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QGuiApplication

    _приложение = QGuiApplication.instance() or QGuiApplication([])

    ПАПКА.mkdir(exist_ok=True)
    SVG.write_text(svg(), encoding="utf-8", newline="\n")
    ICO.write_bytes(собрать_ico([(размер, нарисовать_png(размер)) for размер in РАЗМЕРЫ_ICO]))
    print(f"записано: {SVG}, {ICO} ({ICO.stat().st_size} байт)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
