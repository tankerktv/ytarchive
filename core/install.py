"""Что нужно сделать, чтобы программа заработала на чистой машине.

Здесь решения: что ставить, чем и в каком порядке, как выглядит ярлык.
Сама установка — в `install.py`, и она только исполняет этот список.

Отдельно, потому что установщик нельзя проверить, запуская его: каждая проба
ставила бы пакеты и разводила ярлыки по рабочему столу. А список шагов —
обычное значение, и проверяется за доли секунды на любой системе: шаги для
мака считаются и на Windows.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath, PureWindowsPath
from xml.sax.saxutils import escape

#: Младшая версия Python, на которой программа проверена.
MIN_PYTHON = (3, 10)

#: Что ставится в окружение всегда. yt-dlp — сюда же, а не «поставьте сами»:
#: без него программа бесполезна, а ставится он той же командой, что и всё.
#: Список повторяет `pyproject.toml`; расхождение ловит проверка.
REQUIRED = ('tomli>=2 ; python_version < "3.11"', "yt-dlp")

#: Что нужно окну.
GUI_REQUIRED = ("PySide6-Essentials>=6.6",)

#: Что pip поставить не может и за чем придётся идти к системе.
SYSTEM_TOOLS = ("node", "ffmpeg")


class Platform(Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


def platform_of(sys_platform: str) -> Platform:
    if sys_platform == "win32":
        return Platform.WINDOWS
    if sys_platform == "darwin":
        return Platform.MACOS
    # Всё остальное считаем линуксом: BSD с ним ближе, чем с чем-то ещё,
    # а отказ «не знаю вашу систему» хуже попытки.
    return Platform.LINUX


def python_ok(version: tuple[int, ...]) -> bool:
    return tuple(version[:2]) >= MIN_PYTHON


def venv_bin(root: str, platform: Platform) -> str:
    """Каталог с исполняемыми файлами окружения."""
    if platform is Platform.WINDOWS:
        return str(PureWindowsPath(root) / ".venv" / "Scripts")
    return str(PurePosixPath(root) / ".venv" / "bin")


def venv_python(root: str, platform: Platform, *, windowed: bool = False) -> str:
    """Интерпретатор окружения. `windowed` — без консоли: ярлык, открывающий
    чёрное окно рядом с программой, выглядит поломкой. Вне Windows разницы нет."""
    if platform is Platform.WINDOWS:
        имя = "pythonw.exe" if windowed else "python.exe"
        return str(PureWindowsPath(venv_bin(root, platform)) / имя)
    return str(PurePosixPath(venv_bin(root, platform)) / "python")


def requirements(*, gui: bool) -> tuple[str, ...]:
    return REQUIRED + (GUI_REQUIRED if gui else ())


# --- системные программы ---

#: Пакетные менеджеры в порядке предпочтения и то, как ими ставят.
#: Имена пакетов у всех свои: `node` в apt называется `nodejs`.
_MANAGERS = {
    Platform.WINDOWS: (
        (
            "winget",
            {
                "node": ("winget", "install", "--id", "OpenJS.NodeJS.LTS", "-e"),
                "ffmpeg": ("winget", "install", "--id", "Gyan.FFmpeg", "-e"),
            },
        ),
    ),
    Platform.MACOS: (
        (
            "brew",
            {
                "node": ("brew", "install", "node"),
                "ffmpeg": ("brew", "install", "ffmpeg"),
            },
        ),
    ),
    Platform.LINUX: (
        (
            "apt-get",
            {
                "node": ("sudo", "apt-get", "install", "-y", "nodejs"),
                "ffmpeg": ("sudo", "apt-get", "install", "-y", "ffmpeg"),
            },
        ),
        (
            "dnf",
            {
                "node": ("sudo", "dnf", "install", "-y", "nodejs"),
                "ffmpeg": ("sudo", "dnf", "install", "-y", "ffmpeg"),
            },
        ),
        (
            "pacman",
            {
                "node": ("sudo", "pacman", "-S", "--needed", "nodejs"),
                "ffmpeg": ("sudo", "pacman", "-S", "--needed", "ffmpeg"),
            },
        ),
        (
            "zypper",
            {
                "node": ("sudo", "zypper", "install", "-y", "nodejs"),
                "ffmpeg": ("sudo", "zypper", "install", "-y", "ffmpeg"),
            },
        ),
    ),
}


def known_managers(platform: Platform) -> tuple[str, ...]:
    """Какие менеджеры искать на этой системе."""
    return tuple(имя for имя, _команды in _MANAGERS[platform])


@dataclass(frozen=True)
class ToolAdvice:
    """Как поставить системную программу.

    `runnable` — можно ли запустить команду самим. Команду с `sudo` не
    запускаем никогда: пароль администратора установщику архиватора роликов
    не нужен, и просить его — приучать человека вводить его куда попало.
    """

    tool: str
    command: tuple[str, ...]
    runnable: bool


def tool_advice(platform: Platform, tool: str, managers: frozenset[str]) -> ToolAdvice:
    for имя, команды in _MANAGERS[platform]:
        if имя in managers and tool in команды:
            команда = команды[tool]
            return ToolAdvice(tool=tool, command=команда, runnable=команда[0] != "sudo")
    # Менеджера нет — команды тоже нет. Пустая команда честнее выдуманной:
    # совет «winget install», когда winget отсутствует, только добавит ошибок.
    return ToolAdvice(tool=tool, command=(), runnable=False)


# --- список шагов ---


class StepKind(Enum):
    VENV = "venv"
    PACKAGES = "packages"
    TOOL = "tool"
    SHORTCUT = "shortcut"
    AUTOSTART = "autostart"


@dataclass(frozen=True)
class Step:
    kind: StepKind
    #: Что именно: пакеты через пробел, имя программы. Для показа человеку.
    what: str = ""
    command: tuple[str, ...] = ()
    #: Делаем сами или только говорим, что сделать.
    runnable: bool = True


@dataclass(frozen=True)
class Found:
    """Что обнаружено на машине."""

    platform: Platform
    venv_exists: bool = False
    #: Чего из SYSTEM_TOOLS нет в PATH.
    missing_tools: tuple[str, ...] = ()
    managers: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Wishes:
    """Что попросил человек."""

    gui: bool = True
    shortcut: bool = True
    autostart: bool = True


def plan(found: Found, wishes: Wishes, python: tuple[int, ...] = MIN_PYTHON) -> list[Step]:
    """Шаги установки по порядку.

    Пакеты ставятся и тогда, когда окружение уже есть: повторный запуск
    установщика — это способ обновить yt-dlp, а он устаревает за недели.
    """
    шаги: list[Step] = []
    if not found.venv_exists:
        шаги.append(Step(StepKind.VENV))

    шаги.append(Step(StepKind.PACKAGES, what=" ".join(_имена(requirements(gui=wishes.gui), python))))

    for программа in SYSTEM_TOOLS:
        if программа in found.missing_tools:
            совет = tool_advice(found.platform, программа, found.managers)
            шаги.append(
                Step(StepKind.TOOL, what=программа, command=совет.command, runnable=совет.runnable)
            )

    # Ярлык открывает окно. Без окна он открывал бы отказ «нет PySide6».
    if wishes.shortcut and wishes.gui:
        шаги.append(Step(StepKind.SHORTCUT))
    if wishes.autostart:
        шаги.append(Step(StepKind.AUTOSTART))
    return шаги


def _имена(требования: tuple[str, ...], python: tuple[int, ...]) -> list[str]:
    """Имена пакетов без версий и условий — для показа, не для pip.

    Пакет с условием «только для старого Python» на новом не показываем:
    pip его пропустит, и обещание «поставлю tomli» оказалось бы неправдой.
    """
    итог = []
    for требование in требования:
        имя, _знак, условие = требование.partition(";")
        if 'python_version < "3.11"' in условие and tuple(python[:2]) >= (3, 11):
            continue
        for знак in (">=", "==", "<", ">", "~="):
            имя = имя.split(знак, 1)[0]
        итог.append(имя.strip())
    return итог


# --- ярлыки ---

#: Ярлык Windows создаётся через WScript.Shell: формат .lnk двоичный, а другого
#: способа без сторонних пакетов нет. Значения приходят переменными окружения,
#: а не подставляются в текст: путь с апострофом или `$` в имени пользователя
#: иначе превратился бы в исполняемый код.
#:
#: Папку спрашиваем у системы: рабочий стол бывает перенесён в OneDrive,
#: и `~/Desktop` тогда — не тот каталог, который видит человек.
WINDOWS_SHORTCUT_SCRIPT = (
    "$ErrorActionPreference = 'Stop'; "
    # Иначе путь с русскими буквами вернётся в кодировке консоли и в отчёте
    # установщика превратится в кракозябры.
    "[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
    "$folder = [Environment]::GetFolderPath($env:YTA_FOLDER); "
    "$path = Join-Path $folder ($env:YTA_NAME + '.lnk'); "
    "$link = (New-Object -ComObject WScript.Shell).CreateShortcut($path); "
    "$link.TargetPath = $env:YTA_TARGET; "
    "$link.Arguments = $env:YTA_ARGS; "
    "$link.WorkingDirectory = $env:YTA_WORKDIR; "
    "$link.Save(); "
    "Write-Output $path"
)


def windows_arguments(argv: tuple[str, ...]) -> str:
    """Доводы для поля ярлыка. Путь с пробелом без кавычек разрезается надвое,
    а каталог пользователя с пробелом в имени — обычное дело."""
    части = []
    for довод in argv:
        части.append(f'"{довод}"' if (" " in довод or not довод) else довод)
    return " ".join(части)


def _exec_quote(довод: str) -> str:
    """Кавычки по правилам поля Exec: внутри двойных экранируются
    обратная черта, кавычка, обратный апостроф и доллар; процент удваивается."""
    внутри = довод.replace("\\", "\\\\")
    for знак in ('"', "`", "$"):
        внутри = внутри.replace(знак, "\\" + знак)
    return '"' + внутри.replace("%", "%%") + '"'


def desktop_entry(name: str, comment: str, argv: tuple[str, ...]) -> str:
    """Файл .desktop — и ярлык в меню, и автозапуск: формат у них один."""
    строки = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={name}",
        f"Comment={comment}",
        "Exec=" + " ".join(_exec_quote(довод) for довод in argv),
        "Terminal=false",
        "Categories=AudioVideo;Network;",
    ]
    return "\n".join(строки) + "\n"


def launch_agent(label: str, argv: tuple[str, ...]) -> str:
    """Задание launchd для автозапуска на маке. На живой машине не проверялось."""
    доводы = "\n".join(f"        <string>{escape(довод)}</string>" for довод in argv)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n'
        "<dict>\n"
        "    <key>Label</key>\n"
        f"    <string>{escape(label)}</string>\n"
        "    <key>ProgramArguments</key>\n"
        "    <array>\n"
        f"{доводы}\n"
        "    </array>\n"
        "    <key>RunAtLoad</key>\n"
        "    <true/>\n"
        "</dict>\n"
        "</plist>\n"
    )


def command_file(argv: tuple[str, ...]) -> str:
    """Файл .command для мака: его открывают двойным щелчком из Finder."""
    слова = " ".join("'" + довод.replace("'", "'\\''") + "'" for довод in argv)
    return f"#!/bin/sh\nexec {слова}\n"


# --- разговор ---

#: «Да» и «нет» на всех языках программы и по-английски сверх того: человек
#: отвечает на своём языке, а не на том, который угадал установщик.
_ДА = frozenset({"y", "yes", "д", "да", "j", "ja", "s", "si", "sí", "o", "oui"})
_НЕТ = frozenset({"n", "no", "н", "нет", "nein", "non"})


def parse_answer(text: str, default: bool) -> bool | None:
    """Ответ на вопрос «да или нет». Пустой — значение по умолчанию.

    None значит «не понял»: переспросить честнее, чем принять опечатку
    за согласие на установку.
    """
    слово = text.strip().lower()
    if not слово:
        return default
    if слово in _ДА:
        return True
    if слово in _НЕТ:
        return False
    return None


# --- поиск программ ---


def extend_path(current: str, extra: str, separator: str) -> str:
    """Дописать каталог В КОНЕЦ списка поиска программ.

    Нужно, чтобы yt-dlp, поставленный установщиком в окружение программы,
    находился и при запуске с ярлыка, где окружение никто не «включал».

    Именно в конец: если у человека уже стоит свой yt-dlp, работать должен
    он — его обновляют привычным способом, и подмена молча вернула бы
    старую версию.
    """
    части = [часть for часть in current.split(separator) if часть]
    if extra in части:
        return current
    return separator.join([*части, extra])
