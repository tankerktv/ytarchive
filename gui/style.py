"""Внешний вид: цвета, карточки, плитки.

Цвета не записаны числами, а выводятся из палитры системы. Раньше приглушённый
текст был задан как `#666` — на светлой теме это серый, на тёмной — почти
невидимый: подписи в окне роликов читались с трудом. Смешивая цвет текста
с цветом фона, получаем приглушённый оттенок, верный для любой темы.

Правятся только те виджеты, что названы здесь по имени или по роли.
Остальные остаются родными для системы: кнопка должна выглядеть кнопкой
этой системы, а не нашей выдумкой.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

#: Цвета состояний. Подобраны так, чтобы читаться и на светлом, и на тёмном.
ЗЕЛЁНЫЙ = "#2ea043"
ЖЁЛТЫЙ = "#bf8700"
СЕРЫЙ = "#8b949e"
СИНИЙ = "#4c8dd6"
КРАСНЫЙ = "#e5484d"


def смешать(первый: QColor, второй: QColor, доля: float) -> str:
    """Цвет между двумя: `доля` — сколько взять от второго."""
    def канал(а: int, б: int) -> int:
        return round(а + (б - а) * доля)

    return QColor(
        канал(первый.red(), второй.red()),
        канал(первый.green(), второй.green()),
        канал(первый.blue(), второй.blue()),
    ).name()


def таблица_стилей(палитра: QPalette) -> str:
    фон = палитра.color(QPalette.ColorRole.Window)
    текст = палитра.color(QPalette.ColorRole.WindowText)
    упор = палитра.color(QPalette.ColorRole.Highlight)
    на_упоре = палитра.color(QPalette.ColorRole.HighlightedText)

    карточка = смешать(фон, текст, 0.05)
    рамка = смешать(фон, текст, 0.14)
    приглушённый = смешать(текст, фон, 0.40)
    упор_наведён = смешать(упор, текст, 0.12)
    упор_выключен = смешать(фон, текст, 0.18)

    return f"""
    QFrame#card {{
        background: {карточка};
        border: 1px solid {рамка};
        border-radius: 10px;
    }}
    QFrame#hint {{
        background: {смешать(фон, упор, 0.14)};
        border: 1px solid {смешать(фон, упор, 0.45)};
        border-radius: 10px;
    }}
    QLabel[role="muted"] {{ color: {приглушённый}; }}
    QLabel[role="title"] {{ font-size: 19px; font-weight: 600; }}
    QLabel[role="section"] {{ font-size: 14px; font-weight: 600; }}
    QLabel[role="tile-value"] {{ font-size: 22px; font-weight: 600; }}
    QLabel[role="tile-label"] {{ color: {приглушённый}; }}
    QPushButton#primary {{
        background: {упор.name()};
        color: {на_упоре.name()};
        border: none;
        border-radius: 6px;
        padding: 8px 22px;
        font-weight: 600;
    }}
    QPushButton#primary:hover {{ background: {упор_наведён}; }}
    QPushButton#primary:disabled {{ background: {упор_выключен}; color: {приглушённый}; }}
    QProgressBar {{
        border: none;
        border-radius: 4px;
        background: {рамка};
        max-height: 8px;
        min-height: 8px;
    }}
    QProgressBar::chunk {{ border-radius: 4px; background: {упор.name()}; }}
    """


def применить(приложение) -> None:
    """Задать вид всему приложению — окну и всем его диалогам разом."""
    приложение.setStyleSheet(таблица_стилей(приложение.palette()))


def приглушить(надпись: QLabel) -> QLabel:
    """Второстепенный текст: пояснения, счётчики, подсказки."""
    надпись.setProperty("role", "muted")
    return надпись


def роль(надпись: QLabel, имя: str) -> QLabel:
    надпись.setProperty("role", имя)
    return надпись


def карточка(имя: str = "card") -> tuple[QFrame, QVBoxLayout]:
    """Рамка со скруглёнными углами и её содержимое."""
    рамка = QFrame()
    рамка.setObjectName(имя)
    внутри = QVBoxLayout(рамка)
    внутри.setContentsMargins(16, 14, 16, 14)
    внутри.setSpacing(8)
    return рамка, внутри


def плитка(подпись: str) -> tuple[QFrame, QLabel]:
    """Крупное число с подписью. Возвращает рамку и надпись с числом."""
    рамка, внутри = карточка()
    внутри.setSpacing(2)
    значение = роль(QLabel("—"), "tile-value")
    внутри.addWidget(значение)
    внутри.addWidget(роль(QLabel(подпись), "tile-label"))
    return рамка, значение
