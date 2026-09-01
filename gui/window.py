"""Окно наблюдения за выкачкой.

**Окно не качает.** Выкачку ведёт задание планировщика; окно только смотрит:
читает журнал, показывает ход и умеет запустить или остановить задание.
Иначе две копии подрались бы за замок и за файл архива.

Отсюда главное следствие: окно можно закрыть, и ничего не остановится.

Весь смысл — в `core`. Здесь только Qt: взять снимок и нарисовать.
Если сюда захотелось добавить `if` с содержательным условием, его место в ядре.
"""

from __future__ import annotations

import sys
from dataclasses import replace

from PySide6.QtCore import QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSystemTrayIcon,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.archive import parse_archive
from core.channels import format_channels, move_channel, parse_channels, remove_channel
from core.config import ConfigError, dump_config, loads, parse_config
from core.status import RunState, build_status
from core.ytdlp_args import ALLOWED_HEIGHTS
from gui.source import ArchiveSource

#: Как часто обновляемся. Журнал разрежен, чаще незачем — а лишние чтения
#: файла с сетевого диска стоят дороже, чем кажется.
REFRESH_MS = 2000
TAIL_LINES = 300

ЦВЕТА = {
    RunState.RUNNING: "#2e7d32",
    RunState.BETWEEN: "#795548",
    RunState.IDLE: "#616161",
    RunState.NEEDS_HUMAN: "#c62828",
}


def нарисовать_значок(цвет: str) -> QIcon:
    """Значок для трея — рисуем, а не носим картинкой в репозитории.

    Цвет отвечает состоянию, поэтому по трею видно, идёт ли выкачка,
    не открывая окна.
    """
    полотно = QPixmap(64, 64)
    полотно.fill(Qt.GlobalColor.transparent)
    кисть = QPainter(полотно)
    кисть.setRenderHint(QPainter.RenderHint.Antialiasing)
    кисть.setBrush(QColor(цвет))
    кисть.setPen(Qt.PenStyle.NoPen)
    кисть.drawEllipse(4, 4, 56, 56)
    кисть.setPen(QColor("white"))
    шрифт = QFont()
    шрифт.setPointSize(30)
    шрифт.setBold(True)
    кисть.setFont(шрифт)
    # Стрелка вниз: «качает». Читается в трее даже в 16 точек.
    кисть.drawText(полотно.rect(), Qt.AlignmentFlag.AlignCenter, "↓")
    кисть.end()
    return QIcon(полотно)


class ПоискКаналов(QThread):
    """Поиск и перепись в отдельном потоке.

    Иначе окно застыло бы на минуты: перепись канала на две тысячи роликов
    идёт заметно дольше самого поиска. Найденное показывается сразу,
    числа подставляются по мере готовности.
    """

    найдено = Signal(object, str)
    измерено = Signal(int, object, str)
    закончено = Signal()

    def __init__(self, source: ArchiveSource, запрос: str) -> None:
        super().__init__()
        self.source = source
        self.запрос = запрос
        self._бросить = False

    def бросить(self) -> None:
        """Прекратить работу: человек закрыл окно или начал новый поиск.
        Досчитывать ненужное — держать его в ожидании зря."""
        self._бросить = True

    def run(self) -> None:
        from runner.avatars import ensure_avatar, fetch_avatar_url
        from runner.search import measure_channel, search_channels

        кандидаты, ответ = search_channels(
            self.запрос, self.source.settings, ytdlp=self.source.ytdlp
        )
        self.найдено.emit(кандидаты, ответ)

        for номер, кандидат in enumerate(кандидаты):
            if self._бросить:
                break
            # Логотип берём первым: он приходит быстро и сразу делает список
            # узнаваемым, пока перепись ещё считает объём.
            адрес = fetch_avatar_url(кандидат, self.source.settings, ytdlp=self.source.ytdlp)
            if адрес:
                ensure_avatar(self.source.avatars_dir, кандидат.channel_id, адрес)
                self.измерено.emit(номер, replace(кандидат, avatar_url=адрес), "логотип")
            if self._бросить:
                break
            измеренный, ответ_меры = measure_channel(
                replace(кандидат, avatar_url=адрес), self.source.settings, ytdlp=self.source.ytdlp
            )
            self.измерено.emit(номер, измеренный, ответ_меры)

        self.закончено.emit()


class ЗагрузкаЛоготипов(QThread):
    """Логотипы уже добавленных каналов — разово, при открытии окна.

    Отдельно от поиска: те каналы уже в списке, искать их незачем, а
    картинки для них ещё не скачаны.
    """

    готово = Signal()

    def __init__(self, source: ArchiveSource, каналы: list) -> None:
        super().__init__()
        self.source = source
        self.каналы = list(каналы)

    def run(self) -> None:
        from core.search import Candidate
        from runner.avatars import cached_avatar, ensure_avatar, fetch_avatar_url

        for канал in self.каналы:
            опознание = [
                к for к in канал.url.rstrip("/").split("/") if к.startswith("UC") and len(к) == 24
            ]
            if not опознание:
                continue  # канал задан хендлом — опознать по адресу нечем
            идентификатор = опознание[0]
            if cached_avatar(self.source.avatars_dir, идентификатор) is not None:
                continue  # уже лежит: аватары не меняются месяцами
            кандидат = Candidate(name=канал.name, channel_id=идентификатор)
            адрес = fetch_avatar_url(кандидат, self.source.settings, ytdlp=self.source.ytdlp)
            if адрес:
                ensure_avatar(self.source.avatars_dir, идентификатор, адрес)
        self.готово.emit()


class Window(QMainWindow):
    def __init__(self, source: ArchiveSource, *, фоновые: bool = True) -> None:
        super().__init__()
        self.source = source
        # Qt обрывает процесс, если поток жив в момент уничтожения окна.
        # В самопроверке окно строится и тут же гибнет, поэтому фоновую
        # работу там не начинаем вовсе — иначе сборка падала бы без
        # единой строки объяснения, как и случилось.
        self._фоновые = фоновые
        self.setWindowTitle("Архив YouTube")
        self.resize(940, 640)

        self.вкладки = QTabWidget()
        self.вкладки.addTab(self._вкладка_обзор(), "Обзор")
        self.вкладки.addTab(self._вкладка_каналы(), "Каналы")
        self.вкладки.addTab(self._вкладка_настройки(), "Настройки")
        self.setCentralWidget(self.вкладки)

        self._последний_журнал = ""
        self._предупредили_о_трее = False
        self._собрать_трей()

        self._логотипы = None
        if self._фоновые and self._каналы:
            self._логотипы = ЗагрузкаЛоготипов(self.source, self._каналы)
            self._логотипы.готово.connect(self._перечитать_каналы)
            self._логотипы.start()

        self.таймер = QTimer(self)
        self.таймер.timeout.connect(self.обновить)
        self.таймер.start(REFRESH_MS)
        self.обновить()

    # --- вкладка «Обзор» ----------------------------------------------------

    def _вкладка_обзор(self) -> QWidget:
        корень = QWidget()
        столбец = QVBoxLayout(корень)
        столбец.setContentsMargins(16, 12, 16, 12)
        столбец.setSpacing(10)

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

        # Две полосы: текущий файл и проход по каналу. Обе показываются только
        # когда есть что показывать — пустая полоса на нуле выглядит как
        # застрявшая работа и тревожит на ровном месте.
        self.полоса_файла = QProgressBar()
        self.полоса_файла.setFormat("%p%")
        self.подпись_файла = QLabel("")
        self.подпись_файла.setStyleSheet("color: #666;")
        столбец.addWidget(self.подпись_файла)
        столбец.addWidget(self.полоса_файла)

        self.полоса_канала = QProgressBar()
        self.полоса_канала.setFormat("%p%")
        self.подпись_канала = QLabel("")
        self.подпись_канала.setStyleSheet("color: #666;")
        столбец.addWidget(self.подпись_канала)
        столбец.addWidget(self.полоса_канала)

        ряд = QHBoxLayout()
        self.кнопка_пуск = QPushButton("Запустить")
        self.кнопка_стоп = QPushButton("Остановить")
        обновить = QPushButton("Обновить")
        for кнопка in (self.кнопка_пуск, self.кнопка_стоп, обновить):
            ряд.addWidget(кнопка)
        ряд.addStretch(1)
        столбец.addLayout(ряд)

        self.кнопка_пуск.clicked.connect(self._пуск)
        self.кнопка_стоп.clicked.connect(self._стоп)
        обновить.clicked.connect(self.обновить)

        self.журнал = QPlainTextEdit()
        self.журнал.setReadOnly(True)
        self.журнал.setFont(QFont("Consolas", 10))
        self.журнал.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        столбец.addWidget(self.журнал, 1)
        return корень

    # --- вкладка «Каналы» ---------------------------------------------------

    def _вкладка_каналы(self) -> QWidget:
        корень = QWidget()
        столбец = QVBoxLayout(корень)
        столбец.setContentsMargins(16, 12, 16, 12)

        # --- поиск канала ---
        ряд_поиска = QHBoxLayout()
        self.поле_поиска = QLineEdit()
        self.поле_поиска.setPlaceholderText("Название канала — например, alex m")
        self.кнопка_искать = QPushButton("Найти")
        ряд_поиска.addWidget(self.поле_поиска, 1)
        ряд_поиска.addWidget(self.кнопка_искать)
        столбец.addLayout(ряд_поиска)

        self.поиск_ответ = QLabel("")
        self.поиск_ответ.setStyleSheet("color: #666;")
        столбец.addWidget(self.поиск_ответ)

        self.находки = QTableWidget(0, 4)
        self.находки.setHorizontalHeaderLabels(["", "Канал", "Объём", "Влезет"])
        self.находки.setIconSize(QSize(32, 32))
        self.находки.horizontalHeader().setStretchLastSection(True)
        self.находки.setColumnWidth(0, 44)
        self.находки.setColumnWidth(1, 260)
        self.находки.setColumnWidth(2, 260)
        self.находки.setMaximumHeight(170)
        self.находки.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.находки.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        столбец.addWidget(self.находки)

        self.кнопка_добавить = QPushButton("Добавить выбранный канал")
        self.кнопка_добавить.setEnabled(False)
        столбец.addWidget(self.кнопка_добавить)

        self.кнопка_искать.clicked.connect(self._искать)
        self.поле_поиска.returnPressed.connect(self._искать)
        self.находки.itemSelectionChanged.connect(self._выбор_находки)
        self.кнопка_добавить.clicked.connect(self._добавить_находку)
        self._находки: list = []
        self._поиск = None

        столбец.addWidget(QLabel("Сколько уже лежит в архиве по каждому каналу:"))
        self.таблица = QTableWidget(0, 3)
        self.таблица.setHorizontalHeaderLabels(["Канал", "Файлов", "Объём"])
        self.таблица.horizontalHeader().setStretchLastSection(True)
        self.таблица.setColumnWidth(0, 380)
        self.таблица.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        столбец.addWidget(self.таблица)

        столбец.addWidget(QLabel(
            "Список каналов. Порядок здесь — это порядок обхода: верхний "
            "забирается первым."
        ))
        ряд_списка = QHBoxLayout()
        self.список_каналов = QTableWidget(0, 4)
        self.список_каналов.setHorizontalHeaderLabels(["", "Канал", "Файлов", "Объём"])
        self.список_каналов.horizontalHeader().setStretchLastSection(True)
        self.список_каналов.setColumnWidth(0, 52)
        self.список_каналов.setColumnWidth(1, 330)
        self.список_каналов.setColumnWidth(2, 80)
        self.список_каналов.verticalHeader().setVisible(False)
        self.список_каналов.setIconSize(QSize(40, 40))
        self.список_каналов.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.список_каналов.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.список_каналов.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        ряд_списка.addWidget(self.список_каналов, 1)

        кнопки = QVBoxLayout()
        self.кнопка_вверх = QPushButton("↑ Выше")
        self.кнопка_вниз = QPushButton("↓ Ниже")
        self.кнопка_убрать = QPushButton("Убрать")
        for к in (self.кнопка_вверх, self.кнопка_вниз, self.кнопка_убрать):
            к.setEnabled(False)
            кнопки.addWidget(к)
        кнопки.addStretch(1)
        ряд_списка.addLayout(кнопки)
        столбец.addLayout(ряд_списка, 1)

        self.каналы_ответ = QLabel("")
        self.каналы_ответ.setStyleSheet("color: #666;")
        self.каналы_ответ.setWordWrap(True)
        столбец.addWidget(self.каналы_ответ)

        self.кнопка_вверх.clicked.connect(lambda: self._переставить(-1))
        self.кнопка_вниз.clicked.connect(lambda: self._переставить(+1))
        self.кнопка_убрать.clicked.connect(self._убрать_канал)
        self.список_каналов.itemSelectionChanged.connect(self._выбор_канала)
        self._каналы: list = []
        self._перечитать_каналы()
        return корень

    # --- порядок и удаление -------------------------------------------------

    def _выбор_канала(self) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        есть = bool(строки)
        номер = строки[0].row() if есть else -1
        self.кнопка_вверх.setEnabled(есть and номер > 0)
        self.кнопка_вниз.setEnabled(есть and номер < len(self._каналы) - 1)
        self.кнопка_убрать.setEnabled(есть)

    def _переставить(self, куда: int) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        номер = строки[0].row()
        стало = move_channel(self._каналы, номер, куда)
        if стало == tuple(self._каналы):
            return
        self.каналы_ответ.setText(self.source.write_channels(format_channels(стало)))
        self._перечитать_каналы()
        self.список_каналов.selectRow(номер + куда)

    def _убрать_канал(self) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        номер = строки[0].row()
        канал = self._каналы[номер]
        ответ = QMessageBox.question(
            self,
            "Убрать канал",
            f"Убрать «{канал.name}» из списка?\n\n"
            "Скачанное останется на диске и в учёте — канал уходит из очереди, "
            "а не из архива. Вернёте обратно — заново качать не станет.",
        )
        if ответ != QMessageBox.StandardButton.Yes:
            return
        стало = remove_channel(self._каналы, номер)
        self.каналы_ответ.setText(self.source.write_channels(format_channels(стало)))
        self._перечитать_каналы()

    def _искать(self) -> None:
        запрос = self.поле_поиска.text().strip()
        if not запрос:
            self.поиск_ответ.setText("введите название")
            return
        if self._поиск is not None and self._поиск.isRunning():
            self._поиск.бросить()

        self.находки.setRowCount(0)
        self._находки = []
        self.кнопка_добавить.setEnabled(False)
        self.кнопка_искать.setEnabled(False)
        self.поиск_ответ.setText("ищу…")

        self._поиск = ПоискКаналов(self.source, запрос)
        self._поиск.найдено.connect(self._показать_находки)
        self._поиск.измерено.connect(self._обновить_находку)
        self._поиск.закончено.connect(lambda: self.кнопка_искать.setEnabled(True))
        self._поиск.start()

    def _показать_находки(self, кандидаты: list, ответ: str) -> None:
        self._находки = list(кандидаты)
        self.поиск_ответ.setText(ответ)
        self.находки.setRowCount(len(self._находки))
        for номер, кандидат in enumerate(self._находки):
            self._нарисовать_находку(номер, кандидат)

    def _обновить_находку(self, номер: int, кандидат, ответ: str) -> None:
        if 0 <= номер < len(self._находки):
            self._находки[номер] = кандидат
            self._нарисовать_находку(номер, кандидат)
            if not кандидат.measured:
                self.поиск_ответ.setText(f"{кандидат.name}: {ответ}")

    def _нарисовать_находку(self, номер: int, кандидат) -> None:
        from core.search import fits

        влезет = fits(кандидат, self.source.free_bytes())
        # Прямо говорим, что неизвестно: «да» по неизмеренному каналу —
        # это обещание, которого мы дать не можем.
        подпись = {None: "…", True: "да", False: "НЕ ВЛЕЗЕТ"}[влезет]

        значок = QTableWidgetItem("")
        from runner.avatars import cached_avatar

        путь = cached_avatar(self.source.avatars_dir, кандидат.channel_id)
        if путь is not None:
            значок.setIcon(QIcon(str(путь)))
        self.находки.setItem(номер, 0, значок)
        self.находки.setRowHeight(номер, 38)

        for сдвиг, значение in enumerate((кандидат.name, кандидат.describe(), подпись)):
            ячейка = QTableWidgetItem(значение)
            if сдвиг == 2 and влезет is False:
                ячейка.setForeground(QColor("#c62828"))
            self.находки.setItem(номер, сдвиг + 1, ячейка)

    def _выбор_находки(self) -> None:
        строки = self.находки.selectionModel().selectedRows()
        self.кнопка_добавить.setEnabled(bool(строки))

    def _добавить_находку(self) -> None:
        строки = self.находки.selectionModel().selectedRows()
        if not строки:
            return
        кандидат = self._находки[строки[0].row()]
        from core.search import fits

        if fits(кандидат, self.source.free_bytes()) is False:
            ответ = QMessageBox.question(
                self,
                "Может не влезть",
                f"По верхней оценке «{кандидат.name}» займёт больше, чем есть свободного места.\n\n"
                f"{кандидат.describe()}\n\nВсё равно добавить?",
            )
            if ответ != QMessageBox.StandardButton.Yes:
                return
        self.поиск_ответ.setText(self.source.add_channel(кандидат.name, кандидат.url))
        self._перечитать_каналы()

    def _перечитать_каналы(self) -> None:
        разбор = parse_channels(self.source.channels_text())
        self._каналы = list(разбор.channels)

        # Непонятые строки не прячем: иначе человек не узнает, что канал
        # выпал из очереди, а перезапись файла из окна их бы и вовсе стёрла.
        if разбор.problems:
            беды = "; ".join(f"строка {p.line_number}: {p.reason}" for p in разбор.problems)
            self.каналы_ответ.setText(f"в файле есть непонятые строки — {беды}")

        по_папкам = {имя: (файлов, байт) for имя, файлов, байт in self.source.channel_stats()}
        self.список_каналов.setRowCount(len(self._каналы))
        for номер, канал in enumerate(self._каналы):
            файлов, байт = по_папкам.get(канал.name, (0, 0))
            значок = QTableWidgetItem("")
            путь = self.source.avatar(канал.name)
            if путь is not None:
                значок.setIcon(QIcon(str(путь)))
            self.список_каналов.setItem(номер, 0, значок)
            self.список_каналов.setItem(номер, 1, QTableWidgetItem(канал.name))
            self.список_каналов.setItem(номер, 2, QTableWidgetItem(str(файлов) if файлов else "—"))
            self.список_каналов.setItem(
                номер, 3, QTableWidgetItem(f"{байт / 1024**3:.1f} ГБ" if байт else "—")
            )
        for номер in range(len(self._каналы)):
            self.список_каналов.setRowHeight(номер, 46)
        self._выбор_канала()

    # --- вкладка «Настройки» ------------------------------------------------

    def _вкладка_настройки(self) -> QWidget:
        корень = QWidget()
        столбец = QVBoxLayout(корень)
        столбец.setContentsMargins(16, 12, 16, 12)

        форма = QFormLayout()
        self.поле_качество = QComboBox()
        for h in ALLOWED_HEIGHTS:
            self.поле_качество.addItem(f"до {h}p", h)
        self.поле_av1 = QCheckBox("Предпочитать AV1 (тот же вид, файл меньше)")
        self.поле_субтитры = QCheckBox("Забирать субтитры")
        self.поле_молчание = QSpinBox()
        self.поле_молчание.setRange(60, 3600)
        self.поле_молчание.setSuffix(" с")
        self.поле_пауза_мин = QSpinBox()
        self.поле_пауза_мин.setRange(0, 600)
        self.поле_пауза_мин.setSuffix(" с")
        self.поле_пауза_макс = QSpinBox()
        self.поле_пауза_макс.setRange(0, 600)
        self.поле_пауза_макс.setSuffix(" с")

        форма.addRow("Качество:", self.поле_качество)
        форма.addRow("", self.поле_av1)
        форма.addRow("", self.поле_субтитры)
        форма.addRow("Считать зависшим после:", self.поле_молчание)
        форма.addRow("Пауза между роликами, от:", self.поле_пауза_мин)
        форма.addRow("до:", self.поле_пауза_макс)
        столбец.addLayout(форма)

        подсказка = QLabel(
            "Паузы между роликами берегут доступ: на потоке в тысячи запросов "
            "YouTube начинает отвечать «подтвердите, что вы не бот». "
            "Предел молчания должен быть заметно больше самой длинной паузы, "
            "иначе живую выкачку будут убивать как зависшую."
        )
        подсказка.setWordWrap(True)
        подсказка.setStyleSheet("color: #666;")
        столбец.addWidget(подсказка)

        ряд = QHBoxLayout()
        сохранить = QPushButton("Сохранить настройки")
        вернуть = QPushButton("Вернуть как было")
        ряд.addWidget(сохранить)
        ряд.addWidget(вернуть)
        ряд.addStretch(1)
        self.настройки_ответ = QLabel("")
        self.настройки_ответ.setStyleSheet("color: #666;")
        ряд.addWidget(self.настройки_ответ)
        столбец.addLayout(ряд)
        столбец.addStretch(1)

        сохранить.clicked.connect(self._сохранить_настройки)
        вернуть.clicked.connect(self._перечитать_настройки)
        self._перечитать_настройки()
        return корень

    def _перечитать_настройки(self) -> None:
        try:
            config = parse_config(loads(self.source.config_text()))
        except (ConfigError, Exception) as ошибка:  # noqa: BLE001
            self.настройки_ответ.setText(f"настройки не читаются: {ошибка}")
            return
        self._config = config
        self.поле_качество.setCurrentIndex(ALLOWED_HEIGHTS.index(config.height))
        self.поле_av1.setChecked(config.prefer_av1)
        self.поле_субтитры.setChecked(config.write_subs)
        self.поле_молчание.setValue(int(config.limits.silence_limit))
        self.поле_пауза_мин.setValue(config.limits.sleep_min)
        self.поле_пауза_макс.setValue(config.limits.sleep_max)
        self.настройки_ответ.setText("")

    def _сохранить_настройки(self) -> None:
        from dataclasses import replace

        пределы = replace(
            self._config.limits,
            silence_limit=float(self.поле_молчание.value()),
            sleep_min=self.поле_пауза_мин.value(),
            sleep_max=self.поле_пауза_макс.value(),
        )
        новый = replace(
            self._config,
            height=self.поле_качество.currentData(),
            prefer_av1=self.поле_av1.isChecked(),
            write_subs=self.поле_субтитры.isChecked(),
            limits=пределы,
        )
        текст = dump_config(новый)
        try:
            # Проверяем то, что собираемся записать: испорченные настройки
            # оставят выкачку без запуска, а человека — без объяснения.
            parse_config(loads(текст))
        except (ConfigError, Exception) as ошибка:  # noqa: BLE001
            QMessageBox.warning(self, "Не сохранил", str(ошибка))
            self.настройки_ответ.setText("не сохранено")
            return
        self.настройки_ответ.setText(self.source.write_config(текст))
        self._config = новый

    # --- трей ---------------------------------------------------------------

    def _собрать_трей(self) -> None:
        self.трей = QSystemTrayIcon(нарисовать_значок(ЦВЕТА[RunState.IDLE]), self)
        меню = QMenu()
        показать = QAction("Показать окно", self)
        пуск = QAction("Запустить выкачку", self)
        стоп = QAction("Остановить выкачку", self)
        выход = QAction("Выйти", self)
        показать.triggered.connect(self._показаться)
        пуск.triggered.connect(self._пуск)
        стоп.triggered.connect(self._стоп)
        выход.triggered.connect(self._выйти)
        for пункт in (показать, пуск, стоп):
            меню.addAction(пункт)
        меню.addSeparator()
        меню.addAction(выход)
        self.трей.setContextMenu(меню)
        self.трей.activated.connect(
            lambda причина: self._показаться()
            if причина == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
        self.трей.show()

    def _показаться(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _дождаться_потоков(self) -> None:
        """Дождаться фоновой работы перед уходом.

        Живой поток в момент уничтожения окна Qt считает ошибкой и
        обрывает процесс — без сообщения, что особенно неприятно.
        """
        for поток in (self._поиск, self._логотипы):
            if поток is None:
                continue
            if hasattr(поток, "бросить"):
                поток.бросить()
            if поток.isRunning():
                поток.wait(5000)

    def _выйти(self) -> None:
        self._дождаться_потоков()
        self.трей.hide()
        QApplication.instance().quit()

    def closeEvent(self, event) -> None:  # noqa: N802 — имя задано Qt
        """Закрытие прячет окно, а не выходит.

        Выкачка от этого не зависит вовсе — её ведёт задание. Но человек,
        закрывший окно, ожидает найти программу в трее, а не гадать,
        осталась ли она.
        """
        event.ignore()
        self.hide()
        if not self._предупредили_о_трее:
            self.трей.showMessage(
                "Архив YouTube",
                "Окно свёрнуто в трей. Выкачка идёт сама и от окна не зависит.",
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )
            self._предупредили_о_трее = True

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

        self._обновить_полосы(снимок)

        self.кнопка_пуск.setEnabled(not снимок.state.is_working)
        self.кнопка_стоп.setEnabled(снимок.state.is_working)

        self.трей.setIcon(нарисовать_значок(ЦВЕТА[снимок.state]))
        self.трей.setToolTip(f"Архив YouTube — {снимок.headline()}")

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

        self._обновить_таблицу()

    def _обновить_полосы(self, снимок) -> None:
        """Полосы показываются, только когда есть что показывать.

        Пустая полоса на нуле выглядит как застрявшая работа и тревожит
        на ровном месте — а выкачка в это время может просто ждать паузы
        между роликами.
        """
        живое = self.source.live_state() if снимок.state.is_working else None

        показать_файл = bool(живое and живое.has_file)
        self.полоса_файла.setVisible(показать_файл)
        self.подпись_файла.setVisible(показать_файл)
        if показать_файл:
            self.полоса_файла.setValue(int(живое.percent))
            части = [живое.file_name]
            if живое.size_bytes:
                части.append(f"{живое.size_bytes / 1024**2:.0f} МБ")
            if живое.speed_bps:
                части.append(f"{живое.speed_bps / 1024**2:.1f} МБ/с")
            if живое.eta:
                части.append(f"осталось {живое.eta}")
            self.подпись_файла.setText(" · ".join(части))

        показать_канал = bool(живое and живое.item_total)
        self.полоса_канала.setVisible(показать_канал)
        self.подпись_канала.setVisible(показать_канал)
        if показать_канал:
            self.полоса_канала.setValue(int(живое.item_fraction() * 100))
            подпись = f"{живое.channel}: ролик {живое.item_index} из {живое.item_total}"
            if живое.channel_total:
                подпись += f" · канал {живое.channel_index} из {живое.channel_total}"
            self.подпись_канала.setText(подпись)

    def _обновить_таблицу(self) -> None:
        строки = self.source.channel_stats()
        if self.таблица.rowCount() != len(строки):
            self.таблица.setRowCount(len(строки))
        for номер, (имя, файлов, байт) in enumerate(строки):
            значения = (имя, str(файлов), f"{байт / 1024**3:.2f} ГБ")
            for столбец, значение in enumerate(значения):
                ячейка = self.таблица.item(номер, столбец)
                if ячейка is None:
                    self.таблица.setItem(номер, столбец, QTableWidgetItem(значение))
                elif ячейка.text() != значение:
                    ячейка.setText(значение)

    # --- кнопки -------------------------------------------------------------

    def _пуск(self) -> None:
        self.подпись.setText(self.source.start())
        self.обновить()

    def _стоп(self) -> None:
        self.подпись.setText(self.source.stop())
        self.обновить()


def run(source: ArchiveSource, *, selftest: bool = False) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    # Без этого закрытие окна завершило бы программу вместе с треем.
    app.setQuitOnLastWindowClosed(False)
    окно = Window(source, фоновые=not selftest)
    окно.show()
    if selftest:
        # Один оборот событий и выход: так сборка убеждается, что окно
        # хотя бы строится, не открывая ничего человеку.
        app.processEvents()
        окно._дождаться_потоков()
        окно.трей.hide()
        return 0
    return app.exec()
