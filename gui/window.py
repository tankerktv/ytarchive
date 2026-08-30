"""Окно наблюдения за выкачкой.

**Окно не качает.** Выкачку ведёт задание планировщика; окно только смотрит:
читает журнал, показывает ход и умеет запустить или остановить задание.
Иначе две копии подрались бы за замок и за файл архива.

Отсюда главное следствие: окно можно закрыть, и ничего не остановится.

Весь смысл — в `core.status`. Здесь только Qt: взять снимок и нарисовать.
Если сюда захотелось добавить `if` с содержательным условием, его место в ядре.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.archive import parse_archive
from core.status import RunState, build_status
from gui.source import ArchiveSource

#: Как часто обновляемся. Журнал разрежен, чаще незачем — а лишние чтения
#: файла с сетевого диска стоят дороже, чем кажется.
REFRESH_MS = 2000

#: Сколько последних строк журнала показываем.
TAIL_LINES = 300

ЦВЕТА = {
    RunState.RUNNING: "#2e7d32",
    RunState.BETWEEN: "#795548",
    RunState.IDLE: "#616161",
    RunState.NEEDS_HUMAN: "#c62828",
}


class Window(QMainWindow):
    def __init__(self, source: ArchiveSource) -> None:
        super().__init__()
        self.source = source
        self.setWindowTitle("Архив YouTube")
        self.resize(900, 600)

        корень = QWidget()
        столбец = QVBoxLayout(корень)
        столбец.setContentsMargins(16, 12, 16, 12)
        столбец.setSpacing(10)

        # --- шапка ---------------------------------------------------------
        self.заголовок = QLabel("читаю состояние…")
        шрифт = self.заголовок.font()
        шрифт.setPointSize(шрифт.pointSize() + 3)
        шрифт.setBold(True)
        self.заголовок.setFont(шрифт)
        self.заголовок.setWordWrap(True)
        столбец.addWidget(self.заголовок)

        self.подпись = QLabel("")
        self.подпись.setStyleSheet("color: #666;")
        self.подпись.setWordWrap(True)
        столбец.addWidget(self.подпись)

        # --- кнопки --------------------------------------------------------
        ряд = QHBoxLayout()
        self.кнопка_пуск = QPushButton("Запустить")
        self.кнопка_стоп = QPushButton("Остановить")
        self.кнопка_обновить = QPushButton("Обновить")
        for кнопка in (self.кнопка_пуск, self.кнопка_стоп, self.кнопка_обновить):
            ряд.addWidget(кнопка)
        ряд.addStretch(1)
        столбец.addLayout(ряд)

        self.кнопка_пуск.clicked.connect(self._пуск)
        self.кнопка_стоп.clicked.connect(self._стоп)
        self.кнопка_обновить.clicked.connect(self.обновить)

        # --- журнал --------------------------------------------------------
        self.журнал = QPlainTextEdit()
        self.журнал.setReadOnly(True)
        self.журнал.setFont(QFont("Consolas", 10))
        self.журнал.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        столбец.addWidget(self.журнал, 1)

        self.setCentralWidget(корень)

        self._последний_журнал = ""
        self.таймер = QTimer(self)
        self.таймер.timeout.connect(self.обновить)
        self.таймер.start(REFRESH_MS)
        self.обновить()

    # --- обновление ---------------------------------------------------------

    def обновить(self) -> None:
        строки = self.source.log_tail(TAIL_LINES)
        архив = parse_archive(self.source.archive_text())
        снимок = build_status(
            строки,
            process_running=self.source.download_running(),
            archive_count=len(архив),
        )

        self.заголовок.setText(снимок.headline())
        self.заголовок.setStyleSheet(f"color: {ЦВЕТА[снимок.state]};")

        части = [f"в архиве {снимок.archive_count} роликов"]
        if снимок.channel:
            части.append(f"канал {снимок.channel}")
        if снимок.last_size_bytes and снимок.last_speed_bps:
            части.append(
                f"последний файл {снимок.last_size_bytes / 1024**2:.0f} МБ, "
                f"{снимок.last_speed_bps / 1024**2:.1f} МБ/с"
            )
        if снимок.errors:
            части.append(f"отказов в этом сеансе {снимок.errors} — заберутся следующим проходом")
        self.подпись.setText(" · ".join(части))

        self.кнопка_пуск.setEnabled(not снимок.state.is_working)
        self.кнопка_стоп.setEnabled(снимок.state.is_working)

        текст = "\n".join(строки)
        if текст != self._последний_журнал:
            # Прокрутку держим внизу, только если человек и так смотрел вниз:
            # иначе окно будет выдёргивать его из середины при каждом обновлении.
            полоса = self.журнал.verticalScrollBar()
            внизу = полоса.value() >= полоса.maximum() - 4
            self.журнал.setPlainText(текст)
            if внизу:
                полоса.setValue(полоса.maximum())
            self._последний_журнал = текст

    # --- кнопки -------------------------------------------------------------

    def _пуск(self) -> None:
        self.подпись.setText(self.source.start())
        self.обновить()

    def _стоп(self) -> None:
        self.подпись.setText(self.source.stop())
        self.обновить()


def run(source: ArchiveSource, *, selftest: bool = False) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    окно = Window(source)
    окно.show()
    if selftest:
        # Один оборот событий и выход: так сборка убеждается, что окно
        # хотя бы строится, не открывая ничего человеку.
        app.processEvents()
        return 0
    return app.exec()
