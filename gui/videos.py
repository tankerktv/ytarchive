"""Окно выбора роликов канала.

По умолчанию отмечено всё: архив собирается сам, и требовать отметить
две тысячи роликов ради того же самого было бы издевательством. Человек
снимает лишнее.

**Снятая галочка ничего не удаляет.** Уже скачанный ролик останется на диске;
галочка решает только судьбу будущих загрузок. Поэтому состояние каждого
ролика показано прямо в списке — иначе снятие выглядело бы как удаление.

Решения принимает `core.exclusions`: здесь только Qt — показать и записать.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.archive import parse_archive
from core.exclusions import merge
from core.videos import Listing, search

#: Размер миниатюры в списке. mqdefault — 320×180, показываем меньше:
#: строка со стокилобайтной картинкой в полный рост нечитаема.
МИНИАТЮРА = QSize(96, 54)
ПРЕДПРОСМОТР = QSize(320, 180)

СТОЛБЦЫ = ["", "", "Название", "Длительность", "Состояние"]


class ПереписьРоликов(QThread):
    """Перепись канала в отдельном потоке.

    На большом канале yt-dlp обходит шестьсот роликов не мгновенно, и в
    главном потоке окно на это время просто замёрзло бы.
    """

    готово = Signal(object)

    def __init__(self, source, канал: str) -> None:
        super().__init__()
        self.source = source
        self.канал = канал

    def run(self) -> None:
        try:
            итог = self.source.listing(self.канал)
        except Exception:  # noqa: BLE001 — окно переживёт любую беду переписи
            итог = Listing()
        self.готово.emit(итог)


class ЗагрузкаМиниатюр(QThread):
    """Миниатюры — по одной, в порядке списка, с кэшем на диске.

    Порядок не случаен: человек смотрит сверху, и картинки должны появляться
    там же. Кэш обязателен — иначе каждое открытие окна это шестьсот запросов.
    """

    картинка = Signal(int)

    def __init__(self, source, видео: list) -> None:
        super().__init__()
        self.source = source
        self.видео = list(видео)
        self._бросить = False

    def бросить(self) -> None:
        self._бросить = True

    def run(self) -> None:
        from runner.images import cached_image, ensure_image

        for номер, ролик in enumerate(self.видео):
            if self._бросить:
                return
            if cached_image(self.source.thumbs_dir, ролик.video_id) is None:
                ensure_image(self.source.thumbs_dir, ролик.video_id, ролик.thumbnail_url)
            if self._бросить:
                return
            self.картинка.emit(номер)


class ОкноРоликов(QDialog):
    """Список роликов канала с галочками, поиском и предпросмотром."""

    def __init__(self, source, канал: str, parent=None, *, фоновые: bool = True) -> None:
        super().__init__(parent)
        self.source = source
        self.канал = канал
        #: Самопроверка строит окно без сети: перепись подставляется руками,
        #: и тянуть миниатюры на выдуманные идентификаторы незачем.
        self._фоновые = фоновые
        self.setWindowTitle(f"Ролики канала «{канал}»")
        self.resize(1180, 720)

        self._видео: list = []
        self._снятые: set[str] = set()
        self._скачанные: frozenset[str] = frozenset()
        self._видимые: list = []
        self._перепись = None
        self._миниатюры = None
        self._рисуем = False

        корень = QVBoxLayout(self)

        self.заголовок = QLabel(f"Читаю список роликов канала «{канал}»…")
        self.заголовок.setStyleSheet("font-size: 15px; font-weight: bold;")
        корень.addWidget(self.заголовок)

        корень.addWidget(QLabel(
            "Отмечено — будет скачано. Снятая галочка не удаляет уже скачанное: "
            "она про будущие проходы."
        ))

        ряд_поиска = QHBoxLayout()
        self.поиск = QLineEdit()
        self.поиск.setPlaceholderText("Поиск по названию")
        self.поиск.setClearButtonEnabled(True)
        ряд_поиска.addWidget(self.поиск, 1)
        self.кнопка_все = QPushButton("Отметить показанные")
        self.кнопка_никого = QPushButton("Снять показанные")
        ряд_поиска.addWidget(self.кнопка_все)
        ряд_поиска.addWidget(self.кнопка_никого)
        корень.addLayout(ряд_поиска)

        ряд = QHBoxLayout()
        self.таблица = QTableWidget(0, len(СТОЛБЦЫ))
        self.таблица.setHorizontalHeaderLabels(СТОЛБЦЫ)
        self.таблица.setColumnWidth(0, 34)
        self.таблица.setColumnWidth(1, 110)
        self.таблица.setColumnWidth(2, 460)
        self.таблица.setColumnWidth(3, 110)
        self.таблица.horizontalHeader().setStretchLastSection(True)
        self.таблица.verticalHeader().setVisible(False)
        self.таблица.setIconSize(МИНИАТЮРА)
        self.таблица.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.таблица.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.таблица.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        ряд.addWidget(self.таблица, 1)
        ряд.addWidget(self._предпросмотр())
        корень.addLayout(ряд, 1)

        нижний = QHBoxLayout()
        self.счётчик = QLabel("")
        self.счётчик.setStyleSheet("color: #666;")
        нижний.addWidget(self.счётчик, 1)
        self.кнопка_сохранить = QPushButton("Сохранить выбор")
        self.кнопка_закрыть = QPushButton("Закрыть")
        self.кнопка_сохранить.setEnabled(False)
        нижний.addWidget(self.кнопка_сохранить)
        нижний.addWidget(self.кнопка_закрыть)
        корень.addLayout(нижний)

        self.поиск.textChanged.connect(self._перерисовать)
        self.таблица.itemChanged.connect(self._галочка)
        self.таблица.itemSelectionChanged.connect(self._показать_предпросмотр)
        self.кнопка_все.clicked.connect(lambda: self._всем_галочку(True))
        self.кнопка_никого.clicked.connect(lambda: self._всем_галочку(False))
        self.кнопка_сохранить.clicked.connect(self._сохранить)
        self.кнопка_закрыть.clicked.connect(self.reject)

        # Архив и снятые галочки — местные файлы, читаются мгновенно и нужны
        # раньше переписи: без них список нечем раскрасить. В сеть ходит
        # только перепись, и только она уходит в поток.
        self._скачанные = parse_archive(self.source.archive_text()).video_ids
        self._снятые = set(self.source.exclusions().video_ids)

        if фоновые:
            self._читать()

    # --- предпросмотр -------------------------------------------------------

    def _предпросмотр(self) -> QWidget:
        панель = QWidget()
        панель.setFixedWidth(340)
        столбец = QVBoxLayout(панель)

        self.картинка = QLabel("")
        self.картинка.setFixedSize(ПРЕДПРОСМОТР)
        self.картинка.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.картинка.setStyleSheet("background: #1b1b1b; color: #888;")
        self.картинка.setText("выберите ролик")
        столбец.addWidget(self.картинка)

        self.название = QLabel("")
        self.название.setWordWrap(True)
        self.название.setStyleSheet("font-weight: bold;")
        столбец.addWidget(self.название)

        self.подпись = QLabel("")
        self.подпись.setStyleSheet("color: #666;")
        self.подпись.setWordWrap(True)
        столбец.addWidget(self.подпись)

        self.кнопка_открыть = QPushButton("Открыть на YouTube")
        self.кнопка_открыть.setEnabled(False)
        self.кнопка_открыть.clicked.connect(self._открыть_в_браузере)
        столбец.addWidget(self.кнопка_открыть)

        столбец.addStretch(1)
        return панель

    def _текущий(self):
        строки = self.таблица.selectionModel().selectedRows()
        if not строки:
            return None
        номер = строки[0].row()
        return self._видимые[номер] if 0 <= номер < len(self._видимые) else None

    def _показать_предпросмотр(self) -> None:
        from runner.images import cached_image

        ролик = self._текущий()
        if ролик is None:
            self.кнопка_открыть.setEnabled(False)
            return

        self.название.setText(ролик.title)
        состояние = self._состояние(ролик)
        self.подпись.setText(f"{ролик.duration_text()} · {состояние} · {ролик.video_id}")
        self.кнопка_открыть.setEnabled(True)

        путь = cached_image(self.source.thumbs_dir, ролик.video_id)
        if путь is None:
            self.картинка.setText("миниатюра ещё не скачана")
            return
        картинка = QPixmap(str(путь))
        if картинка.isNull():
            self.картинка.setText("миниатюра не читается")
            return
        self.картинка.setPixmap(
            картинка.scaled(
                ПРЕДПРОСМОТР,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _открыть_в_браузере(self) -> None:
        ролик = self._текущий()
        if ролик is not None:
            QDesktopServices.openUrl(QUrl(ролик.url))

    # --- чтение -------------------------------------------------------------

    def _читать(self) -> None:
        self._перепись = ПереписьРоликов(self.source, self.канал)
        self._перепись.готово.connect(self._перепись_готова)
        self._перепись.start()

    def _перепись_готова(self, перепись) -> None:
        self._видео = list(перепись.videos)
        # Из общего файла нас касаются только ролики этого канала: остальные
        # трогать нельзя, и держать их в памяти окна незачем.
        известные = {в.video_id for в in self._видео}
        self._снятые &= известные

        if not self._видео:
            self.заголовок.setText(
                f"«{self.канал}»: список получить не удалось — "
                f"сеть или вход в аккаунт. Выбор не тронут."
            )
            return

        self.заголовок.setText(f"«{self.канал}»: роликов {len(self._видео)}")
        self.кнопка_сохранить.setEnabled(True)
        self._перерисовать()

        if self._фоновые:
            self._миниатюры = ЗагрузкаМиниатюр(self.source, self._видео)
            self._миниатюры.картинка.connect(self._миниатюра_готова)
            self._миниатюры.start()

    def _миниатюра_готова(self, номер: int) -> None:
        if 0 <= номер < len(self._видео):
            self._нарисовать_миниатюру(self._видео[номер])

    def _нарисовать_миниатюру(self, ролик) -> None:
        from runner.images import cached_image

        for строка, видимый in enumerate(self._видимые):
            if видимый.video_id != ролик.video_id:
                continue
            путь = cached_image(self.source.thumbs_dir, ролик.video_id)
            ячейка = self.таблица.item(строка, 1)
            if путь is not None and ячейка is not None:
                ячейка.setIcon(QIcon(str(путь)))
            break

    # --- список -------------------------------------------------------------

    def _состояние(self, ролик) -> str:
        if ролик.video_id in self._скачанные:
            return "скачан"
        if ролик.video_id in self._снятые:
            return "снят"
        return "в очереди"

    def _перерисовать(self) -> None:
        from runner.images import cached_image

        self._видимые = search(self._видео, self.поиск.text())

        # Пока перерисовываем, itemChanged срабатывает на каждую ячейку.
        # Без этого заслона выставление галочек само себя же и перепишет.
        self._рисуем = True
        try:
            self.таблица.setRowCount(len(self._видимые))
            for строка, ролик in enumerate(self._видимые):
                отметка = QTableWidgetItem("")
                отметка.setFlags(
                    Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsUserCheckable
                )
                отметка.setCheckState(
                    Qt.CheckState.Unchecked
                    if ролик.video_id in self._снятые
                    else Qt.CheckState.Checked
                )
                отметка.setData(Qt.ItemDataRole.UserRole, ролик.video_id)
                self.таблица.setItem(строка, 0, отметка)

                значок = QTableWidgetItem("")
                путь = cached_image(self.source.thumbs_dir, ролик.video_id)
                if путь is not None:
                    значок.setIcon(QIcon(str(путь)))
                self.таблица.setItem(строка, 1, значок)

                self.таблица.setItem(строка, 2, QTableWidgetItem(ролик.title))
                self.таблица.setItem(строка, 3, QTableWidgetItem(ролик.duration_text()))
                self.таблица.setItem(строка, 4, QTableWidgetItem(self._состояние(ролик)))
                self.таблица.setRowHeight(строка, 60)
        finally:
            self._рисуем = False

        self._обновить_счётчик()

    def _обновить_счётчик(self) -> None:
        всего = len(self._видео)
        снято = len(self._снятые)
        показано = len(self._видимые)
        хвост = f", показано {показано}" if показано != всего else ""
        self.счётчик.setText(
            f"отмечено {всего - снято} из {всего}{хвост}"
            + (f"; снято {снято}" if снято else "")
        )

    def _галочка(self, item) -> None:
        if self._рисуем or item.column() != 0:
            return
        идентификатор = item.data(Qt.ItemDataRole.UserRole)
        if not идентификатор:
            return
        if item.checkState() == Qt.CheckState.Checked:
            self._снятые.discard(идентификатор)
        else:
            self._снятые.add(идентификатор)

        строка = item.row()
        состояние = self.таблица.item(строка, 4)
        if состояние is not None and 0 <= строка < len(self._видимые):
            состояние.setText(self._состояние(self._видимые[строка]))
        self._обновить_счётчик()

    def _всем_галочку(self, отметить: bool) -> None:
        """Только по показанным: иначе поиск превращается в ловушку —
        человек ищет «стрим», жмёт «снять», и лишается всего канала.
        """
        for ролик in self._видимые:
            if отметить:
                self._снятые.discard(ролик.video_id)
            else:
                self._снятые.add(ролик.video_id)
        self._перерисовать()

    # --- запись -------------------------------------------------------------

    def _сохранить(self) -> None:
        известные = {в.video_id for в in self._видео}
        try:
            итог = merge(self.source.exclusions(), известные, self._снятые & известные)
        except ValueError as ошибка:
            QMessageBox.warning(self, "Выбор не сохранён", str(ошибка))
            return

        ответ = self.source.write_exclusions(итог.video_ids)
        if ответ.startswith("не сохранилось"):
            QMessageBox.warning(self, "Выбор не сохранён", ответ)
            return
        self.accept()

    # --- закрытие -----------------------------------------------------------

    def _дождаться_потоков(self) -> None:
        """Живой QThread в момент разрушения окна валит Qt целиком —
        без сообщения и без кода возврата. Проверено на себе.
        """
        for поток in (self._миниатюры, self._перепись):
            if поток is None:
                continue
            бросить = getattr(поток, "бросить", None)
            if бросить is not None:
                бросить()
            if поток.isRunning():
                поток.wait(3000)

    def closeEvent(self, event) -> None:  # noqa: N802 — имя задано Qt
        self._дождаться_потоков()
        super().closeEvent(event)

    def done(self, result: int) -> None:
        self._дождаться_потоков()
        super().done(result)
