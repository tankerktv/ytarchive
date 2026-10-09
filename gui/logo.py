"""Знак программы: ролик, лежащий в лотке.

Треугольник — «видео», лоток под ним — «сохранено». Вместе это и есть архив
роликов, а не просто «скачать».

Знак рисуется, а не лежит картинкой: в трее он меняет цвет по состоянию
выкачки, и держать по картинке на каждый цвет и каждый размер было бы
шестнадцатью файлами, которые разъедутся при первой же правке формы.
Файлы в `assets/` — для того, что рисовать не умеет: ярлыка Windows и README.
Их собирает `tools/make_icon.py` из этих же чисел.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF

from core.logo import (  # noqa: F401 — ФИРМЕННЫЙ нужен тем, кто зовёт отсюда
    ЛОТОК,
    СЕТКА,
    СКРУГЛЕНИЕ,
    ТОЛЩИНА_ЛОТКА,
    ТОЛЩИНА_ТРЕУГОЛЬНИКА,
    ТРЕУГОЛЬНИК,
    ФИРМЕННЫЙ,
)

#: Размеры, в которых значок нужен системе: трей, заголовок окна, панель задач,
#: крупные значки проводника.
РАЗМЕРЫ = (16, 24, 32, 48, 64, 128, 256)


def нарисовать(размер: int, цвет: str = ФИРМЕННЫЙ) -> QPixmap:
    """Знак в заданном размере на плитке заданного цвета."""
    полотно = QPixmap(размер, размер)
    полотно.fill(Qt.GlobalColor.transparent)
    кисть = QPainter(полотно)
    кисть.setRenderHint(QPainter.RenderHint.Antialiasing)
    кисть.scale(размер / СЕТКА, размер / СЕТКА)

    кисть.setPen(Qt.PenStyle.NoPen)
    кисть.setBrush(QColor(цвет))
    кисть.drawRoundedRect(QRectF(0, 0, СЕТКА, СЕТКА), СКРУГЛЕНИЕ, СКРУГЛЕНИЕ)

    белый = QColor("white")
    перо = QPen(белый, ТОЛЩИНА_ТРЕУГОЛЬНИКА)
    перо.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    кисть.setPen(перо)
    кисть.setBrush(белый)
    кисть.drawPolygon(QPolygonF([QPointF(x, y) for x, y in ТРЕУГОЛЬНИК]))

    перо = QPen(белый, ТОЛЩИНА_ЛОТКА)
    перо.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    перо.setCapStyle(Qt.PenCapStyle.RoundCap)
    кисть.setPen(перо)
    кисть.setBrush(Qt.BrushStyle.NoBrush)
    путь = QPainterPath(QPointF(*ЛОТОК[0]))
    for точка in ЛОТОК[1:]:
        путь.lineTo(QPointF(*точка))
    кисть.drawPath(путь)

    кисть.end()
    return полотно


def значок(цвет: str = ФИРМЕННЫЙ) -> QIcon:
    """Значок во всех нужных размерах. Система берёт ближайший, а не
    растягивает один: растянутый 64-точечный в трее превращается в кашу."""
    итог = QIcon()
    for размер in РАЗМЕРЫ:
        итог.addPixmap(нарисовать(размер, цвет))
    return итог
