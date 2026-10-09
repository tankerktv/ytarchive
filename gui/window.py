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
    QFrame,
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
    QScrollArea,
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
from core.status import Hint, RunState, build_status, is_new_trouble, next_hint, size_parts
from core.ytdlp_args import ALLOWED_HEIGHTS
from gui.logo import значок
from gui.source import ArchiveSource
from core.videos import title_from_filename
from gui.style import ЖЁЛТЫЙ, ЗЕЛЁНЫЙ, КРАСНЫЙ, СЕРЫЙ, СИНИЙ, карточка, плитка, приглушить, применить, роль
from core.i18n import ИСХОДНЫЙ, НАЗВАНИЯ, СИСТЕМНЫЙ, нормализовать
from core.locales import КАТАЛОГИ
from runner.language import _, системный_язык

#: Как часто обновляемся. Журнал разрежен, чаще незачем — а лишние чтения
#: файла с сетевого диска стоят дороже, чем кажется.
REFRESH_MS = 2000
TAIL_LINES = 300

ЦВЕТА = {
    RunState.RUNNING: ЗЕЛЁНЫЙ,
    RunState.BETWEEN: ЖЁЛТЫЙ,
    RunState.WAITING: СИНИЙ,
    RunState.IDLE: СЕРЫЙ,
    RunState.NEEDS_HUMAN: КРАСНЫЙ,
}


def объём_текст(байт: float) -> str:
    """Объём словами, в подходящих единицах."""
    число, единица = size_parts(байт)
    return (_('{:.2f} ТБ') if единица == "tb" else _('{:.1f} ГБ')).format(число)


def нарисовать_значок(цвет: str) -> QIcon:
    """Значок для трея: знак программы на плитке цвета состояния.

    Цвет отвечает состоянию, поэтому по трею видно, идёт ли выкачка,
    не открывая окна. Форма при этом всегда одна — по ней программу узнают.
    """
    return значок(цвет)


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
        # В заголовке и на панели задач — фирменный цвет: он не меняется,
        # и по нему окно находят среди прочих. Цвет состояния — только в трее.
        self.setWindowIcon(значок())
        self.resize(980, 720)

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
        столбец.setContentsMargins(18, 16, 18, 16)
        столбец.setSpacing(12)

        # --- состояние и главная кнопка ---
        # Кнопка одна: показывается та, что сейчас имеет смысл. Две рядом, из
        # которых одна всегда серая, заставляют каждый раз читать обе.
        карта, внутри = карточка()
        ряд = QHBoxLayout()
        ряд.setSpacing(10)
        self.точка = QLabel("")
        self.точка.setFixedSize(14, 14)
        self.заголовок = роль(QLabel(_("читаю состояние…")), "title")
        self.заголовок.setWordWrap(True)
        self.кнопка_пуск = QPushButton(_("Запустить"))
        self.кнопка_пуск.setObjectName("primary")
        self.кнопка_стоп = QPushButton(_("Остановить"))
        ряд.addWidget(self.точка)
        ряд.addWidget(self.заголовок, 1)
        ряд.addWidget(self.кнопка_пуск)
        ряд.addWidget(self.кнопка_стоп)
        внутри.addLayout(ряд)

        self.подпись = приглушить(QLabel(""))
        self.подпись.setWordWrap(True)
        внутри.addWidget(self.подпись)
        столбец.addWidget(карта)

        self.кнопка_пуск.clicked.connect(self._пуск)
        self.кнопка_стоп.clicked.connect(self._стоп)

        # --- подсказка: чего не хватает, чтобы начать ---
        self.карта_подсказки, внутри = карточка("hint")
        ряд = QHBoxLayout()
        self.текст_подсказки = QLabel("")
        self.текст_подсказки.setWordWrap(True)
        self.кнопка_подсказки = QPushButton("")
        ряд.addWidget(self.текст_подсказки, 1)
        ряд.addWidget(self.кнопка_подсказки)
        внутри.addLayout(ряд)
        self.карта_подсказки.setVisible(False)
        self.кнопка_подсказки.clicked.connect(self._по_подсказке)
        self._подсказка = None
        столбец.addWidget(self.карта_подсказки)

        # --- числа ---
        ряд_плиток = QHBoxLayout()
        ряд_плиток.setSpacing(12)
        self.плитки: dict[str, QLabel] = {}
        for ключ, название in (
            ("ролики", _("роликов в архиве")),
            ("объём", _("объём архива")),
            ("место", _("свободно на диске")),
            ("каналы", _("каналов в списке")),
        ):
            рамка, значение = плитка(название)
            self.плитки[ключ] = значение
            ряд_плиток.addWidget(рамка, 1)
        столбец.addLayout(ряд_плиток)

        # --- что качается сейчас ---
        # Показывается, только когда есть что показывать: пустая полоса на нуле
        # выглядит как застрявшая работа и тревожит на ровном месте.
        self.карта_сейчас, внутри = карточка()
        self.подпись_файла = QLabel("")
        self.подпись_файла.setWordWrap(True)
        self.полоса_файла = QProgressBar()
        self.полоса_файла.setTextVisible(False)
        self.подпись_канала = приглушить(QLabel(""))
        self.полоса_канала = QProgressBar()
        self.полоса_канала.setTextVisible(False)
        for виджет in (
            self.подпись_файла, self.полоса_файла, self.подпись_канала, self.полоса_канала
        ):
            внутри.addWidget(виджет)
        self.карта_сейчас.setVisible(False)
        столбец.addWidget(self.карта_сейчас)

        # --- журнал ---
        ряд = QHBoxLayout()
        ряд.addWidget(роль(QLabel(_("Журнал")), "section"))
        ряд.addStretch(1)
        self.кнопка_журнал = QPushButton(_("Скрыть"))
        self.кнопка_журнал.setFlat(True)
        ряд.addWidget(self.кнопка_журнал)
        столбец.addLayout(ряд)

        self.журнал = QPlainTextEdit()
        self.журнал.setReadOnly(True)
        self.журнал.setFont(QFont("Consolas", 10))
        self.журнал.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.журнал.setFrameShape(QFrame.Shape.NoFrame)
        столбец.addWidget(self.журнал, 1)
        # Пружина держит верх на месте, когда журнал скрыт: без неё карточки
        # растянулись бы на всё окно.
        self._пружина_обзора = QWidget()
        self._пружина_обзора.setVisible(False)
        столбец.addWidget(self._пружина_обзора, 1)
        self.кнопка_журнал.clicked.connect(self._переключить_журнал)
        return корень

    def _переключить_журнал(self) -> None:
        виден = not self.журнал.isVisible()
        self.журнал.setVisible(виден)
        self._пружина_обзора.setVisible(not виден)
        self.кнопка_журнал.setText(_("Скрыть") if виден else _("Показать"))

    def _по_подсказке(self) -> None:
        """Отвести человека туда, где подсказка исполняется."""
        if self._подсказка is Hint.NO_CHANNELS:
            self.вкладки.setCurrentIndex(1)
            self.поле_поиска.setFocus()
        elif self._подсказка is Hint.NO_COOKIES:
            self.вкладки.setCurrentIndex(2)
            self.поле_куки.setFocus()

    # --- вкладка «Каналы» ---------------------------------------------------

    def _вкладка_каналы(self) -> QWidget:
        корень = QWidget()
        столбец = QVBoxLayout(корень)
        столбец.setContentsMargins(18, 16, 18, 16)
        столбец.setSpacing(12)

        # --- добавить канал ---
        карта, внутри = карточка()
        внутри.addWidget(роль(QLabel(_("Добавить канал")), "section"))
        ряд_поиска = QHBoxLayout()
        self.поле_поиска = QLineEdit()
        self.поле_поиска.setPlaceholderText(_("Название канала — например, alex m"))
        self.поле_поиска.setClearButtonEnabled(True)
        self.кнопка_искать = QPushButton(_("Найти"))
        self.кнопка_искать.setObjectName("primary")
        self.кнопка_по_адресу = QPushButton(_("Добавить по адресу…"))
        self.кнопка_по_адресу.setToolTip(
            _("Плейлист, отдельный ролик или канал, которого нет в поиске.")
        )
        ряд_поиска.addWidget(self.поле_поиска, 1)
        ряд_поиска.addWidget(self.кнопка_искать)
        ряд_поиска.addWidget(self.кнопка_по_адресу)
        внутри.addLayout(ряд_поиска)

        self.поиск_ответ = приглушить(QLabel(""))
        self.поиск_ответ.setWordWrap(True)
        self.поиск_ответ.setVisible(False)
        внутри.addWidget(self.поиск_ответ)

        # Находки появляются только после поиска: пустая таблица на полэкрана
        # ничего не говорит и отнимает место у списка каналов.
        self.находки = QTableWidget(0, 4)
        self.находки.setHorizontalHeaderLabels(["", _("Канал"), _("Объём"), _("Влезет")])
        self.находки.setIconSize(QSize(32, 32))
        self.находки.horizontalHeader().setStretchLastSection(True)
        self.находки.verticalHeader().setVisible(False)
        self.находки.setShowGrid(False)
        self.находки.setColumnWidth(0, 44)
        self.находки.setColumnWidth(1, 260)
        self.находки.setColumnWidth(2, 260)
        self.находки.setMaximumHeight(190)
        self.находки.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.находки.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.находки.setVisible(False)
        внутри.addWidget(self.находки)

        self.кнопка_добавить = QPushButton(_("Добавить выбранный канал"))
        self.кнопка_добавить.setEnabled(False)
        self.кнопка_добавить.setVisible(False)
        внутри.addWidget(self.кнопка_добавить)
        столбец.addWidget(карта)

        self.кнопка_искать.clicked.connect(self._искать)
        self.поле_поиска.returnPressed.connect(self._искать)
        self.находки.itemSelectionChanged.connect(self._выбор_находки)
        self.кнопка_добавить.clicked.connect(self._добавить_находку)
        self.кнопка_по_адресу.clicked.connect(self._добавить_по_адресу)
        self._находки: list = []
        self._поиск = None

        # --- список каналов ---
        столбец.addWidget(роль(QLabel(_("Мои каналы")), "section"))
        про_порядок = приглушить(QLabel(
            _("Список каналов. Порядок здесь — это порядок обхода: верхний "
            "забирается первым.")
        ))
        # С переносом: по-немецки эта строка вдвое длиннее и без него
        # распирала окно до 1250 точек.
        про_порядок.setWordWrap(True)
        столбец.addWidget(про_порядок)

        ряд_списка = QHBoxLayout()
        ряд_списка.setSpacing(12)
        self.список_каналов = QTableWidget(0, 4)
        self.список_каналов.setHorizontalHeaderLabels(["", _("Канал"), _("Файлов"), _("Объём")])
        self.список_каналов.horizontalHeader().setStretchLastSection(True)
        self.список_каналов.setColumnWidth(0, 56)
        self.список_каналов.setColumnWidth(1, 360)
        self.список_каналов.setColumnWidth(2, 90)
        self.список_каналов.verticalHeader().setVisible(False)
        self.список_каналов.setShowGrid(False)
        self.список_каналов.setAlternatingRowColors(True)
        self.список_каналов.setIconSize(QSize(40, 40))
        self.список_каналов.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.список_каналов.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.список_каналов.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        ряд_списка.addWidget(self.список_каналов, 1)

        # Сначала то, что делают с каналом чаще всего; удаление — последним
        # и отдельно, чтобы не попасть в него мимо соседней кнопки.
        кнопки = QVBoxLayout()
        self.кнопка_ролики = QPushButton(_("Выбрать ролики…"))
        self.кнопка_ролики.setToolTip(
            _("Список роликов канала с галочками. По умолчанию отмечены все.")
        )
        self.кнопка_правила = QPushButton(_("Правила…"))
        self.кнопка_правила.setToolTip(
            _("Не короче, не длиннее, не старше — одной строкой вместо сотни галочек.")
        )
        self.кнопка_имя = QPushButton(_("Переименовать…"))
        self.кнопка_имя.setToolTip(_("Сменить название канала вместе с его папкой."))
        self.кнопка_вверх = QPushButton(_("↑ Выше"))
        self.кнопка_вниз = QPushButton(_("↓ Ниже"))
        self.кнопка_убрать = QPushButton(_("Убрать"))
        for к in (self.кнопка_ролики, self.кнопка_правила, self.кнопка_имя):
            к.setEnabled(False)
            кнопки.addWidget(к)
        кнопки.addSpacing(10)
        for к in (self.кнопка_вверх, self.кнопка_вниз):
            к.setEnabled(False)
            кнопки.addWidget(к)
        кнопки.addStretch(1)
        self.кнопка_убрать.setEnabled(False)
        кнопки.addWidget(self.кнопка_убрать)
        ряд_списка.addLayout(кнопки)
        столбец.addLayout(ряд_списка, 1)

        self.каналы_ответ = приглушить(QLabel(""))
        self.каналы_ответ.setWordWrap(True)
        столбец.addWidget(self.каналы_ответ)

        # Папки, которых нет в списке. Именно так выглядел расколотый архив:
        # рядом с `SoyuzUS` молча вырос `Soyuz`. Прежде это было видно по
        # отдельной таблице папок; теперь говорится словами и только когда есть.
        self.чужие_папки = QLabel("")
        self.чужие_папки.setWordWrap(True)
        self.чужие_папки.setStyleSheet(f"color: {ЖЁЛТЫЙ};")
        self.чужие_папки.setVisible(False)
        столбец.addWidget(self.чужие_папки)

        self.кнопка_вверх.clicked.connect(lambda: self._переставить(-1))
        self.кнопка_вниз.clicked.connect(lambda: self._переставить(+1))
        self.кнопка_убрать.clicked.connect(self._убрать_канал)
        self.кнопка_ролики.clicked.connect(self._выбрать_ролики)
        self.кнопка_имя.clicked.connect(self._переименовать_канал)
        self.кнопка_правила.clicked.connect(self._правила_канала)
        self.список_каналов.itemSelectionChanged.connect(self._выбор_канала)
        self.список_каналов.itemDoubleClicked.connect(lambda _ячейка: self._выбрать_ролики())
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
        self.поиск_ответ.setVisible(True)
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
            self.поиск_ответ.setVisible(True)
            return
        if self._поиск is not None and self._поиск.isRunning():
            self._поиск.бросить()

        self.находки.setRowCount(0)
        self._находки = []
        self.кнопка_добавить.setEnabled(False)
        self.кнопка_искать.setEnabled(False)
        self.поиск_ответ.setText(_("ищу…"))
        self.поиск_ответ.setVisible(True)

        self._поиск = ПоискКаналов(self.source, запрос)
        self._поиск.найдено.connect(self._показать_находки)
        self._поиск.измерено.connect(self._обновить_находку)
        self._поиск.закончено.connect(lambda: self.кнопка_искать.setEnabled(True))
        self._поиск.start()

    def _показать_находки(self, кандидаты: list, ответ: str) -> None:
        self._находки = list(кандидаты)
        self.поиск_ответ.setText(ответ)
        self.поиск_ответ.setVisible(bool(ответ))
        self.находки.setVisible(bool(self._находки))
        self.кнопка_добавить.setVisible(bool(self._находки))
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
        self.поиск_ответ.setVisible(True)
        self._перечитать_каналы()

    def _перечитать_каналы(self) -> None:
        разбор = parse_channels(self.source.channels_text())
        self._каналы = list(разбор.channels)

        # Непонятые строки не прячем: иначе человек не узнает, что канал
        # выпал из очереди, а перезапись файла из окна их бы и вовсе стёрла.
        if разбор.problems:
            беды = "; ".join(_('строка {}: {}').format(p.line_number, p.reason) for p in разбор.problems)
            self.каналы_ответ.setText(_('в файле есть непонятые строки — {}').format(беды))

        # Список перечитывают после правки — тут счёт нужен свежий.
        по_папкам = {
            имя: (файлов, байт) for имя, файлов, байт in self.source.channel_stats(fresh=True)
        }
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
                номер, 3, QTableWidgetItem(объём_текст(байт) if байт else "—")
            )
        for номер in range(len(self._каналы)):
            self.список_каналов.setRowHeight(номер, 46)
        self._выбор_канала()

    # --- вкладка «Настройки» ------------------------------------------------

    def _вкладка_настройки(self) -> QWidget:
        # Настроек стало больше, чем помещается в окно, — отсюда прокрутка.
        # Разделы вместо одного длинного столбца: человек ищет «про скорость»,
        # а не восьмую строку сверху.
        корень = QScrollArea()
        корень.setWidgetResizable(True)
        корень.setFrameShape(QFrame.Shape.NoFrame)
        лист = QWidget()
        корень.setWidget(лист)
        столбец = QVBoxLayout(лист)
        столбец.setContentsMargins(18, 16, 18, 16)
        столбец.setSpacing(12)

        формы: list[QFormLayout] = []

        def раздел(название: str) -> QFormLayout:
            карта, внутри = карточка()
            внутри.addWidget(роль(QLabel(название), "section"))
            форма = QFormLayout()
            формы.append(форма)
            форма.setHorizontalSpacing(16)
            форма.setVerticalSpacing(8)
            внутри.addLayout(форма)
            столбец.addWidget(карта)
            форма.пояснить = lambda текст: внутри.addWidget(self._пояснение(текст))
            return форма

        # --- архив ---
        форма = раздел(_("Архив"))
        ряд_папки = QHBoxLayout()
        ряд_папки.setContentsMargins(0, 0, 0, 0)
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
        форма.пояснить(
            _("Рабочая папка — это и склад роликов, и учёт скачанного. Смена "
            "папки ничего не переносит: новая папка начинается с того, что "
            "в ней уже лежит. Выкачка перейдёт на неё со следующего прохода.")
        )

        # --- что качать ---
        форма = раздел(_("Что качать"))
        self.поле_качество = QComboBox()
        for h in ALLOWED_HEIGHTS:
            self.поле_качество.addItem(_('до {}p').format(h), h)
        self.поле_av1 = QCheckBox(_("Предпочитать AV1 (тот же вид, файл меньше)"))
        self.поле_субтитры = QCheckBox(_("Забирать субтитры"))
        self.поле_куки = QComboBox()
        self.поле_куки.addItem(_("из файла cookies.txt"), "")
        for браузер in BROWSERS:
            self.поле_куки.addItem(_("из браузера {}").format(браузер.capitalize()), браузер)
        форма.addRow(_("Качество:"), self.поле_качество)
        форма.addRow("", self.поле_av1)
        форма.addRow("", self.поле_субтитры)
        форма.addRow(_("Куки YouTube:"), self.поле_куки)

        # --- сеть и расписание ---
        форма = раздел(_("Сеть и расписание"))
        self.поле_скорость = QSpinBox()
        self.поле_скорость.setRange(0, 10_000_000)
        self.поле_скорость.setSingleStep(256)
        self.поле_скорость.setSuffix(_(" КиБ/с"))
        self.поле_скорость.setSpecialValueText(_("без потолка"))
        self.поле_часы = QLineEdit()
        self.поле_часы.setPlaceholderText(_("23-7 или 23:00-07:30 — пусто: всегда"))
        self.поле_ползёт = QSpinBox()
        self.поле_ползёт.setRange(0, 1_000_000)
        self.поле_ползёт.setSingleStep(10)
        self.поле_ползёт.setSuffix(_(" КиБ/с"))
        self.поле_ползёт.setSpecialValueText(_("не проверять"))
        форма.addRow(_("Потолок скорости:"), self.поле_скорость)
        форма.addRow(_("Часы работы:"), self.поле_часы)
        форма.addRow(_("Откладывать загрузку медленнее:"), self.поле_ползёт)

        # --- осторожность ---
        форма = раздел(_("Осторожность"))
        self.поле_молчание = QSpinBox()
        self.поле_молчание.setRange(60, 3600)
        self.поле_молчание.setSuffix(_(" с"))
        self.поле_пауза_мин = QSpinBox()
        self.поле_пауза_мин.setRange(0, 600)
        self.поле_пауза_мин.setSuffix(_(" с"))
        self.поле_пауза_макс = QSpinBox()
        self.поле_пауза_макс.setRange(0, 600)
        self.поле_пауза_макс.setSuffix(_(" с"))
        форма.addRow(_("Считать зависшим после:"), self.поле_молчание)
        форма.addRow(_("Пауза между роликами, от:"), self.поле_пауза_мин)
        форма.addRow(_("до:"), self.поле_пауза_макс)
        форма.пояснить(
            _("Паузы между роликами берегут доступ: на потоке в тысячи запросов "
            "YouTube начинает отвечать «подтвердите, что вы не бот». "
            "Предел молчания должен быть заметно больше самой длинной паузы, "
            "иначе живую выкачку будут убивать как зависшую.")
        )

        # Подписи во всех разделах — одной ширины: иначе у каждого раздела
        # поля начинаются со своего места, и столбец выглядит изломанным.
        подписи = [
            форма.itemAt(строка, QFormLayout.ItemRole.LabelRole).widget()
            for форма in формы
            for строка in range(форма.rowCount())
            if форма.itemAt(строка, QFormLayout.ItemRole.LabelRole) is not None
        ]
        ширина = max((подпись.sizeHint().width() for подпись in подписи), default=0)
        for подпись in подписи:
            подпись.setMinimumWidth(ширина)

        ряд = QHBoxLayout()
        сохранить = QPushButton(_("Сохранить настройки"))
        сохранить.setObjectName("primary")
        вернуть = QPushButton(_("Вернуть как было"))
        ряд.addWidget(сохранить)
        ряд.addWidget(вернуть)
        self.настройки_ответ = приглушить(QLabel(""))
        ряд.addWidget(self.настройки_ответ, 1)
        столбец.addLayout(ряд)

        # --- уход за архивом ---
        карта, внутри = карточка()
        внутри.addWidget(роль(QLabel(_("Уход за архивом")), "section"))
        ряд_ухода = QHBoxLayout()
        обновить_ytdlp = QPushButton(_("Обновить yt-dlp"))
        сверить = QPushButton(_("Сверить учёт с диском"))
        убрать = QPushButton(_("Убрать старое…"))
        убрать.setToolTip(_("Старые журналы и обломки загрузок. Сначала покажет, что уберёт."))
        for кнопка in (обновить_ytdlp, сверить, убрать):
            ряд_ухода.addWidget(кнопка)
        ряд_ухода.addStretch(1)
        внутри.addLayout(ряд_ухода)
        столбец.addWidget(карта)
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

    @staticmethod
    def _пояснение(текст: str) -> QLabel:
        надпись = приглушить(QLabel(текст))
        надпись.setWordWrap(True)
        return надпись

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
        # «Работает» и «качает прямо сейчас» — разные вещи: между проходами
        # обход жив и ждёт. Не различив их, окно предлагало бы запустить
        # уже запущенное.
        обход_работает = self.source.worker_running()
        снимок = build_status(
            process_running=self.source.download_running(),
            archive_count=len(архив),
            live=живое,
            worker_running=обход_работает,
        )

        цвет = ЦВЕТА[снимок.state]
        self.заголовок.setText(снимок.title(_))
        self.точка.setStyleSheet(f"background: {цвет}; border-radius: 7px;")
        # Цветом пишем только беду. Обычное состояние — обычным текстом:
        # серый заголовок «не запущена» на тёмной теме был почти не виден,
        # а цвет состояния и так несёт точка рядом.
        self.заголовок.setStyleSheet(
            f"color: {цвет};" if снимок.state is RunState.NEEDS_HUMAN else ""
        )

        части = [_("обход работает") if обход_работает else _("обход не запущен")]
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

        for кнопка, нужна in ((self.кнопка_пуск, not обход_работает), (self.кнопка_стоп, обход_работает)):
            кнопка.setEnabled(нужна)
            кнопка.setVisible(нужна)

        папки = self.source.channel_stats()
        self.плитки["ролики"].setText(f"{снимок.archive_count:,}".replace(",", "\u202f"))
        всего_байт = sum(байт for _имя, _файлов, байт in папки)
        self.плитки["объём"].setText(объём_текст(всего_байт) if всего_байт else "—")
        свободно = self.source.free_bytes()
        self.плитки["место"].setText(объём_текст(свободно) if свободно else "—")
        self.плитки["каналы"].setText(str(len(self._каналы)))

        self._обновить_подсказку()

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

        self.трей.setIcon(нарисовать_значок(цвет))
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

        self._обновить_числа(папки)

    def _обновить_подсказку(self) -> None:
        """Показать, чего не хватает, чтобы выкачка могла начаться."""
        подсказка = next_hint(channels=len(self._каналы), has_cookies=self.source.has_cookies())
        self._подсказка = подсказка
        self.карта_подсказки.setVisible(подсказка is not None)
        if подсказка is Hint.NO_CHANNELS:
            self.текст_подсказки.setText(
                _("Каналов пока нет. Добавьте первый — программа покажет, сколько в нём "
                  "роликов и хватит ли места, ещё до того, как начнёт качать.")
            )
            self.кнопка_подсказки.setText(_("Добавить канал"))
        elif подсказка is Hint.NO_COOKIES:
            self.текст_подсказки.setText(
                _("YouTube не отдаёт ролики без входа в аккаунт. Выберите в настройках "
                  "браузер, в котором вы вошли в YouTube, или положите файл cookies.txt.")
            )
            self.кнопка_подсказки.setText(_("Открыть настройки"))

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
            части = [title_from_filename(живое.file_name), f"{живое.percent:.0f}%"]
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

        self.карта_сейчас.setVisible(показать_файл or показать_канал)

    def _обновить_числа(self, папки: list) -> None:
        """Обновить счёт файлов в списке каналов и назвать папки не из списка."""
        по_папкам = {имя: (файлов, байт) for имя, файлов, байт in папки}
        for номер, канал in enumerate(self._каналы):
            файлов, байт = по_папкам.get(канал.name, (0, 0))
            for столбец, значение in (
                (2, str(файлов) if файлов else "—"),
                (3, объём_текст(байт) if байт else "—"),
            ):
                ячейка = self.список_каналов.item(номер, столбец)
                if ячейка is not None and ячейка.text() != значение:
                    ячейка.setText(значение)

        свои = {канал.name for канал in self._каналы}
        чужие = [имя for имя, файлов, _байт in папки if имя not in свои and файлов]
        self.чужие_папки.setVisible(bool(чужие))
        if чужие:
            self.чужие_папки.setText(
                _("В папке архива лежат ролики в папках, которых нет в списке: {}. "
                  "Так выглядит канал, переименованный в файле руками.").format(", ".join(чужие))
            )

    # --- кнопки -------------------------------------------------------------

    def _пуск(self) -> None:
        self.подпись.setText(self.source.start())
        self.обновить()

    def _стоп(self) -> None:
        self.подпись.setText(self.source.stop())
        self.обновить()


def _назваться_системе() -> None:
    """Сказать Windows, что это отдельная программа, а не «Python».

    Без этого панель задач группирует окно с интерпретатором и рисует его
    значок — змею вместо знака программы, что бы ни было задано окну.
    Делается до создания окна; на других системах не нужно.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ytarchive.window")
    except (AttributeError, OSError):
        pass  # значок на панели задач — не повод не открыть окно


def run(source: ArchiveSource, *, selftest: bool = False) -> int:
    _назваться_системе()
    app = QApplication.instance() or QApplication(sys.argv)
    app.setWindowIcon(значок())

    # Окно уже открыто (скорее всего, спрятано в трей) — просим его показаться
    # и уходим. Самопроверку это не касается: она строит окно и сразу выходит.
    from gui.single import имя_соединения, попросить_показаться, слушать

    имя = имя_соединения(source.config_path)
    if not selftest and попросить_показаться(имя):
        return 0

    # Без этого закрытие окна завершило бы программу вместе с треем.
    app.setQuitOnLastWindowClosed(False)
    применить(app)
    окно = Window(source, фоновые=not selftest)
    if not selftest:
        окно._одно_окно = слушать(имя, окно._показаться, окно)
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
