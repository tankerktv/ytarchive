"""Вкладка «Библиотека»: скачанное по всем каналам, с поиском и просмотром.

Программа умела скачать, но не помогала смотреть: найти ролик значило идти
в проводник и листать папку на шестьсот файлов.

Решения — что считать роликом, что подходит под отбор — принимает
`core.library`. Здесь только Qt: показать и открыть.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QSize, Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.library import description_from_tags, matches
from core.status import size_parts
from gui.style import ЖЁЛТЫЙ, приглушить
from runner.language import _

МИНИАТЮРА = QSize(96, 54)
ПРЕДПРОСМОТР = QSize(304, 171)

СТОЛБЕЦ_КАРТИНКА, СТОЛБЕЦ_НАЗВАНИЕ, СТОЛБЕЦ_КАНАЛ, СТОЛБЕЦ_ДАТА, СТОЛБЕЦ_РАЗМЕР = range(5)


class _Число(QTableWidgetItem):
    """Ячейка, которая упорядочивается по числу, а не по тексту: иначе
    «9.5 ГБ» оказалось бы больше, чем «10.2 ГБ»."""

    def __init__(self, текст: str, число: float) -> None:
        super().__init__(текст)
        self.число = число

    def __lt__(self, другая) -> bool:
        return self.число < getattr(другая, "число", 0)


def объём(байт: float) -> str:
    число, единица = size_parts(байт)
    if единица == "tb":
        return _('{:.2f} ТБ').format(число)
    if число < 1:
        return _('{:.0f} МБ').format(байт / 1024**2)
    return _('{:.1f} ГБ').format(число)


class ВкладкаБиблиотека(QWidget):
    def __init__(self, source, parent=None, *, фоновые: bool = True) -> None:
        super().__init__(parent)
        self.source = source
        self._фоновые = фоновые
        self._записи: list = []
        self._показано = None  # тот список, по которому построена таблица
        self._картинки: dict[str, QTableWidgetItem] = {}
        self._миниатюры = None
        self._заполняем = False

        корень = QVBoxLayout(self)
        корень.setContentsMargins(18, 16, 18, 16)
        корень.setSpacing(10)

        ряд = QHBoxLayout()
        self.поиск = QLineEdit()
        self.поиск.setPlaceholderText(_("Поиск по названию — по всем каналам"))
        self.поиск.setClearButtonEnabled(True)
        self.канал = QComboBox()
        self.только_пропавшие = QCheckBox(_("Только те, которых нет на YouTube"))
        self.только_пропавшие.setToolTip(
            _("Ролики из архива, которых больше нет в списке канала: удалены, скрыты "
              "или лежат на другой вкладке канала (Shorts, трансляции).")
        )
        ряд.addWidget(self.поиск, 1)
        ряд.addWidget(self.канал)
        ряд.addWidget(self.только_пропавшие)
        корень.addLayout(ряд)

        середина = QHBoxLayout()
        середина.setSpacing(12)
        # Отдельного столбца «есть ли на YouTube» нет намеренно: он пуст почти
        # у всех строк и отнимал место у названия. Пропавший ролик отмечен
        # цветом названия и подписью справа.
        self.таблица = QTableWidget(0, 5)
        self.таблица.setHorizontalHeaderLabels(
            ["", _("Название"), _("Канал"), _("Дата"), _("Размер")]
        )
        self.таблица.setColumnWidth(СТОЛБЕЦ_КАРТИНКА, 104)
        self.таблица.setColumnWidth(СТОЛБЕЦ_КАНАЛ, 130)
        self.таблица.setColumnWidth(СТОЛБЕЦ_ДАТА, 92)
        self.таблица.setColumnWidth(СТОЛБЕЦ_РАЗМЕР, 80)
        self.таблица.horizontalHeader().setSectionResizeMode(
            СТОЛБЕЦ_НАЗВАНИЕ, QHeaderView.ResizeMode.Stretch
        )
        self.таблица.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.таблица.verticalHeader().setVisible(False)
        self.таблица.setShowGrid(False)
        self.таблица.setIconSize(МИНИАТЮРА)
        self.таблица.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.таблица.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.таблица.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        середина.addWidget(self.таблица, 1)
        середина.addWidget(self._предпросмотр())
        корень.addLayout(середина, 1)

        self.счётчик = приглушить(QLabel(""))
        корень.addWidget(self.счётчик)

        self.поиск.textChanged.connect(self._отобрать)
        self.канал.currentIndexChanged.connect(self._отобрать)
        self.только_пропавшие.toggled.connect(self._отобрать)
        self.таблица.itemSelectionChanged.connect(self._показать)
        self.таблица.itemDoubleClicked.connect(lambda _ячейка: self._смотреть())

        # Описание читает ffprobe отдельным процессом: файл может лежать на
        # уснувшем диске, и ждать его в главном потоке значило бы заморозить окно.
        self._ffprobe = QProcess(self)
        self._ffprobe.finished.connect(self._описание_прочитано)
        self._ждём_описание = ""

    # --- предпросмотр -------------------------------------------------------

    def _предпросмотр(self) -> QWidget:
        панель = QWidget()
        панель.setFixedWidth(ПРЕДПРОСМОТР.width())
        столбец = QVBoxLayout(панель)
        столбец.setContentsMargins(0, 0, 0, 0)

        self.картинка = QLabel(_("выберите ролик"))
        self.картинка.setFixedSize(ПРЕДПРОСМОТР)
        self.картинка.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.картинка.setStyleSheet("background: #1b1b1b; color: #888;")
        столбец.addWidget(self.картинка)

        self.название = QLabel("")
        self.название.setWordWrap(True)
        self.название.setStyleSheet("font-weight: bold;")
        столбец.addWidget(self.название)

        self.подпись = приглушить(QLabel(""))
        self.подпись.setWordWrap(True)
        столбец.addWidget(self.подпись)

        self.кнопка_смотреть = QPushButton(_("Смотреть"))
        self.кнопка_смотреть.setObjectName("primary")
        ряд = QHBoxLayout()
        self.кнопка_папка = QPushButton(_("Показать в папке"))
        self.кнопка_youtube = QPushButton(_("Открыть на YouTube"))
        ряд.addWidget(self.кнопка_папка)
        ряд.addWidget(self.кнопка_youtube)
        столбец.addWidget(self.кнопка_смотреть)
        столбец.addLayout(ряд)
        for кнопка in (self.кнопка_смотреть, self.кнопка_папка, self.кнопка_youtube):
            кнопка.setEnabled(False)

        self.описание = QPlainTextEdit()
        self.описание.setReadOnly(True)
        self.описание.setPlaceholderText(_("описание ролика"))
        столбец.addWidget(self.описание, 1)

        self.кнопка_смотреть.clicked.connect(self._смотреть)
        self.кнопка_папка.clicked.connect(self._показать_в_папке)
        self.кнопка_youtube.clicked.connect(self._открыть_на_youtube)
        return панель

    # --- заполнение ---------------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802 — имя задано Qt
        """Читаем диск, только когда вкладку открыли: до того это лишняя работа."""
        super().showEvent(event)
        self.перечитать()

    def перечитать(self, fresh: bool = False) -> None:
        записи = self.source.library(fresh=fresh)
        if записи is self._показано:
            return  # архив не менялся — таблица уже верна
        self._показано = записи
        self._записи = list(записи)
        self._заполнить()

    def _заполнить(self) -> None:
        from runner.images import cached_image

        выбранный = self.канал.currentData()
        self.канал.blockSignals(True)
        self.канал.clear()
        self.канал.addItem(_("Все каналы"), "")
        for имя in sorted({з.channel for з in self._записи}):
            self.канал.addItem(имя, имя)
        место = self.канал.findData(выбранный)
        self.канал.setCurrentIndex(место if место >= 0 else 0)
        self.канал.blockSignals(False)

        # Порядок выключаем на время заполнения: иначе таблица переставляла бы
        # строки после каждой вставленной ячейки, и ячейки одной записи
        # разъезжались бы по разным строкам.
        self._заполняем = True
        self.таблица.setSortingEnabled(False)
        self.таблица.setRowCount(len(self._записи))
        self._картинки = {}
        for строка, запись in enumerate(self._записи):
            значок = QTableWidgetItem("")
            путь = cached_image(self.source.thumbs_dir, запись.video_id)
            if путь is not None:
                значок.setIcon(QIcon(str(путь)))
            self._картинки[запись.video_id] = значок
            self.таблица.setItem(строка, СТОЛБЕЦ_КАРТИНКА, значок)

            название = QTableWidgetItem(запись.title)
            # Номер записи едет вместе с ячейкой: после смены порядка номер
            # строки уже ничего не говорит о том, что в ней лежит.
            название.setData(Qt.ItemDataRole.UserRole, строка)
            self.таблица.setItem(строка, СТОЛБЕЦ_НАЗВАНИЕ, название)
            self.таблица.setItem(строка, СТОЛБЕЦ_КАНАЛ, QTableWidgetItem(запись.channel))
            self.таблица.setItem(строка, СТОЛБЕЦ_ДАТА, QTableWidgetItem(запись.date_text))
            self.таблица.setItem(
                строка, СТОЛБЕЦ_РАЗМЕР, _Число(объём(запись.size_bytes), запись.size_bytes)
            )
            if запись.gone:
                название.setForeground(QColor(ЖЁЛТЫЙ))
                название.setToolTip(
                    _("нет в списке канала") + ". " + self.только_пропавшие.toolTip()
                )
            self.таблица.setRowHeight(строка, 60)
        self.таблица.setSortingEnabled(True)
        self.таблица.sortByColumn(СТОЛБЕЦ_ДАТА, Qt.SortOrder.DescendingOrder)
        self._заполняем = False
        self._отобрать()

        if self._фоновые and self._записи:
            self._тянуть_миниатюры()

    def _запись_в_строке(self, строка: int):
        ячейка = self.таблица.item(строка, СТОЛБЕЦ_НАЗВАНИЕ)
        if ячейка is None:
            return None
        номер = ячейка.data(Qt.ItemDataRole.UserRole)
        return self._записи[номер] if isinstance(номер, int) and 0 <= номер < len(self._записи) else None

    def _отобрать(self) -> None:
        """Спрятать строки, не подходящие под отбор. Прячем, а не строим
        заново: две тысячи строк с картинками на каждую набранную букву —
        это заметная задержка."""
        if self._заполняем:
            return
        видно = пропавших = 0
        байт = 0
        for строка in range(self.таблица.rowCount()):
            запись = self._запись_в_строке(строка)
            годится = запись is not None and matches(
                запись,
                query=self.поиск.text(),
                channel=self.канал.currentData() or "",
                only_gone=self.только_пропавшие.isChecked(),
            )
            self.таблица.setRowHidden(строка, not годится)
            if годится:
                видно += 1
                байт += запись.size_bytes
                пропавших += 1 if запись.gone else 0
        части = [_('показано {} из {}').format(видно, len(self._записи)), объём(байт)]
        if пропавших:
            части.append(_('из них нет на YouTube: {}').format(пропавших))
        self.счётчик.setText(" · ".join(части))

    # --- миниатюры ----------------------------------------------------------

    def _тянуть_миниатюры(self) -> None:
        from gui.videos import ЗагрузкаМиниатюр, _отпустить

        _отпустить(self._миниатюры)
        self._миниатюры = ЗагрузкаМиниатюр(self.source, self._записи)
        self._миниатюры.картинка.connect(self._миниатюра_готова)
        self._миниатюры.start()

    def _миниатюра_готова(self, номер: int) -> None:
        from runner.images import cached_image

        if not 0 <= номер < len(self._записи):
            return
        запись = self._записи[номер]
        ячейка = self._картинки.get(запись.video_id)
        путь = cached_image(self.source.thumbs_dir, запись.video_id)
        if ячейка is not None and путь is not None and ячейка.icon().isNull():
            ячейка.setIcon(QIcon(str(путь)))

    def дождаться_потоков(self) -> None:
        """Живой поток в момент разрушения окна валит Qt целиком."""
        from gui.videos import _отпустить

        _отпустить(self._миниатюры)
        self._миниатюры = None
        if self._ffprobe.state() != QProcess.ProcessState.NotRunning:
            self._ffprobe.kill()
            self._ffprobe.waitForFinished(2000)

    # --- выбранный ролик ----------------------------------------------------

    def _текущая(self):
        строки = self.таблица.selectionModel().selectedRows()
        return self._запись_в_строке(строки[0].row()) if строки else None

    def _путь(self, запись) -> Path:
        return Path(self.source.base) / запись.path

    def _показать(self) -> None:
        from runner.images import cached_image

        запись = self._текущая()
        for кнопка in (self.кнопка_смотреть, self.кнопка_папка, self.кнопка_youtube):
            кнопка.setEnabled(запись is not None)
        if запись is None:
            return

        self.название.setText(запись.title)
        части = [запись.channel, запись.date_text, объём(запись.size_bytes)]
        if запись.gone:
            части.append(_("нет в списке канала"))
        self.подпись.setText(" · ".join(часть for часть in части if часть != "—"))

        путь = cached_image(self.source.thumbs_dir, запись.video_id)
        картинка = QPixmap(str(путь)) if путь is not None else QPixmap()
        if картинка.isNull():
            self.картинка.setPixmap(QPixmap())
            self.картинка.setText(_("миниатюра ещё не скачана"))
        else:
            self.картинка.setPixmap(
                картинка.scaled(
                    ПРЕДПРОСМОТР,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        self._читать_описание(запись)

    def _читать_описание(self, запись) -> None:
        self.описание.setPlainText("")
        if self._ffprobe.state() != QProcess.ProcessState.NotRunning:
            # Человек листает список быстрее, чем отвечает диск: прежний
            # вопрос уже не нужен.
            self._ffprobe.kill()
            self._ffprobe.waitForFinished(1000)
        self._ждём_описание = запись.video_id
        self._ffprobe.start(
            "ffprobe",
            ["-v", "error", "-show_entries", "format_tags", "-of", "json", str(self._путь(запись))],
        )

    def _описание_прочитано(self, _код: int, _статус) -> None:
        запись = self._текущая()
        if запись is None or запись.video_id != self._ждём_описание:
            return  # ответ на вопрос о ролике, с которого уже ушли
        try:
            данные = json.loads(bytes(self._ffprobe.readAllStandardOutput()).decode("utf-8", "replace"))
            метки = данные.get("format", {}).get("tags", {})
        except (json.JSONDecodeError, AttributeError):
            метки = {}
        self.описание.setPlainText(description_from_tags(метки) if isinstance(метки, dict) else "")

    def _смотреть(self) -> None:
        запись = self._текущая()
        if запись is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._путь(запись))))

    def _показать_в_папке(self) -> None:
        запись = self._текущая()
        if запись is None:
            return
        путь = self._путь(запись)
        if sys.platform == "win32":
            # Проводник умеет открыть папку с уже выделенным файлом.
            subprocess.Popen(["explorer", "/select,", str(путь)])
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(путь.parent)))

    def _открыть_на_youtube(self) -> None:
        запись = self._текущая()
        if запись is not None:
            QDesktopServices.openUrl(QUrl(запись.url))
