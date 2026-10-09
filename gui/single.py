"""Одно окно на один архив.

Закрытое окно прячется в трей, а не выходит. Человек, не найдя его глазами,
открывает ярлык снова — и получает второе окно, потом третье. На машине
автора их нашлось три разом: три значка в трее, три набора потоков, и каждое
каждые две секунды читало архив.

Второй запуск теперь не открывает окно, а просит первое показаться.

Связь — через местное соединение с именем от пути к настройкам: окна разных
архивов друг другу не мешают.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from PySide6.QtNetwork import QLocalServer, QLocalSocket

#: Сколько ждём ответа первого окна. Оно либо есть и отвечает сразу, либо его нет.
ЖДАТЬ_МС = 500


def имя_соединения(config_path: Path) -> str:
    """Имя, одинаковое для всех запусков с одними настройками."""
    путь = str(Path(config_path).resolve()).casefold()
    return "ytarchive-" + hashlib.sha1(путь.encode("utf-8")).hexdigest()[:16]


def попросить_показаться(имя: str) -> bool:
    """Достучаться до уже открытого окна. True — оно есть и просьбу получило."""
    связь = QLocalSocket()
    связь.connectToServer(имя)
    if not связь.waitForConnected(ЖДАТЬ_МС):
        return False
    связь.write(b"show")
    связь.waitForBytesWritten(ЖДАТЬ_МС)
    связь.disconnectFromServer()
    return True


def слушать(имя: str, показаться: Callable[[], None], parent=None) -> QLocalServer | None:
    """Стать тем окном, к которому будут стучаться следующие запуски."""
    # След упавшего окна: на Linux и macOS соединение — файл, и после
    # аварийного выхода он остаётся. Раз до него не достучались, он ничей.
    QLocalServer.removeServer(имя)
    сервер = QLocalServer(parent)
    if not сервер.listen(имя):
        return None  # не вышло — окно откроется как раньше, без этой защиты

    def принять() -> None:
        связь = сервер.nextPendingConnection()
        if связь is not None:
            связь.disconnected.connect(связь.deleteLater)
        показаться()

    сервер.newConnection.connect(принять)
    return сервер
