"""Обернуть надписи в `_()` — разово, при переводе интерфейса на языки.

Руками это полторы сотни правок, и каждая — шанс промахнуться мимо кавычки.
Разбор кода делает то же самое механически, а `--apply` отделён от отчёта
намеренно: сначала смотрим, что получится, потом правим.

Оставлено в репозитории не из бережливости, а потому что понадобится снова:
надписи прибывают, и следующий заход должен быть таким же дешёвым.

    python tools/wrap_strings.py gui/window.py           показать
    python tools/wrap_strings.py gui/window.py --apply   переписать
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

КИРИЛЛИЦА = re.compile(r"[А-Яа-яЁё]")


def докстринги(дерево: ast.AST) -> set[int]:
    """Строки-пояснения — по номеру узла. Их не переводят: их читает тот,
    кто открыл исходник, а он и так справится."""
    свои = set()
    for узел in ast.walk(дерево):
        if isinstance(узел, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            тело = getattr(узел, "body", [])
            if тело and isinstance(тело[0], ast.Expr) and isinstance(тело[0].value, ast.Constant):
                свои.add(id(тело[0].value))
        if isinstance(узел, ast.Expr) and isinstance(узел.value, ast.Constant) \
                and isinstance(узел.value.value, str):
            свои.add(id(узел.value))
    return свои


def уже_обёрнута(родители: dict, узел: ast.AST) -> bool:
    род = родители.get(id(узел))
    return (
        isinstance(род, ast.Call)
        and isinstance(род.func, ast.Name)
        and род.func.id == "_"
    )


def шаблон_фстроки(узел: ast.JoinedStr, исходник: str) -> tuple[str, list[str]] | None:
    """Разложить f-строку на переводимый шаблон и подстановки.

    `f"осталось {n} шт"` → `("осталось {} шт", ["n"])`. Так переводчику
    достаётся связная фраза, а не обрывки вокруг дырок.

    `None` значит «не берусь»: вложенные шаблоны в спецификаторе формата
    встречаются редко, и разбирать их ради трёх мест не стоит.
    """
    куски: list[str] = []
    доводы: list[str] = []
    for часть in узел.values:
        if isinstance(часть, ast.Constant) and isinstance(часть.value, str):
            куски.append(часть.value.replace("{", "{{").replace("}", "}}"))
            continue
        if not isinstance(часть, ast.FormattedValue):
            return None

        спец = ""
        if часть.format_spec is not None:
            if not isinstance(часть.format_spec, ast.JoinedStr):
                return None
            for под in часть.format_spec.values:
                if not (isinstance(под, ast.Constant) and isinstance(под.value, str)):
                    return None  # спецификатор сам с подстановкой — не берёмся
                спец += под.value

        преобразование = f"!{chr(часть.conversion)}" if часть.conversion and часть.conversion > 0 else ""
        куски.append("{" + преобразование + (f":{спец}" if спец else "") + "}")

        текст = ast.get_source_segment(исходник, часть.value)
        if текст is None:
            return None
        доводы.append(текст)

    return "".join(куски), доводы


def правки(путь: pathlib.Path) -> list[tuple[int, int, str, str]]:
    """Найти, что заменить: (начало, конец, было, стало).

    Смещения — В БАЙТАХ, и это не придирка: Python считает колонки узлов
    в байтах UTF-8. На кириллице байт и символ — разное, и резка по символам
    съезжает ровно там, где надписи по-русски, то есть везде.
    """
    исходник = путь.read_text(encoding="utf-8")
    байты = исходник.encode("utf-8")
    дерево = ast.parse(исходник)

    родители = {}
    for узел in ast.walk(дерево):
        for ребёнок in ast.iter_child_nodes(узел):
            родители[id(ребёнок)] = узел

    пропустить = докстринги(дерево)

    # Куски f-строк — тоже Constant. Не отметив их, мы заменили бы и всю
    # f-строку, и её обрывки по отдельности: правки наложились бы друг
    # на друга и порвали код.
    внутри_фстроки = set()
    for узел in ast.walk(дерево):
        if isinstance(узел, ast.JoinedStr):
            for под in ast.walk(узел):
                if под is not узел:
                    внутри_фстроки.add(id(под))

    начала = [0]
    for строка in байты.splitlines(keepends=True):
        начала.append(начала[-1] + len(строка))

    def место(узел) -> tuple[int, int]:
        return (
            начала[узел.lineno - 1] + узел.col_offset,
            начала[узел.end_lineno - 1] + узел.end_col_offset,
        )

    def кусок(начало: int, конец: int) -> str:
        return байты[начало:конец].decode("utf-8")

    найдено = []
    for узел in ast.walk(дерево):
        if isinstance(узел, ast.JoinedStr):
            куски = [ч.value for ч in узел.values
                     if isinstance(ч, ast.Constant) and isinstance(ч.value, str)]
            if not any(КИРИЛЛИЦА.search(к) for к in куски):
                continue
            if уже_обёрнута(родители, узел) or id(узел) in внутри_фстроки:
                continue
            разбор = шаблон_фстроки(узел, исходник)
            if разбор is None:
                continue
            шаблон, доводы = разбор
            хвост = f".format({', '.join(доводы)})" if доводы else ""
            начало, конец = место(узел)
            найдено.append((начало, конец, кусок(начало, конец), f"_({шаблон!r}){хвост}"))
            continue

        if isinstance(узел, ast.Constant) and isinstance(узел.value, str):
            if id(узел) in пропустить or id(узел) in внутри_фстроки:
                continue
            if not КИРИЛЛИЦА.search(узел.value) or уже_обёрнута(родители, узел):
                continue
            начало, конец = место(узел)
            найдено.append((начало, конец, кусок(начало, конец), f"_({кусок(начало, конец)})"))

    # С конца: иначе смещения поедут после первой же замены.
    return sorted(найдено, key=lambda п: п[0], reverse=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--apply", action="store_true", help="переписать, а не показать")
    args = parser.parse_args(argv)

    всего = 0
    for имя in args.files:
        путь = pathlib.Path(имя)
        найденное = правки(путь)
        всего += len(найденное)
        print(f"{путь}: мест {len(найденное)}")
        if not args.apply:
            for _, _, было, стало in найденное[:4]:
                print(f"    {было[:60]}  ->  {стало[:70]}")
            continue

        байты = путь.read_text(encoding="utf-8").encode("utf-8")
        for начало, конец, _, стало in найденное:
            байты = байты[:начало] + стало.encode("utf-8") + байты[конец:]
        текст = байты.decode("utf-8")
        try:
            ast.parse(текст)
        except SyntaxError as ошибка:
            # Ничего не записываем: файл с ошибкой разбора хуже неправленого.
            print(f"  ОТКАЗ: после правки не разбирается — {ошибка}", file=sys.stderr)
            return 1
        путь.write_text(текст, encoding="utf-8", newline="\n")
        print("  переписан")

    print(f"итого мест: {всего}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
