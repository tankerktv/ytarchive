"""Общее для всех проверок.

Переводчик один на процесс — так задумано, язык за время работы программы
меняется редко. Но в проверках это делает их зависимыми от порядка: тест,
переключивший язык, оставляет его следующему, и тот вдруг видит «downloaded»
там, где ждал «скачан».

Поймано на себе: мастер первого запуска берёт язык у системы, а система здесь
английская — и два теста списка роликов упали, хотя ничего в них не менялось.
"""

import pytest

from core.i18n import ИСХОДНЫЙ
from runner.language import настроить, текущий


@pytest.fixture(autouse=True)
def язык_как_в_исходнике():
    """Каждая проверка начинается на исходном языке и возвращает его после.

    Автоматически: помнить об этом в каждом тесте — значит однажды забыть.
    """
    настроить(ИСХОДНЫЙ)
    yield
    if текущий() != ИСХОДНЫЙ:
        настроить(ИСХОДНЫЙ)


@pytest.fixture(scope="session", autouse=True)
def окна_убираются_до_выхода():
    """Уничтожить окна, пока Qt ещё жив.

    Поймано в Debian: все проверки проходили, а потом процесс падал при
    выходе — «shared QObject was deleted directly», Segmentation fault. Окна,
    созданные в проверках, доживали до конца интерпретатора, и Python
    разбирал их уже после самого Qt. На Windows это сходило с рук, в сборке
    означало бы красный прогон при зелёных проверках.

    Там, где Qt нет, делать нечего: проверки окна тогда и не запускались.
    """
    yield
    try:
        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtWidgets import QApplication
    except ImportError:
        return
    приложение = QApplication.instance()
    if приложение is None:
        return
    for окно in приложение.topLevelWidgets():
        окно.close()
        окно.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    приложение.processEvents()
