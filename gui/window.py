"""Окно наблюдения за выкачкой.

**Окно не качает.** Выкачку ведёт отдельный процесс; окно только смотрит:
читает журнал, показывает ход и умеет его завести или попросить остановиться.
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
    QInputDialog,
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
from core.config import BROWSERS, ConfigError, dump_config, loads, parse_config
from core.schedule import format_hours, parse_hours
from core.status import RunState, build_status, is_new_trouble
from core.ytdlp_args import ALLOWED_HEIGHTS
from gui.source import ArchiveSource
from core.i18n import ИСХОДНЫЙ, НАЗВАНИЯ, СИСТЕМНЫЙ, нормализовать
from core.locales import КАТАЛОГИ
from runner.language import _, системный_язык

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
                self.измерено.emit(номер, replace(кандидат, avatar_url=адрес), _("логотип"))
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
        self.setWindowTitle(_("Архив YouTube"))
        self.resize(940, 640)

        self.вкладки = QTabWidget()
        self.вкладки.addTab(self._вкладка_обзор(), _("Обзор"))
        self.вкладки.addTab(self._вкладка_каналы(), _("Каналы"))
        self.вкладки.addTab(self._вкладка_настройки(), _("Настройки"))
        self.setCentralWidget(self.вкладки)

        self._последний_журнал = ""
        self._предупредили_о_трее = False
        #: О какой беде уже сказано всплывающим сообщением.
        self._сказанная_беда = ""
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

        self.заголовок = QLabel(_("читаю состояние…"))
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
        self.кнопка_пуск = QPushButton(_("Запустить"))
        self.кнопка_стоп = QPushButton(_("Остановить"))
        обновить = QPushButton(_("Обновить"))
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
        self.поле_поиска.setPlaceholderText(_("Название канала — например, alex m"))
        self.кнопка_искать = QPushButton(_("Найти"))
        ряд_поиска.addWidget(self.поле_поиска, 1)
        ряд_поиска.addWidget(self.кнопка_искать)
        столбец.addLayout(ряд_поиска)

        self.поиск_ответ = QLabel("")
        self.поиск_ответ.setStyleSheet("color: #666;")
        столбец.addWidget(self.поиск_ответ)

        self.находки = QTableWidget(0, 4)
        self.находки.setHorizontalHeaderLabels(["", _("Канал"), _("Объём"), _("Влезет")])
        self.находки.setIconSize(QSize(32, 32))
        self.находки.horizontalHeader().setStretchLastSection(True)
        self.находки.setColumnWidth(0, 44)
        self.находки.setColumnWidth(1, 260)
        self.находки.setColumnWidth(2, 260)
        self.находки.setMaximumHeight(170)
        self.находки.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.находки.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        столбец.addWidget(self.находки)

        ряд_добавить = QHBoxLayout()
        self.кнопка_добавить = QPushButton(_("Добавить выбранный канал"))
        self.кнопка_добавить.setEnabled(False)
        self.кнопка_по_адресу = QPushButton(_("Добавить по адресу…"))
        self.кнопка_по_адресу.setToolTip(
            _("Плейлист, отдельный ролик или канал, которого нет в поиске.")
        )
        ряд_добавить.addWidget(self.кнопка_добавить, 1)
        ряд_добавить.addWidget(self.кнопка_по_адресу)
        столбец.addLayout(ряд_добавить)
        self.кнопка_по_адресу.clicked.connect(self._добавить_по_адресу)

        self.кнопка_искать.clicked.connect(self._искать)
        self.поле_поиска.returnPressed.connect(self._искать)
        self.находки.itemSelectionChanged.connect(self._выбор_находки)
        self.кнопка_добавить.clicked.connect(self._добавить_находку)
        self._находки: list = []
        self._поиск = None

        столбец.addWidget(QLabel(_("Сколько уже лежит в архиве по каждому каналу:")))
        self.таблица = QTableWidget(0, 3)
        self.таблица.setHorizontalHeaderLabels([_("Канал"), _("Файлов"), _("Объём")])
        self.таблица.horizontalHeader().setStretchLastSection(True)
        self.таблица.setColumnWidth(0, 380)
        self.таблица.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        столбец.addWidget(self.таблица)

        про_порядок = QLabel(
            _("Список каналов. Порядок здесь — это порядок обхода: верхний "
            "забирается первым.")
        )
        # С переносом: по-немецки эта строка вдвое длиннее и без него
        # распирала окно до 1250 точек.
        про_порядок.setWordWrap(True)
        столбец.addWidget(про_порядок)
        ряд_списка = QHBoxLayout()
        self.список_каналов = QTableWidget(0, 4)
        self.список_каналов.setHorizontalHeaderLabels(["", _("Канал"), _("Файлов"), _("Объём")])
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
        self.кнопка_вверх = QPushButton(_("↑ Выше"))
        self.кнопка_вниз = QPushButton(_("↓ Ниже"))
        self.кнопка_убрать = QPushButton(_("Убрать"))
        self.кнопка_имя = QPushButton(_("Переименовать…"))
        self.кнопка_имя.setToolTip(_("Сменить название канала вместе с его папкой."))
        self.кнопка_ролики = QPushButton(_("Выбрать ролики…"))
        self.кнопка_ролики.setToolTip(
            _("Список роликов канала с галочками. По умолчанию отмечены все.")
        )
        self.кнопка_правила = QPushButton(_("Правила…"))
        self.кнопка_правила.setToolTip(
            _("Не короче, не длиннее, не старше — одной строкой вместо сотни галочек.")
        )
        for к in (
            self.кнопка_вверх,
            self.кнопка_вниз,
            self.кнопка_убрать,
            self.кнопка_имя,
            self.кнопка_ролики,
            self.кнопка_правила,
        ):
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
        self.кнопка_ролики.clicked.connect(self._выбрать_ролики)
        self.кнопка_имя.clicked.connect(self._переименовать_канал)
        self.кнопка_правила.clicked.connect(self._правила_канала)
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
        self.кнопка_имя.setEnabled(есть)
        self.кнопка_ролики.setEnabled(есть)
        self.кнопка_правила.setEnabled(есть)

    def _правила_канала(self) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        номер = строки[0].row()
        канал = self._каналы[номер]

        from gui.upkeep import ОкноПравил

        окно = ОкноПравил(канал.name, канал.rules, self)
        if not окно.exec():
            return
        ответ = self.source.set_rules(номер, окно.правила)
        self.каналы_ответ.setText(
            ответ.text + (_(" — вступит в силу со следующего прохода") if ответ.ok else "")
        )
        self._перечитать_каналы()
        self.список_каналов.selectRow(номер)

    def _добавить_по_адресу(self) -> None:
        адрес, согласие = QInputDialog.getText(
            self,
            _("Добавить по адресу"),
            _("Адрес плейлиста, ролика или вкладки videos канала:"),
        )
        адрес = адрес.strip()
        if not согласие or not адрес:
            return
        имя, согласие = QInputDialog.getText(
            self,
            _("Добавить по адресу"),
            _("Название. Оно же станет именем папки в архиве:"),
        )
        if not согласие or not имя.strip():
            return
        self.поиск_ответ.setText(self.source.add_channel(имя.strip(), адрес))
        self._перечитать_каналы()

    def _выбрать_ролики(self) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        канал = self._каналы[строки[0].row()]

        from gui.videos import ОкноРоликов

        окно = ОкноРоликов(self.source, канал.name, self)
        if окно.exec():
            снято = len(self.source.exclusions())
            self.каналы_ответ.setText(
                _('выбор сохранён; всего снято роликов по всем каналам: {}').format(снято)
                + _(" — вступит в силу со следующего прохода")
            )

    def _переставить(self, куда: int) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        номер = строки[0].row()
        стало = move_channel(self._каналы, номер, куда)
        if стало == tuple(self._каналы):
            return
        self.каналы_ответ.setText(self.source.write_channels(format_channels(стало)).text)
        self._перечитать_каналы()
        self.список_каналов.selectRow(номер + куда)

    def _переименовать_канал(self) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        номер = строки[0].row()
        прежнее = self._каналы[номер].name

        новое, согласие = QInputDialog.getText(
            self,
            _("Переименовать канал"),
            _("Новое название. Оно же станет именем папки — она переименуется вместе с каналом."),
            text=прежнее,
        )
        if not согласие:
            return

        ответ = self.source.rename_channel(номер, новое)
        self.каналы_ответ.setText(ответ.text)
        if ответ.ok:
            self._перечитать_каналы()
            self._обновить_таблицу()

    def _убрать_канал(self) -> None:
        строки = self.список_каналов.selectionModel().selectedRows()
        if not строки:
            return
        номер = строки[0].row()
        канал = self._каналы[номер]
        ответ = QMessageBox.question(
            self,
            _("Убрать канал"),
            _('Убрать «{}» из списка?\n\nСкачанное останется на диске и в учёте — канал уходит из очереди, а не из архива. Вернёте обратно — заново качать не станет.').format(канал.name),
        )
        if ответ != QMessageBox.StandardButton.Yes:
            return
        стало = remove_channel(self._каналы, номер)
        self.каналы_ответ.setText(self.source.write_channels(format_channels(стало)).text)
        self._перечитать_каналы()

    def _искать(self) -> None:
        запрос = self.поле_поиска.text().strip()
        if not запрос:
            self.поиск_ответ.setText(_("введите название"))
            return
        if self._поиск is not None and self._поиск.isRunning():
            self._поиск.бросить()

        self.находки.setRowCount(0)
        self._находки = []
        self.кнопка_добавить.setEnabled(False)
        self.кнопка_искать.setEnabled(False)
        self.поиск_ответ.setText(_("ищу…"))

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
        подпись = {None: "…", True: _("да"), False: _("НЕ ВЛЕЗЕТ")}[влезет]

        значок = QTableWidgetItem("")
        from runner.avatars import cached_avatar

        путь = cached_avatar(self.source.avatars_dir, кандидат.channel_id)
        if путь is not None:
            значок.setIcon(QIcon(str(путь)))
        self.находки.setItem(номер, 0, значок)
        self.находки.setRowHeight(номер, 38)

        for сдвиг, значение in enumerate((кандидат.name, кандидат.describe(_), подпись)):
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
                _("Может не влезть"),
                _('По верхней оценке «{}» займёт больше, чем есть свободного места.\n\n{}\n\nВсё равно добавить?').format(кандидат.name, кандидат.describe(_)),
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
            беды = "; ".join(_('строка {}: {}').format(p.line_number, p.reason) for p in разбор.problems)
            self.каналы_ответ.setText(_('в файле есть непонятые строки — {}').format(беды))

        по_папкам = {имя: (файлов, байт) for имя, файлов, байт in self.source.channel_stats()}
        self.список_каналов.setRowCount(len(self._каналы))
        for номер, канал in enumerate(self._каналы):
            файлов, байт = по_папкам.get(канал.name, (0, 0))
            значок = QTableWidgetItem("")
            путь = self.source.avatar(канал.name)
            if путь is not None:
                значок.setIcon(QIcon(str(путь)))
            self.список_каналов.setItem(номер, 0, значок)
            название = QTableWidgetItem(канал.name)
            if канал.rules:
                # Правило невидимо, пока не откроешь окно: без подсказки человек
                # будет гадать, почему у канала качается не всё.
                from core.rules import format_rules

                название.setText(f"{канал.name}  ⚙")
                название.setToolTip(_("Правила отбора: {}").format(format_rules(канал.rules)))
            self.список_каналов.setItem(номер, 1, название)
            self.список_каналов.setItem(номер, 2, QTableWidgetItem(str(файлов) if файлов else "—"))
            self.список_каналов.setItem(
                номер, 3, QTableWidgetItem(_('{:.1f} ГБ').format(байт / 1024**3) if байт else "—")
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

        ряд_папки = QHBoxLayout()
        self.поле_папка = QLineEdit()
        # Только чтение: папку выбирают в проводнике, а не набирают руками.
        # Опечатка здесь означает архив, начатый с нуля.
        self.поле_папка.setReadOnly(True)
        self.кнопка_обзор = QPushButton(_("Обзор…"))
        ряд_папки.addWidget(self.поле_папка, 1)
        ряд_папки.addWidget(self.кнопка_обзор)
        обёртка = QWidget()
        обёртка.setLayout(ряд_папки)
        форма.addRow(_("Рабочая папка:"), обёртка)

        self.поле_язык = QComboBox()
        # Системный — первым и по умолчанию: чужой язык на первом запуске
        # хуже отсутствия выбора. В скобках — что это на деле означает,
        # иначе человеку остаётся гадать.
        self.поле_язык.addItem(
            _("Системный язык — {}").format(
                НАЗВАНИЯ.get(нормализовать(системный_язык()), "?")
            ),
            СИСТЕМНЫЙ,
        )
        for код in [ИСХОДНЫЙ, *sorted(КАТАЛОГИ)]:
            self.поле_язык.addItem(НАЗВАНИЯ.get(код, код), код)
        форма.addRow(_("Язык:"), self.поле_язык)

        self.поле_качество = QComboBox()
        for h in ALLOWED_HEIGHTS:
            self.поле_качество.addItem(_('до {}p').format(h), h)
        self.поле_av1 = QCheckBox(_("Предпочитать AV1 (тот же вид, файл меньше)"))
        self.поле_субтитры = QCheckBox(_("Забирать субтитры"))
        self.поле_молчание = QSpinBox()
        self.поле_молчание.setRange(60, 3600)
        self.поле_молчание.setSuffix(_(" с"))
        self.поле_пауза_мин = QSpinBox()
        self.поле_пауза_мин.setRange(0, 600)
        self.поле_пауза_мин.setSuffix(_(" с"))
        self.поле_пауза_макс = QSpinBox()
        self.поле_пауза_макс.setRange(0, 600)
        self.поле_пауза_макс.setSuffix(_(" с"))

        self.поле_куки = QComboBox()
        self.поле_куки.addItem(_("из файла cookies.txt"), "")
        for браузер in BROWSERS:
            self.поле_куки.addItem(_("из браузера {}").format(браузер.capitalize()), браузер)
        self.поле_скорость = QSpinBox()
        self.поле_скорость.setRange(0, 10_000_000)
        self.поле_скорость.setSingleStep(256)
        self.поле_скорость.setSuffix(_(" КиБ/с"))
        self.поле_скорость.setSpecialValueText(_("без потолка"))
        self.поле_ползёт = QSpinBox()
        self.поле_ползёт.setRange(0, 1_000_000)
        self.поле_ползёт.setSingleStep(10)
        self.поле_ползёт.setSuffix(_(" КиБ/с"))
        self.поле_ползёт.setSpecialValueText(_("не проверять"))
        self.поле_часы = QLineEdit()
        self.поле_часы.setPlaceholderText(_("23-7 или 23:00-07:30 — пусто: всегда"))

        форма.addRow(_("Качество:"), self.поле_качество)
        форма.addRow("", self.поле_av1)
        форма.addRow("", self.поле_субтитры)
        форма.addRow(_("Считать зависшим после:"), self.поле_молчание)
        форма.addRow(_("Пауза между роликами, от:"), self.поле_пауза_мин)
        форма.addRow(_("до:"), self.поле_пауза_макс)
        форма.addRow(_("Куки YouTube:"), self.поле_куки)
        форма.addRow(_("Потолок скорости:"), self.поле_скорость)
        форма.addRow(_("Откладывать загрузку медленнее:"), self.поле_ползёт)
        форма.addRow(_("Часы работы:"), self.поле_часы)
        столбец.addLayout(форма)

        про_папку = QLabel(
            _("Рабочая папка — это и склад роликов, и учёт скачанного. Смена "
            "папки ничего не переносит: новая папка начинается с того, что "
            "в ней уже лежит. Выкачка перейдёт на неё со следующего прохода.")
        )
        про_папку.setWordWrap(True)
        про_папку.setStyleSheet("color: #666;")
        столбец.addWidget(про_папку)

        подсказка = QLabel(
            _("Паузы между роликами берегут доступ: на потоке в тысячи запросов "
            "YouTube начинает отвечать «подтвердите, что вы не бот». "
            "Предел молчания должен быть заметно больше самой длинной паузы, "
            "иначе живую выкачку будут убивать как зависшую.")
        )
        подсказка.setWordWrap(True)
        подсказка.setStyleSheet("color: #666;")
        столбец.addWidget(подсказка)

        ряд = QHBoxLayout()
        сохранить = QPushButton(_("Сохранить настройки"))
        вернуть = QPushButton(_("Вернуть как было"))
        ряд.addWidget(сохранить)
        ряд.addWidget(вернуть)
        ряд.addStretch(1)
        self.настройки_ответ = QLabel("")
        self.настройки_ответ.setStyleSheet("color: #666;")
        ряд.addWidget(self.настройки_ответ)
        столбец.addLayout(ряд)

        # --- уход за архивом ---
        столбец.addWidget(QLabel(_("Уход за архивом:")))
        ряд_ухода = QHBoxLayout()
        обновить_ytdlp = QPushButton(_("Обновить yt-dlp"))
        сверить = QPushButton(_("Сверить учёт с диском"))
        убрать = QPushButton(_("Убрать старое…"))
        убрать.setToolTip(_("Старые журналы и обломки загрузок. Сначала покажет, что уберёт."))
        for кнопка in (обновить_ytdlp, сверить, убрать):
            ряд_ухода.addWidget(кнопка)
        ряд_ухода.addStretch(1)
        столбец.addLayout(ряд_ухода)
        обновить_ytdlp.clicked.connect(
            lambda: self._команда(_("Обновление yt-dlp"), ("update",))
        )
        сверить.clicked.connect(
            lambda: self._команда(
                _("Сверка учёта с диском"), ("verify",),
                применить=("verify", "--apply"), подпись=_("Убрать повторные строки"),
            )
        )
        убрать.clicked.connect(
            lambda: self._команда(
                _("Что можно убрать"), ("clean",),
                применить=("clean", "--apply"), подпись=_("Убрать показанное"),
            )
        )
        столбец.addStretch(1)

        сохранить.clicked.connect(self._сохранить_настройки)
        вернуть.clicked.connect(self._перечитать_настройки)
        self.кнопка_обзор.clicked.connect(self._выбрать_папку)
        self._перечитать_настройки()
        return корень

    def _команда(self, заголовок: str, доводы: tuple, *, применить: tuple = (), подпись: str = "") -> None:
        from gui.upkeep import ОкноКоманды

        ОкноКоманды(
            self.source.config_path, заголовок, доводы,
            применить=применить, подпись_применить=подпись, parent=self,
        ).exec()

    def _выбрать_папку(self) -> None:
        """Выбрать рабочую папку. Согласие спрашивается словами о последствиях:
        учёт скачанного лежит внутри папки, и пустая означает всё заново.
        """
        from pathlib import Path

        from PySide6.QtWidgets import QFileDialog

        выбор = QFileDialog.getExistingDirectory(
            self, _("Куда складывать архив"), self.поле_папка.text()
        )
        if not выбор:
            return

        осмотр = self.source.check_folder(Path(выбор))
        if not осмотр.ok:
            QMessageBox.warning(self, _("Эта папка не подойдёт"), осмотр.reason)
            return

        ответ = QMessageBox.question(
            self,
            _("Сменить рабочую папку?"),
            _('{}\n\n{}\n\nСменить?').format(выбор, осмотр.warning),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ответ != QMessageBox.StandardButton.Yes:
            return

        self.поле_папка.setText(str(Path(выбор)))
        self.настройки_ответ.setText(_("папка сменится при сохранении"))

    def _перечитать_настройки(self) -> None:
        try:
            config = parse_config(loads(self.source.config_text()))
        except (ConfigError, Exception) as ошибка:  # noqa: BLE001
            self.настройки_ответ.setText(_('настройки не читаются: {}').format(ошибка))
            return
        self._config = config
        self.поле_папка.setText(config.paths.base)
        место = self.поле_язык.findData(config.language)
        self.поле_язык.setCurrentIndex(место if место >= 0 else 0)
        self.поле_качество.setCurrentIndex(ALLOWED_HEIGHTS.index(config.height))
        self.поле_av1.setChecked(config.prefer_av1)
        self.поле_субтитры.setChecked(config.write_subs)
        self.поле_молчание.setValue(int(config.limits.silence_limit))
        self.поле_пауза_мин.setValue(config.limits.sleep_min)
        self.поле_пауза_макс.setValue(config.limits.sleep_max)
        место = self.поле_куки.findData(config.cookies_browser)
        self.поле_куки.setCurrentIndex(место if место >= 0 else 0)
        self.поле_скорость.setValue(config.rate_limit)
        self.поле_ползёт.setValue(config.limits.crawl_speed)
        self.поле_часы.setText(format_hours(config.hours))
        self.настройки_ответ.setText("")

    def _сохранить_настройки(self) -> None:
        from dataclasses import replace

        try:
            часы = parse_hours(self.поле_часы.text())
        except ValueError as ошибка:
            QMessageBox.warning(self, _("Не сохранил"), str(ошибка))
            self.настройки_ответ.setText(_("не сохранено"))
            return
        пределы = replace(
            self._config.limits,
            silence_limit=float(self.поле_молчание.value()),
            sleep_min=self.поле_пауза_мин.value(),
            sleep_max=self.поле_пауза_макс.value(),
            crawl_speed=self.поле_ползёт.value(),
        )
        пути = replace(self._config.paths, base=self.поле_папка.text())
        язык_сменился = self.поле_язык.currentData() != self._config.language
        сменилась = пути.base != self._config.paths.base
        новый = replace(
            self._config,
            paths=пути,
            language=self.поле_язык.currentData(),
            height=self.поле_качество.currentData(),
            prefer_av1=self.поле_av1.isChecked(),
            write_subs=self.поле_субтитры.isChecked(),
            limits=пределы,
            cookies_browser=self.поле_куки.currentData(),
            rate_limit=self.поле_скорость.value(),
            hours=часы,
        )
        текст = dump_config(новый)
        try:
            # Проверяем то, что собираемся записать: испорченные настройки
            # оставят выкачку без запуска, а человека — без объяснения.
            parse_config(loads(текст))
        except (ConfigError, Exception) as ошибка:  # noqa: BLE001
            QMessageBox.warning(self, _("Не сохранил"), str(ошибка))
            self.настройки_ответ.setText(_("не сохранено"))
            return
        ответ = self.source.write_config(текст)
        self._config = новый
        сообщение = ответ.text
        if язык_сменился and ответ.ok:
            from runner.language import настроить

            настроить(self.поле_язык.currentData())
            # Через singleShot, а не прямо здесь: пересборка удалит ту самую
            # кнопку, из обработчика которой мы сейчас выполняемся. Удалять
            # виджет внутри его же сигнала — верный способ уронить Qt.
            QTimer.singleShot(0, self._язык_сменён)
            сообщение = ""
        if сменилась and ответ.ok:
            # Окно читало старую папку при запуске и продолжит её показывать:
            # умолчать об этом значит показывать вчерашние числа как сегодняшние.
            сообщение = _("папка сменена; окно покажет новую после перезапуска")
            QMessageBox.information(
                self,
                _("Рабочая папка сменена"),
                _("Выкачка перейдёт на новую папку со следующего прохода.\n\n"
                "Это окно показывает прежнюю папку, пока его не перезапустить."),
            )
        self.настройки_ответ.setText(сообщение)

    # --- трей ---------------------------------------------------------------

    def _собрать_трей(self) -> None:
        self.трей = QSystemTrayIcon(нарисовать_значок(ЦВЕТА[RunState.IDLE]), self)
        self.трей.setContextMenu(self._меню_трея())
        self.трей.activated.connect(
            lambda причина: self._показаться()
            if причина == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
        self.трей.show()

    def _меню_трея(self) -> QMenu:
        """Меню трея отдельно от значка: при смене языка пересобирается оно,
        а значок остаётся на месте и не мигает."""
        меню = QMenu()
        показать = QAction(_("Показать окно"), self)
        пуск = QAction(_("Запустить выкачку"), self)
        стоп = QAction(_("Остановить выкачку"), self)
        выход = QAction(_("Выйти"), self)
        показать.triggered.connect(self._показаться)
        пуск.triggered.connect(self._пуск)
        стоп.triggered.connect(self._стоп)
        выход.triggered.connect(self._выйти)
        for пункт in (показать, пуск, стоп):
            меню.addAction(пункт)
        меню.addSeparator()
        меню.addAction(выход)
        # Меню держим за окном: без ссылки Qt соберёт его мусорщиком,
        # и щелчок по трею откроет пустоту.
        self._меню = меню
        return меню

    def _язык_сменён(self) -> None:
        """Пересобрать окно и сказать об этом уже на новом языке."""
        self.перестроить()
        self.настройки_ответ.setText(_("язык сменён"))

    def перестроить(self) -> None:
        """Собрать окно заново — например, после смены языка.

        Именно пересобрать, а не переписать подписи по одной. Переписывание
        неизбежно что-нибудь пропускает, и пропущенное молча остаётся на
        прежнем языке: заметит это не разработчик, а человек, которому
        неудобно. Пересборка промахнуться не может.

        Окно, положение и потоки остаются те же — меняется только его нутро.
        """
        вкладка = self.вкладки.currentIndex()

        self.setWindowTitle(_("Архив YouTube"))
        прежние = self.centralWidget()

        self.вкладки = QTabWidget()
        self.вкладки.addTab(self._вкладка_обзор(), _("Обзор"))
        self.вкладки.addTab(self._вкладка_каналы(), _("Каналы"))
        self.вкладки.addTab(self._вкладка_настройки(), _("Настройки"))
        self.setCentralWidget(self.вкладки)

        # Прежнее дерево приходится убирать руками: сам по себе setCentralWidget
        # его не удаляет, а оставляет ребёнком окна. Проверено — после смены
        # языка в окне оказалось двадцать четыре подписи вместо двенадцати,
        # немецкие вперемешку с русскими. На каждой смене копилась бы копия.
        if прежние is not None:
            прежние.setParent(None)
            прежние.deleteLater()
        self.вкладки.setCurrentIndex(вкладка)

        self.трей.setContextMenu(self._меню_трея())
        self._последний_журнал = ""  # перерисовать журнал целиком
        self.обновить()

    def _показаться(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _дождаться_потоков(self) -> None:
        """Дождаться фоновой работы перед уходом.

        Живой поток в момент уничтожения окна Qt считает ошибкой и
        обрывает процесс — без сообщения, что особенно неприятно.
        """
        from gui.videos import _отпустить, дождаться_доживающих

        for поток in (self._поиск, self._логотипы):
            _отпустить(поток)
        self._поиск = None
        self._логотипы = None
        # Потоки, отпущенные закрытым окном роликов, тоже наши: при выходе
        # разрушается всё, и живой поток снова обрубил бы концы.
        дождаться_доживающих()

    def _выйти(self) -> None:
        self._дождаться_потоков()
        self.трей.hide()
        QApplication.instance().quit()

    def closeEvent(self, event) -> None:  # noqa: N802 — имя задано Qt
        """Закрытие прячет окно, а не выходит.

        Выкачка от этого не зависит вовсе — её ведёт отдельный процесс. Но человек,
        закрывший окно, ожидает найти программу в трее, а не гадать,
        осталась ли она.
        """
        event.ignore()
        self.hide()
        if not self._предупредили_о_трее:
            self.трей.showMessage(
                _("Архив YouTube"),
                _("Окно свёрнуто в трей. Выкачка идёт сама и от окна не зависит."),
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )
            self._предупредили_о_трее = True

    # --- обновление ---------------------------------------------------------

    def обновить(self) -> None:
        строки = self.source.log_tail(TAIL_LINES)
        архив = parse_archive(self.source.archive_text())
        живое = self.source.live_state()
        снимок = build_status(
            process_running=self.source.download_running(),
            archive_count=len(архив),
            live=живое,
        )

        self.заголовок.setText(снимок.headline(_))
        self.заголовок.setStyleSheet(f"color: {ЦВЕТА[снимок.state]};")

        # «Работает» и «качает прямо сейчас» — разные вещи: между проходами
        # обход жив и ждёт. Не различив их, окно предлагало бы запустить
        # уже запущенное.
        обход_работает = self.source.worker_running()

        части = [
            _("обход работает") if обход_работает else _("обход не запущен"),
            _('в архиве {} роликов').format(снимок.archive_count),
        ]
        if снимок.channel:
            части.append(_('канал {}').format(снимок.channel))
        if снимок.last_size_bytes and снимок.last_speed_bps:
            части.append(
                _('последний файл {:.0f} МБ, {:.1f} МБ/с').format(снимок.last_size_bytes / 1024**2, снимок.last_speed_bps / 1024**2)
            )
        if снимок.errors:
            части.append(_('отказов в этом сеансе {} — заберутся следующим проходом').format(снимок.errors))
        self.подпись.setText(" · ".join(части))

        self._обновить_полосы(снимок)

        self.кнопка_пуск.setEnabled(not обход_работает)
        self.кнопка_стоп.setEnabled(обход_работает)

        # Беда, требующая человека, говорится всплывающим сообщением: окно
        # обычно свёрнуто в трей, и «истекли куки» в заголовке никто не видит —
        # выкачка могла стоять днями.
        беда = (живое.stopped_reason if живое else "") or ""
        if is_new_trouble(self._сказанная_беда, беда):
            self.трей.showMessage(
                _("Архив YouTube — нужен человек"),
                _(беда),
                QSystemTrayIcon.MessageIcon.Warning,
                15000,
            )
        self._сказанная_беда = беда

        self.трей.setIcon(нарисовать_значок(ЦВЕТА[снимок.state]))
        self.трей.setToolTip(_('Архив YouTube — {}').format(снимок.headline(_)))

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
                части.append(_('{:.0f} МБ').format(живое.size_bytes / 1024**2))
            if живое.speed_bps:
                части.append(_('{:.1f} МБ/с').format(живое.speed_bps / 1024**2))
            if живое.eta:
                части.append(_('осталось {}').format(живое.eta))
            self.подпись_файла.setText(" · ".join(части))

        показать_канал = bool(живое and живое.item_total)
        self.полоса_канала.setVisible(показать_канал)
        self.подпись_канала.setVisible(показать_канал)
        if показать_канал:
            self.полоса_канала.setValue(int(живое.item_fraction() * 100))
            подпись = _('{}: ролик {} из {}').format(живое.channel, живое.item_index, живое.item_total)
            if живое.channel_total:
                подпись += _(' · канал {} из {}').format(живое.channel_index, живое.channel_total)
            self.подпись_канала.setText(подпись)

    def _обновить_таблицу(self) -> None:
        строки = self.source.channel_stats()
        if self.таблица.rowCount() != len(строки):
            self.таблица.setRowCount(len(строки))
        for номер, (имя, файлов, байт) in enumerate(строки):
            значения = (имя, str(файлов), _('{:.2f} ГБ').format(байт / 1024**3))
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
        _проверить_окно_роликов(source)
        app.processEvents()
        окно._дождаться_потоков()
        окно.трей.hide()
        return 0
    return app.exec()


def _проверить_окно_роликов(source: ArchiveSource) -> None:
    """Построить окно выбора на выдуманной переписи, не выходя в сеть.

    Именно так ловились обе прошлые беды интерфейса — живой поток в момент
    разрушения окна и упавший обработчик. Сеть здесь не нужна: перепись
    подставляется руками, а рисование идёт то же самое.
    """
    from core.videos import Listing, Video
    from gui.videos import ОкноРоликов

    окно = ОкноРоликов(source, "проверка", фоновые=False)
    окно._перепись_готова(
        Listing(
            videos=(
                Video("aaaaaaaaaaa", "Первый ролик", 2796),
                Video("bbbbbbbbbbb", "Второй ролик | со чертой", 0),
            )
        )
    )
    окно.поиск.setText("второй")
    окно._всем_галочку(False)
    окно.поиск.setText("")
    окно._показать_предпросмотр()
    окно._дождаться_потоков()
    окно.deleteLater()

    from core.rules import Rules
    from gui.upkeep import ОкноКоманды, ОкноПравил

    правила = ОкноПравил("проверка", Rules(min_seconds=60, after="20240101"))
    assert правила.собрать() == Rules(min_seconds=60, after="20240101")
    правила.deleteLater()
    # Команду не запускаем: самопроверка не должна ничего трогать на диске.
    команда = ОкноКоманды(
        source.config_path, "проверка", ("clean",), применить=("clean", "--apply"), запустить=False
    )
    команда.done(0)
    команда.deleteLater()
