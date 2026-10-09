#!/usr/bin/env python3
"""Установщик: из скачанной папки — в работающую программу.

    python install.py              спросить, показать шаги, выполнить
    python install.py --dry-run    только показать шаги, ничего не трогая
    python install.py --yes        не спрашивать (для повторной установки)

Повторный запуск безопасен и полезен: он обновляет yt-dlp, а тот устаревает
за недели — YouTube меняется чаще, чем выходят версии этой программы.

Сам ничего не решает: список шагов строит `core/install.py`, здесь он
только исполняется. Пишет лишь в папку программы (`.venv`) и кладёт ярлыки;
прав администратора не просит и `sudo` не запускает.
"""

from __future__ import annotations

import sys

# Проверка версии — до всего остального и на двух языках: переводчик лежит
# в коде, который старый Python может не разобрать, а человек должен узнать
# причину, а не увидеть SyntaxError.
if sys.version_info < (3, 10):
    сейчас = "%d.%d" % sys.version_info[:2]
    print("ytarchive needs Python 3.10 or newer; this one is " + сейчас + ".")
    print("Нужен Python 3.10 или новее, а запущен " + сейчас + ".")
    raise SystemExit(2)

import argparse
import os
import shutil
import subprocess
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent
sys.path.insert(0, str(КОРЕНЬ))

from core.install import (  # noqa: E402
    SYSTEM_TOOLS,
    WINDOWS_SHORTCUT_SCRIPT,
    Found,
    Platform,
    Step,
    StepKind,
    Wishes,
    command_file,
    desktop_entry,
    known_managers,
    launch_agent,
    parse_answer,
    plan,
    platform_of,
    requirements,
    venv_python,
    windows_arguments,
)
from runner.language import _, настроить  # noqa: E402

ПУСКОВОЙ = КОРЕНЬ / "ytarchive.py"
ЗНАЧОК_ICO = КОРЕНЬ / "assets" / "ytarchive.ico"
ЗНАЧОК_SVG = КОРЕНЬ / "assets" / "logo.svg"

#: Имя задания launchd и файлов .desktop. Латиницей: это имена файлов,
#: которые человек будет искать, чтобы убрать программу.
МЕТКА = "org.ytarchive"


def осмотреться(платформа: Platform, искать=shutil.which) -> Found:
    return Found(
        platform=платформа,
        venv_exists=Path(venv_python(str(КОРЕНЬ), платформа)).exists(),
        missing_tools=tuple(имя for имя in SYSTEM_TOOLS if искать(имя) is None),
        managers=frozenset(имя for имя in known_managers(платформа) if искать(имя)),
    )


def спросить(вопрос: str, по_умолчанию: bool = True) -> bool:
    подсказка = _("[Д/н]") if по_умолчанию else _("[д/Н]")
    while True:
        try:
            ответ = input(f"{вопрос} {подсказка} ")
        except EOFError:
            return по_умолчанию
        решение = parse_answer(ответ, по_умолчанию)
        if решение is not None:
            return решение


def описание(шаг: Step) -> str:
    if шаг.kind is StepKind.VENV:
        return _("создать окружение Python в папке программы (.venv)")
    if шаг.kind is StepKind.PACKAGES:
        return _("поставить в окружение программы: {}").format(шаг.what)
    if шаг.kind is StepKind.TOOL:
        if not шаг.command:
            return _("{} — не найден, и я не знаю, чем его поставить на этой системе").format(
                шаг.what
            )
        if шаг.runnable:
            return _("поставить {}: {}").format(шаг.what, " ".join(шаг.command))
        return _("{} — поставьте сами: {}").format(шаг.what, " ".join(шаг.command))
    if шаг.kind is StepKind.SHORTCUT:
        return _("положить ярлык окна")
    return _("запускать выкачку при входе в систему")


def запустить(команда: list[str]) -> bool:
    print("    > " + " ".join(команда))
    try:
        return subprocess.run(команда, cwd=str(КОРЕНЬ)).returncode == 0
    except OSError as ошибка:
        print("    " + str(ошибка))
        return False


def создать_окружение() -> bool:
    if запустить([sys.executable, "-m", "venv", str(КОРЕНЬ / ".venv")]):
        return True
    # На Debian и Ubuntu модуль venv вынесен в отдельный пакет, и отказ
    # выглядит как невнятная жалоба на ensurepip.
    if shutil.which("apt-get"):
        print(_("    на Debian и Ubuntu сначала нужно: sudo apt-get install python3-venv"))
    return False


def поставить_пакеты(платформа: Platform, окно: bool) -> bool:
    питон = venv_python(str(КОРЕНЬ), платформа)
    return запустить([питон, "-m", "pip", "install", "--upgrade", *requirements(gui=окно)])


def _ярлык_windows(папка: str, имя: str, цель: str, доводы: tuple[str, ...]) -> str | None:
    окружение = dict(
        os.environ,
        YTA_FOLDER=папка,
        YTA_NAME=имя,
        YTA_TARGET=цель,
        YTA_ARGS=windows_arguments(доводы),
        YTA_WORKDIR=str(КОРЕНЬ),
        # Нет файла значка — берём значок самого интерпретатора, как было бы
        # и без этой строки. Ярлык обязан создаться в любом случае.
        YTA_ICON=str(ЗНАЧОК_ICO) if ЗНАЧОК_ICO.exists() else f"{цель},0",
    )
    try:
        итог = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", WINDOWS_SHORTCUT_SCRIPT],
            env=окружение,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    return итог.stdout.strip() or None if итог.returncode == 0 else None


def _записать(путь: Path, текст: str, исполняемый: bool = False) -> str | None:
    try:
        путь.parent.mkdir(parents=True, exist_ok=True)
        путь.write_text(текст, encoding="utf-8", newline="\n")
        if исполняемый:
            путь.chmod(0o755)
    except OSError as ошибка:
        print("    " + str(ошибка))
        return None
    return str(путь)


def _каталог_xdg(переменная: str, запасной: str) -> Path:
    значение = os.environ.get(переменная, "").strip()
    return Path(значение) if значение else Path.home() / запасной


def значок_linux() -> str:
    return str(ЗНАЧОК_SVG) if ЗНАЧОК_SVG.exists() else ""


def положить_ярлык(платформа: Platform) -> str | None:
    """Ярлык окна. Возвращает, куда положили, или None, если не вышло."""
    имя = _("Архив YouTube")
    доводы = (str(ПУСКОВОЙ), "gui")
    питон = venv_python(str(КОРЕНЬ), платформа, windowed=True)
    if платформа is Platform.WINDOWS:
        return _ярлык_windows("Desktop", имя, питон, доводы)
    if платформа is Platform.MACOS:
        return _записать(
            Path.home() / "Desktop" / (имя + ".command"),
            command_file((питон, *доводы)),
            исполняемый=True,
        )
    return _записать(
        _каталог_xdg("XDG_DATA_HOME", ".local/share") / "applications" / "ytarchive.desktop",
        desktop_entry(имя, _("Окно архива роликов"), (питон, *доводы), значок_linux()),
    )


def завести_автозапуск(платформа: Platform) -> str | None:
    имя = _("Архив YouTube — выкачка")
    доводы = (str(ПУСКОВОЙ), "daemon")
    питон = venv_python(str(КОРЕНЬ), платформа, windowed=True)
    if платформа is Platform.WINDOWS:
        return _ярлык_windows("Startup", имя, питон, доводы)
    if платформа is Platform.MACOS:
        return _записать(
            Path.home() / "Library" / "LaunchAgents" / (МЕТКА + ".daemon.plist"),
            launch_agent(МЕТКА + ".daemon", (питон, *доводы)),
        )
    return _записать(
        _каталог_xdg("XDG_CONFIG_HOME", ".config") / "autostart" / "ytarchive-daemon.desktop",
        desktop_entry(имя, _("Выкачка новых роликов в фоне"), (питон, *доводы), значок_linux()),
    )


def выполнить(шаг: Step, платформа: Platform, окно: bool, осталось: list[str]) -> bool:
    """Один шаг. False — дальше идти нельзя. То, что не удалось, но работе
    установщика не мешает, складывается в `осталось` и называется в конце:
    иначе человек увидит «готово» и не узнает, что ярлыка нет."""
    if шаг.kind is StepKind.VENV:
        return создать_окружение()
    if шаг.kind is StepKind.PACKAGES:
        return поставить_пакеты(платформа, окно)
    if шаг.kind is StepKind.TOOL:
        if шаг.runnable and запустить(list(шаг.command)):
            return True
        осталось.append(описание(Step(шаг.kind, шаг.what, шаг.command, runnable=False)))
        return True
    if шаг.kind is StepKind.SHORTCUT:
        куда = положить_ярлык(платформа)
    else:
        куда = завести_автозапуск(платформа)
    if куда:
        print("    " + куда)
    else:
        осталось.append(_("не получилось: {}").format(описание(шаг)))
    return True


def открыть_окно(платформа: Platform) -> None:
    питон = venv_python(str(КОРЕНЬ), платформа, windowed=True)
    try:
        subprocess.Popen([питон, str(ПУСКОВОЙ), "gui"], cwd=str(КОРЕНЬ))
    except OSError as ошибка:
        print(str(ошибка))


def main(argv: list[str] | None = None) -> int:
    for поток in (sys.stdout, sys.stderr):
        # Консоль Windows бывает в кодировке, где нет тире и многоточия.
        # Знак вопроса вместо тире лучше, чем падение посреди установки.
        try:
            поток.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass

    настроить("")

    parser = argparse.ArgumentParser(description=_("Установка ytarchive."))
    parser.add_argument(
        "--dry-run", action="store_true", help=_("только показать шаги, ничего не трогая")
    )
    parser.add_argument("--yes", action="store_true", help=_("не спрашивать"))
    parser.add_argument(
        "--no-gui", action="store_true", help=_("без окна: только командная строка и выкачка")
    )
    parser.add_argument("--no-shortcut", action="store_true", help=_("не класть ярлык окна"))
    parser.add_argument(
        "--no-autostart", action="store_true", help=_("не запускать выкачку при входе в систему")
    )
    args = parser.parse_args(argv)

    платформа = platform_of(sys.platform)
    разговор = not args.yes and not args.dry_run
    if разговор and not sys.stdin.isatty():
        print(_("Спросить некого: запустите в терминале или добавьте --yes."))
        return 2

    print(_("Установка ytarchive в {}").format(КОРЕНЬ))
    print(_("Python {} — подходит.").format("%d.%d.%d" % sys.version_info[:3]))
    print()

    окно = not args.no_gui
    ярлык = окно and not args.no_shortcut
    автозапуск = not args.no_autostart
    if разговор:
        if ярлык:
            ярлык = спросить(_("Положить ярлык, открывающий окно?"))
        if автозапуск:
            автозапуск = спросить(_("Запускать выкачку при входе в систему?"))
        print()

    найдено = осмотреться(платформа)
    шаги = plan(
        найдено, Wishes(gui=окно, shortcut=ярлык, autostart=автозапуск), sys.version_info[:2]
    )

    print(_("Что будет сделано:"))
    for номер, шаг in enumerate(шаги, 1):
        print(f"  {номер}. {описание(шаг)}")
    print()

    if args.dry_run:
        print(_("Вхолостую: ничего не тронуто."))
        return 0
    if разговор and not спросить(_("Выполнить?")):
        print(_("Отменено, ничего не тронуто."))
        return 0

    осталось: list[str] = []
    for номер, шаг in enumerate(шаги, 1):
        print(f"[{номер}/{len(шаги)}] {описание(шаг)}")
        if not выполнить(шаг, платформа, окно, осталось):
            print()
            print(_("Остановился на шаге {}: дальше без него нельзя.").format(номер))
            print(_("Исправьте причину и запустите установку ещё раз — сделанное не пропадёт."))
            return 1

    print()
    print(_("Готово."))
    if осталось:
        print(_("Осталось сделать руками:"))
        for строка in осталось:
            print("  - " + строка)
        print(_("После установки node и ffmpeg откройте новый терминал: старый их не увидит."))
    # В кавычках: путь с пробелом, скопированный без них, не запустится.
    питон = windows_arguments((venv_python(str(КОРЕНЬ), платформа),))
    пусковой = windows_arguments((str(ПУСКОВОЙ),))
    if окно:
        print(_("Открыть окно:  {} {} gui").format(питон, пусковой))
    else:
        # Без окна спросить папку архива некому — настройки создаёт команда.
        print(_("Создать настройки: {} {} init").format(питон, пусковой))
    print(_("Что дальше — куки YouTube и первый канал — написано в INSTALL.ru.md."))

    if разговор and окно and спросить(_("Открыть окно сейчас?")):
        открыть_окно(платформа)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
