"""Окна ухода за архивом: вывод команды и правила канала.

Сверка учёта, уборка и обновление yt-dlp уже есть командами. Окно их не
повторяет, а запускает и показывает ответ как есть: так у окна и командной
строки не может оказаться двух разных мнений о том, что убирать.

Команда идёт отдельным процессом через QProcess — он не блокирует окно и
не требует своего потока. Потоки здесь обходим намеренно: живой поток в
момент закрытия окна обрывает программу целиком, и это уже случалось.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from core.rules import Rules, RulesError, format_rules, parse_rules
from runner.language import _


def команда_программы(config_path: Path, *доводы: str) -> list[str]:
    """Чем позвать саму программу. Без консоли там, где это различают:
    иначе рядом с окном на миг открывается чёрное окно."""
    питон = Path(sys.executable)
    без_окна = питон.with_name("pythonw.exe")
    if sys.platform == "win32" and без_окна.exists():
        питон = без_окна
    корень = Path(__file__).resolve().parents[1]
    return [str(питон), str(корень / "ytarchive.py"), "--config", str(config_path), *доводы]


class ОкноКоманды(QDialog):
    """Запустить команду программы и показать, что она ответила.

    `применить` — доводы второго шага. Если они заданы, первый запуск только
    показывает, а менять что-либо начинает кнопка: тот же порядок «сначала
    вхолостую», что и в командной строке.
    """

    def __init__(
        self,
        config_path: Path,
        заголовок: str,
        доводы: tuple[str, ...],
        *,
        применить: tuple[str, ...] = (),
        подпись_применить: str = "",
        parent=None,
        запустить: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(заголовок)
        self.resize(760, 460)
        self._config_path = config_path
        self._применить = применить

        столбец = QVBoxLayout(self)
        self.состояние = QLabel("")
        self.состояние.setStyleSheet("color: #666;")
        столбец.addWidget(self.состояние)

        self.вывод = QPlainTextEdit()
        self.вывод.setReadOnly(True)
        self.вывод.setFont(QFont("Consolas", 10))
        столбец.addWidget(self.вывод, 1)

        ряд = QHBoxLayout()
        self.кнопка_применить = QPushButton(подпись_применить or _("Выполнить"))
        self.кнопка_применить.setVisible(bool(применить))
        self.кнопка_применить.setEnabled(False)
        закрыть = QPushButton(_("Закрыть"))
        ряд.addWidget(self.кнопка_применить)
        ряд.addStretch(1)
        ряд.addWidget(закрыть)
        столбец.addLayout(ряд)

        self.кнопка_применить.clicked.connect(self._выполнить_второй_шаг)
        закрыть.clicked.connect(self.accept)

        self.процесс = QProcess(self)
        # Потоки слиты: порядок строк важнее того, откуда они пришли.
        self.процесс.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        окружение = QProcessEnvironment.systemEnvironment()
        # Иначе кириллица из потомка приходит в кодировке консоли.
        окружение.insert("PYTHONIOENCODING", "utf-8")
        окружение.insert("PYTHONUTF8", "1")
        self.процесс.setProcessEnvironment(окружение)
        self.процесс.readyRead.connect(self._дочитать)
        self.процесс.finished.connect(self._кончилось)
        self.процесс.errorOccurred.connect(self._не_запустилось)
        self._второй_шаг_сделан = False

        if запустить:
            self._пуск(доводы)

    def _пуск(self, доводы: tuple[str, ...]) -> None:
        команда = команда_программы(self._config_path, *доводы)
        self.состояние.setText(_("работаю…"))
        self.кнопка_применить.setEnabled(False)
        self.процесс.start(команда[0], команда[1:])

    def _дочитать(self) -> None:
        кусок = bytes(self.процесс.readAll()).decode("utf-8", errors="replace")
        if кусок:
            self.вывод.moveCursor(self.вывод.textCursor().MoveOperation.End)
            self.вывод.insertPlainText(кусок.replace("\r\n", "\n"))
            полоса = self.вывод.verticalScrollBar()
            полоса.setValue(полоса.maximum())

    def _кончилось(self, код: int, _статус) -> None:
        self._дочитать()
        self.состояние.setText(_("готово") if код == 0 else _("закончено с замечаниями"))
        # Второй шаг предлагаем один раз: повторять удаление незачем.
        self.кнопка_применить.setEnabled(bool(self._применить) and not self._второй_шаг_сделан)

    def _не_запустилось(self, _ошибка) -> None:
        self.состояние.setText(_("не вышло запустить: {}").format(self.процесс.errorString()))

    def _выполнить_второй_шаг(self) -> None:
        self._второй_шаг_сделан = True
        self.вывод.appendPlainText("")
        self._пуск(self._применить)

    def done(self, итог: int) -> None:  # noqa: D401 — имя задано Qt
        """Закрытие окна не должно оставлять команду работать без хозяина."""
        if self.процесс.state() != QProcess.ProcessState.NotRunning:
            self.процесс.kill()
            self.процесс.waitForFinished(3000)
        super().done(итог)


class ОкноПравил(QDialog):
    """Правила отбора одного канала."""

    def __init__(self, имя: str, правила: Rules, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Правила канала — {}").format(имя))
        self.правила = правила

        столбец = QVBoxLayout(self)
        пояснение = QLabel(
            _("Правило вычёркивает ролики из очереди, но ничего не удаляет с диска: "
              "снимете правило — ролики вернутся в очередь. Ролик, у которого "
              "длительность или дата неизвестны, правилу не подчиняется.")
        )
        пояснение.setWordWrap(True)
        пояснение.setStyleSheet("color: #666;")
        столбец.addWidget(пояснение)

        форма = QFormLayout()
        self.поле_мин = QSpinBox()
        self.поле_мин.setRange(0, 24 * 3600)
        self.поле_мин.setSuffix(_(" с"))
        self.поле_мин.setSpecialValueText(_("не ограничено"))
        self.поле_мин.setValue(правила.min_seconds)
        self.поле_макс = QSpinBox()
        self.поле_макс.setRange(0, 7 * 24 * 3600)
        self.поле_макс.setSuffix(_(" с"))
        self.поле_макс.setSpecialValueText(_("не ограничено"))
        self.поле_макс.setValue(правила.max_seconds)
        self.поле_дата = QLineEdit()
        self.поле_дата.setPlaceholderText(_("ГГГГ-ММ-ДД — пусто: любые"))
        if правила.after:
            self.поле_дата.setText(f"{правила.after[:4]}-{правила.after[4:6]}-{правила.after[6:]}")
        форма.addRow(_("Не короче:"), self.поле_мин)
        форма.addRow(_("Не длиннее:"), self.поле_макс)
        форма.addRow(_("Не старше:"), self.поле_дата)
        столбец.addLayout(форма)

        self.ответ = QLabel("")
        self.ответ.setStyleSheet("color: #c62828;")
        self.ответ.setWordWrap(True)
        столбец.addWidget(self.ответ)

        кнопки = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        кнопки.accepted.connect(self._принять)
        кнопки.rejected.connect(self.reject)
        столбец.addWidget(кнопки)

    def собрать(self) -> Rules:
        """Правила из полей. Проходит через тот же разбор, что и файл:
        у окна и файла не должно быть двух мнений о том, что допустимо."""
        дата = self.поле_дата.text().strip()
        черновик = Rules(min_seconds=self.поле_мин.value(), max_seconds=self.поле_макс.value())
        текст = format_rules(черновик)
        if дата:
            текст = ";".join(часть for часть in (текст, f"after={дата}") if часть)
        return parse_rules(текст)

    def _принять(self) -> None:
        try:
            self.правила = self.собрать()
        except RulesError as ошибка:
            self.ответ.setText(str(ошибка))
            return
        self.accept()
