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

#: Где живут надписи. Ядро и цикл выкачки сюда не входят: их сообщения идут
#: в журнал, и перевод журнала — отдельная работа, ещё не сделанная.
ФАЙЛЫ = ("gui/window.py", "gui/videos.py", "gui/source.py")


def из_файла(путь: pathlib.Path) -> set[str]:
    """Строки-доводы всех вызовов `_(...)` в файле."""
    найдено: set[str] = set()
    дерево = ast.parse(путь.read_text(encoding="utf-8"))
    for узел in ast.walk(дерево):
        if not (isinstance(узел, ast.Call) and isinstance(узел.func, ast.Name)):
            continue
        if узел.func.id != "_" or not узел.args:
            continue
        первый = узел.args[0]
        if isinstance(первый, ast.Constant) and isinstance(первый.value, str):
            найдено.add(первый.value)
    return найдено


def собрать(корень: pathlib.Path | None = None) -> set[str]:
    основа = корень or КОРЕНЬ
    итог: set[str] = set()
    for имя in ФАЙЛЫ:
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
