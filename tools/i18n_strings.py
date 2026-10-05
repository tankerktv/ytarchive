"""Собрать надписи, обёрнутые в `_()`, — по коду, а не по памяти.

Служит двум хозяевам: этим списком наполняют словари и им же проверяют
их полноту. Один источник на оба дела намеренно — разойдись они, проверка
начала бы одобрять неполные словари.

    python tools/i18n_strings.py            показать список
    python tools/i18n_strings.py --count    только счёт
"""

from __future__ import annotations

import argparse
import ast
import pathlib

КОРЕНЬ = pathlib.Path(__file__).resolve().parent.parent

#: Где живут надписи — окно, командная строка и журнал.
ФАЙЛЫ = (
    "gui/window.py",
    "gui/videos.py",
    "gui/source.py",
    "gui/firstrun.py",
    "app/main.py",
    "runner/session.py",
    "runner/daemon.py",
    "install.py",
)

#: Ядро своих строк не переводит — оно принимает переводчик доводом и зовёт
#: его под именем `перевод`. Собирать надо и такие вызовы: иначе полнота
#: словарей проверялась бы мимо половины сообщений журнала.
ФАЙЛЫ_ЯДРА = ("core/flow.py", "core/locking.py", "core/search.py", "core/status.py")

ИМЕНА = ("_", "перевод")


def по_значению() -> set[str]:
    """Строки, которые переводятся по своему значению, а не вызовом `_("...")`.

    Состояния выкачки приходят из ядра готовым текстом и переводятся уже
    в окне. Разбор кода такого не находит — вызова с литералом нет. Поэтому
    перечисляем: иначе проверка полноты сочла бы их переводы лишними,
    а сами строки остались бы непереведёнными.
    """
    import sys

    sys.path.insert(0, str(КОРЕНЬ))
    from core.flow import HOPELESS
    from core.probe import Diagnosis
    from core.status import RunState

    #: Причины остановки хранятся по-русски и переводятся тем, кто показывает.
    #: Иначе выкачка, запущенная вчера по-русски, отдала бы окну русский текст,
    #: когда окно уже говорит по-немецки.
    свои = {
        "не удалось прочитать список каналов",
        "проверка не дала ответа",
    }
    return (
        {состояние.value for состояние in RunState}
        | {диагноз.value for диагноз in Diagnosis}
        | set(HOPELESS.values())
        | свои
    )


def из_файла(путь: pathlib.Path) -> set[str]:
    """Строки-доводы всех вызовов `_(...)` в файле."""
    найдено: set[str] = set()
    дерево = ast.parse(путь.read_text(encoding="utf-8"))
    for узел in ast.walk(дерево):
        if not (isinstance(узел, ast.Call) and isinstance(узел.func, ast.Name)):
            continue
        if узел.func.id not in ИМЕНА or not узел.args:
            continue
        первый = узел.args[0]
        if isinstance(первый, ast.Constant) and isinstance(первый.value, str):
            найдено.add(первый.value)
    return найдено


def собрать(корень: pathlib.Path | None = None) -> set[str]:
    основа = корень or КОРЕНЬ
    итог: set[str] = set(по_значению())
    for имя in ФАЙЛЫ + ФАЙЛЫ_ЯДРА:
        путь = основа / имя
        if путь.exists():
            итог |= из_файла(путь)
    return итог


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", action="store_true", help="только количество")
    args = parser.parse_args(argv)

    строки = собрать()
    if args.count:
        print(len(строки))
        return 0
    for строка in sorted(строки):
        print(repr(строка))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
