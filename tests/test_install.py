"""Список шагов установки и содержимое ярлыков.

Установщик нельзя проверять запуском: каждая проба ставила бы пакеты и
оставляла ярлыки на рабочем столе. Поэтому решения вынесены в ядро и
проверяются здесь — для всех трёх систем разом, на какой бы ни гонялись.
"""

from pathlib import Path

import pytest

from core.install import (
    GUI_REQUIRED,
    REQUIRED,
    WINDOWS_SHORTCUT_SCRIPT,
    Found,
    Platform,
    StepKind,
    Wishes,
    command_file,
    desktop_entry,
    extend_path,
    known_managers,
    launch_agent,
    parse_answer,
    plan,
    platform_of,
    python_ok,
    requirements,
    tool_advice,
    venv_python,
    windows_arguments,
)

КОРЕНЬ = Path(__file__).resolve().parents[1]


def виды(шаги):
    return [шаг.kind for шаг in шаги]


# --- версия и система ---


@pytest.mark.parametrize(
    "версия, годится",
    [((3, 9, 18), False), ((3, 10, 0), True), ((3, 10, 6), True), ((3, 13, 1), True), ((2, 7), False)],
)
def test_версия_python(версия, годится):
    assert python_ok(версия) is годится


def test_неизвестная_система_считается_линуксом():
    """Отказ «не знаю вашу систему» хуже попытки."""
    assert platform_of("win32") is Platform.WINDOWS
    assert platform_of("darwin") is Platform.MACOS
    assert platform_of("linux") is Platform.LINUX
    assert platform_of("freebsd14") is Platform.LINUX


def test_интерпретатор_окружения_на_каждой_системе():
    assert venv_python(r"C:\Program Files\yta", Platform.WINDOWS) == (
        r"C:\Program Files\yta\.venv\Scripts\python.exe"
    )
    assert venv_python("/opt/yta", Platform.LINUX) == "/opt/yta/.venv/bin/python"
    assert venv_python("/opt/yta", Platform.MACOS) == "/opt/yta/.venv/bin/python"


def test_ярлык_на_windows_без_консоли():
    """Иначе рядом с окном программы открывается чёрное окно — выглядит поломкой."""
    assert venv_python(r"C:\yta", Platform.WINDOWS, windowed=True).endswith("pythonw.exe")
    assert venv_python("/opt/yta", Platform.LINUX, windowed=True).endswith("/python")


# --- что ставится ---


def test_список_пакетов_не_разошёлся_с_pyproject():
    """Список в установщике повторяет `pyproject.toml`: установщик работает
    на голом Python, где разобрать TOML ещё нечем. Повтор без сверки
    разойдётся при первом же обновлении зависимостей."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    проект = tomllib.loads((КОРЕНЬ / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    for требование in проект["dependencies"]:
        assert требование in REQUIRED
    assert tuple(проект["optional-dependencies"]["gui"]) == GUI_REQUIRED


def test_yt_dlp_ставится_всегда():
    """Без него программа бесполезна, и «поставьте сами» здесь — лишний шаг,
    на котором новичок и застрянет."""
    assert "yt-dlp[default]" in requirements(gui=False)
    assert "yt-dlp[default]" in requirements(gui=True)


def test_yt_dlp_ставится_с_решателем_задач():
    """Настоящий случай, выпуск 0.3.0: установщик ставил голый `yt-dlp`, без
    решателя задач YouTube. Программа устанавливалась без единой ошибки и не
    могла скачать ни одного ролика — «Only images are available for download».
    Нашлось, когда установщик впервые прошёл на машине автора."""
    assert "yt-dlp" not in requirements(gui=False), "голый yt-dlp ставится без решателя"
    шаг = next(ш for ш in plan(Found(Platform.LINUX), Wishes()) if ш.kind is StepKind.PACKAGES)
    assert "yt-dlp" in шаг.what.split(), "человеку показываем имя без довеска"


def test_qt_ставится_только_с_окном():
    assert not any("PySide6" in имя for имя in requirements(gui=False))
    assert any("PySide6" in имя for имя in requirements(gui=True))


# --- список шагов ---


def test_чистая_машина_полный_путь():
    шаги = plan(Found(Platform.WINDOWS), Wishes())
    assert виды(шаги) == [
        StepKind.VENV,
        StepKind.PACKAGES,
        StepKind.SHORTCUT,
        StepKind.AUTOSTART,
    ]


def test_повторный_запуск_обновляет_пакеты():
    """Повторная установка — способ обновить yt-dlp. Пропусти мы пакеты,
    раз окружение уже есть, обновить его было бы нечем."""
    шаги = plan(Found(Platform.LINUX, venv_exists=True), Wishes())
    assert StepKind.VENV not in виды(шаги)
    assert StepKind.PACKAGES in виды(шаги)


def test_без_окна_ярлык_не_кладётся():
    """Ярлык открывает окно; без окна он открывал бы отказ «нет PySide6»."""
    шаги = plan(Found(Platform.WINDOWS), Wishes(gui=False, shortcut=True))
    assert StepKind.SHORTCUT not in виды(шаги)
    assert StepKind.AUTOSTART in виды(шаги)
    пакеты = next(шаг for шаг in шаги if шаг.kind is StepKind.PACKAGES)
    assert "PySide6" not in пакеты.what


def test_отказ_от_ярлыка_и_автозапуска_уважается():
    шаги = plan(Found(Platform.MACOS), Wishes(shortcut=False, autostart=False))
    assert виды(шаги) == [StepKind.VENV, StepKind.PACKAGES]


def test_недостающие_программы_попадают_в_шаги():
    найдено = Found(
        Platform.WINDOWS, missing_tools=("node", "ffmpeg"), managers=frozenset({"winget"})
    )
    программы = [шаг for шаг in plan(найдено, Wishes()) if шаг.kind is StepKind.TOOL]
    assert [шаг.what for шаг in программы] == ["node", "ffmpeg"]
    assert all(шаг.runnable and шаг.command[0] == "winget" for шаг in программы)


def test_что_уже_стоит_не_ставится():
    найдено = Found(Platform.WINDOWS, missing_tools=("ffmpeg",), managers=frozenset({"winget"}))
    программы = [шаг.what for шаг in plan(найдено, Wishes()) if шаг.kind is StepKind.TOOL]
    assert программы == ["ffmpeg"]


# --- системные программы ---


def test_sudo_сами_не_запускаем():
    """Пароль администратора установщику архиватора не нужен, и просить его —
    приучать человека вводить его куда попало."""
    for менеджер in known_managers(Platform.LINUX):
        совет = tool_advice(Platform.LINUX, "node", frozenset({менеджер}))
        assert совет.command[0] == "sudo"
        assert совет.runnable is False


def test_node_в_apt_называется_иначе():
    совет = tool_advice(Platform.LINUX, "node", frozenset({"apt-get"}))
    assert совет.command[-1] == "nodejs"


def test_без_менеджера_команду_не_выдумываем():
    """Совет «winget install» там, где winget нет, только добавит ошибок."""
    совет = tool_advice(Platform.WINDOWS, "node", frozenset())
    assert совет.command == ()
    assert совет.runnable is False


def test_на_маке_ставит_brew():
    совет = tool_advice(Platform.MACOS, "ffmpeg", frozenset({"brew"}))
    assert совет.command == ("brew", "install", "ffmpeg")
    assert совет.runnable is True


def test_из_нескольких_менеджеров_берётся_первый_по_порядку():
    совет = tool_advice(Platform.LINUX, "ffmpeg", frozenset({"pacman", "apt-get"}))
    assert "apt-get" in совет.command


# --- ярлыки ---


def test_путь_с_пробелом_в_ярлыке_берётся_в_кавычки():
    """Каталог пользователя с пробелом в имени — обычное дело; без кавычек
    путь разрезается надвое, и ярлык открывает «файл не найден»."""
    доводы = windows_arguments((r"C:\Users\Ivan Petrov\ytarchive\ytarchive.py", "gui"))
    assert доводы == r'"C:\Users\Ivan Petrov\ytarchive\ytarchive.py" gui'


def test_значения_в_сценарий_ярлыка_не_подставляются():
    """Путь с апострофом или долларом, вклеенный в текст сценария, стал бы
    исполняемым кодом. Значения идут переменными окружения."""
    for имя in ("YTA_FOLDER", "YTA_NAME", "YTA_TARGET", "YTA_ARGS", "YTA_WORKDIR"):
        assert f"$env:{имя}" in WINDOWS_SHORTCUT_SCRIPT
    assert "{" not in WINDOWS_SHORTCUT_SCRIPT


def test_файл_desktop_собирается():
    текст = desktop_entry(
        "Архив YouTube", "Окно", ("/home/u/my apps/.venv/bin/python", "/home/u/my apps/ytarchive.py", "gui")
    )
    assert текст.startswith("[Desktop Entry]\n")
    assert "Name=Архив YouTube\n" in текст
    assert 'Exec="/home/u/my apps/.venv/bin/python" "/home/u/my apps/ytarchive.py" "gui"\n' in текст
    assert "Terminal=false" in текст


def test_особые_знаки_в_exec_экранируются():
    """Доллар и процент в поле Exec значащие: путь `/home/a$b/100%` без
    экранирования запустил бы не то или не запустился бы вовсе."""
    текст = desktop_entry("x", "y", ("/home/a$b/100%/py",))
    assert 'Exec="/home/a\\$b/100%%/py"' in текст


def test_задание_launchd_экранирует_xml():
    текст = launch_agent("org.ytarchive.daemon", ("/Users/a&b/python", "ytarchive.py", "daemon"))
    assert "<string>org.ytarchive.daemon</string>" in текст
    assert "<string>/Users/a&amp;b/python</string>" in текст
    assert "<key>RunAtLoad</key>" in текст


def test_файл_command_выдерживает_пробел_и_апостроф():
    текст = command_file(("/Users/O'Neil/my apps/python", "gui"))
    assert текст.startswith("#!/bin/sh\n")
    assert "exec '/Users/O'\\''Neil/my apps/python' 'gui'" in текст


# --- разговор ---


@pytest.mark.parametrize("слово", ["y", "Y", "yes", "д", "Да", "ja", "oui", "sí", " si "])
def test_да_на_всех_языках(слово):
    assert parse_answer(слово, default=False) is True


@pytest.mark.parametrize("слово", ["n", "No", "н", "нет", "nein", "non"])
def test_нет_на_всех_языках(слово):
    assert parse_answer(слово, default=True) is False


def test_пустой_ответ_значит_по_умолчанию():
    assert parse_answer("", default=True) is True
    assert parse_answer("  ", default=False) is False


def test_непонятный_ответ_не_считается_согласием():
    """Опечатку нельзя принимать за «да»: за ней идёт установка."""
    assert parse_answer("lf", default=True) is None
    assert parse_answer("maybe", default=False) is None


# --- поиск программ ---


def test_каталог_окружения_идёт_первым():
    """Настоящий случай: общий yt-dlp стоял через pip в старом Python и
    обновиться не мог, а свежий из окружения программы до работы не доходил.
    Кнопка «Обновить yt-dlp» обновляла копию, которой никто не пользовался."""
    итог = extend_path("/usr/bin:/bin", "/opt/yta/.venv/bin", ":")
    assert итог == "/opt/yta/.venv/bin:/usr/bin:/bin"


def test_каталог_уже_в_списке_переезжает_в_начало_а_не_двоится():
    путь = r"C:\Windows;C:\yta\.venv\Scripts;C:\Tools"
    assert extend_path(путь, r"C:\yta\.venv\Scripts", ";") == r"C:\yta\.venv\Scripts;C:\Windows;C:\Tools"


def test_пустой_список_поиска():
    assert extend_path("", "/opt/yta/.venv/bin", ":") == "/opt/yta/.venv/bin"



def test_пакет_для_старого_python_на_новом_не_обещаем():
    """pip такой пакет пропускает; строка «поставлю tomli» была бы неправдой."""
    старый = next(ш for ш in plan(Found(Platform.LINUX), Wishes(), (3, 10)) if ш.kind is StepKind.PACKAGES)
    новый = next(ш for ш in plan(Found(Platform.LINUX), Wishes(), (3, 12)) if ш.kind is StepKind.PACKAGES)
    assert "tomli" in старый.what
    assert "tomli" not in новый.what
    assert "yt-dlp" in новый.what
