"""Первый запуск: спросить язык и куда складывать архив.

Без этого разговора программа, скачанная из репозитория, встречает человека
отказом «нет файла настроек» и советом запустить что-то в командной строке.
Для того, кто пришёл за окном, это тупик.

Спрашиваем ровно две вещи и обе — те, которые нельзя угадать. Язык системы
угадывается, но неверно чаще, чем кажется: на машине, где это писалось,
интерфейс Windows английский, а человек русский. Папку не угадать вовсе:
архив вырастает до терабайта, и куда его класть, знает только хозяин диска.

Всё остальное — качество, паузы, расписание — имеет разумные умолчания
и правится потом, в настройках.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.config import DEFAULT_CONFIG_TEXT, dump_config, loads, parse_config
from core.i18n import ИСХОДНЫЙ, НАЗВАНИЯ, СИСТЕМНЫЙ, нормализовать
from core.locales import КАТАЛОГИ
from gui.source import осмотреть_папку
from runner.language import _, настроить, системный_язык

#: Где внутри рабочей папки лежит учёт. Совпадает с умолчанием настроек:
#: мастер должен узнать готовый архив, если человек указал на него.
УЧЁТ = "_tools/downloaded.txt"


class ОкноПервогоЗапуска(QDialog):
    """Язык и рабочая папка. Возвращает согласие только когда папка годная."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.папка: Path | None = None
        self.язык = СИСТЕМНЫЙ
        self.resize(660, 380)
        self._корень = QVBoxLayout(self)
        self._построить()

    # --- сборка -------------------------------------------------------------

    def _построить(self) -> None:
        """Собрать содержимое. Зовётся заново при смене языка — по той же
        причине, что и в главном окне: переписывание подписей по одной
        обязательно что-нибудь пропустит."""
        прежнее = getattr(self, "_нутро", None)

        self.setWindowTitle(_("Архив YouTube — первый запуск"))
        нутро = QWidget()
        столбец = QVBoxLayout(нутро)

        привет = QLabel(_("Программа будет забирать новые ролики с выбранных каналов сама."))
        привет.setStyleSheet("font-size: 15px; font-weight: bold;")
        привет.setWordWrap(True)
        столбец.addWidget(привет)

        ряд_языка = QHBoxLayout()
        ряд_языка.addWidget(QLabel(_("Язык:")))
        self.поле_язык = QComboBox()
        self.поле_язык.addItem(
            _("Системный язык — {}").format(
                НАЗВАНИЯ.get(нормализовать(системный_язык()), "?")
            ),
            СИСТЕМНЫЙ,
        )
        for код in [ИСХОДНЫЙ, *sorted(КАТАЛОГИ)]:
            self.поле_язык.addItem(НАЗВАНИЯ.get(код, код), код)
        место = self.поле_язык.findData(self.язык)
        self.поле_язык.setCurrentIndex(место if место >= 0 else 0)
        self.поле_язык.currentIndexChanged.connect(self._язык_выбран)
        ряд_языка.addWidget(self.поле_язык, 1)
        столбец.addLayout(ряд_языка)

        пояснение = QLabel(_(
            "Ролики скачиваются целиком, и места им нужно много: час видео — "
            "от 0,6 до 1,6 ГБ, а канал целиком легко занимает сотни гигабайт. "
            "Выберите папку на диске, где есть запас."
        ))
        пояснение.setWordWrap(True)
        пояснение.setStyleSheet("color: #8b949e;")
        столбец.addWidget(пояснение)

        ряд_папки = QHBoxLayout()
        self.поле_папка = QLineEdit()
        self.поле_папка.setReadOnly(True)
        self.поле_папка.setPlaceholderText(_("Папка не выбрана"))
        if self.папка is not None:
            self.поле_папка.setText(str(self.папка))
        обзор = QPushButton(_("Обзор…"))
        обзор.clicked.connect(self._выбрать_папку)
        ряд_папки.addWidget(self.поле_папка, 1)
        ряд_папки.addWidget(обзор)
        столбец.addLayout(ряд_папки)

        self.приговор = QLabel("")
        self.приговор.setWordWrap(True)
        столбец.addWidget(self.приговор)
        столбец.addStretch(1)

        кнопки = QHBoxLayout()
        кнопки.addStretch(1)
        self.кнопка_готово = QPushButton(_("Готово"))
        self.кнопка_готово.setEnabled(self.папка is not None)
        self.кнопка_готово.clicked.connect(self.accept)
        отмена = QPushButton(_("Отмена"))
        отмена.clicked.connect(self.reject)
        кнопки.addWidget(отмена)
        кнопки.addWidget(self.кнопка_готово)
        столбец.addLayout(кнопки)

        self._корень.addWidget(нутро)
        self._нутро = нутро
        if прежнее is not None:
            # Как и в главном окне: само оно не удалится, а останется
            # ребёнком и будет копиться на каждой смене языка.
            self._корень.removeWidget(прежнее)
            прежнее.setParent(None)
            прежнее.deleteLater()

    # --- выбор --------------------------------------------------------------

    def _язык_выбран(self) -> None:
        self.язык = self.поле_язык.currentData()
        настроить(self.язык)
        self._построить()

    def _выбрать_папку(self) -> None:
        выбор = QFileDialog.getExistingDirectory(
            self, _("Куда складывать архив"), str(self.папка or Path.home())
        )
        if not выбор:
            return

        осмотр = осмотреть_папку(Path(выбор), учёт=УЧЁТ)
        if not осмотр.ok:
            self.приговор.setText(осмотр.reason)
            self.приговор.setStyleSheet("color: #c62828;")
            self.кнопка_готово.setEnabled(False)
            return

        self.папка = Path(выбор)
        self.поле_папка.setText(str(self.папка))
        self.приговор.setText(осмотр.warning)
        self.приговор.setStyleSheet("color: #8b949e;")
        self.кнопка_готово.setEnabled(True)


def настройки_для(папка: Path, язык: str) -> str:
    """Текст настроек для выбранного. Всё прочее берётся из умолчаний —
    их не спрашивают, потому что разумный ответ известен."""
    основа = parse_config(loads(DEFAULT_CONFIG_TEXT))
    готово = replace(
        основа,
        paths=replace(основа.paths, base=Path(папка).as_posix()),
        language=язык,
    )
    return dump_config(готово)


def спросить(parent=None) -> tuple[Path, str] | None:
    """Провести разговор. `None` — человек отказался, и это его право."""
    окно = ОкноПервогоЗапуска(parent)
    if окно.exec() and окно.папка is not None:
        return окно.папка, окно.язык
    return None
