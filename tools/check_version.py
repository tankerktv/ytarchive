"""Сверка версии проекта с тегом и чейнджлогом.

Разбор ведётся нормальным языком, а не `sed` с `grep`: цена ошибки здесь —
выпуск не той версии, а такое замечают уже у пользователей.

Два режима, как принято: по умолчанию только показывает, что видит;
валит сборку — только когда попросили явно.

    python tools/check_version.py                  отчёт
    python tools/check_version.py --tag v0.1.0     сверка с тегом, код 1 при расхождении
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:  # 3.11 и новее
    import tomllib
except ModuleNotFoundError:
    # 3.10: тот же разбор внешним пакетом. Без этого проверку нельзя
    # прогнать на машине разработки, а гонять её надо ДО тега, не в CI.
    import tomli as tomllib

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"

#: Раздел выпущенной версии: номер и дата. Пока раздел без даты — версия
#: не готова, и тег ставить нельзя. Это предохранитель, а не украшение.
RELEASED_SECTION = re.compile(
    r"^##\s*\[(?P<version>\d+\.\d+\.\d+)\]\s*[—-]\s*(?P<date>\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)


def project_version() -> str:
    with PYPROJECT.open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def released_versions() -> dict[str, str]:
    """Версии, у которых в чейнджлоге есть раздел С ДАТОЙ."""
    if not CHANGELOG.exists():
        return {}
    text = CHANGELOG.read_text(encoding="utf-8")
    return {m.group("version"): m.group("date") for m in RELEASED_SECTION.finditer(text)}


def strip_prefix(tag: str) -> str:
    return tag[1:] if tag.startswith("v") else tag


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="тег вида vX.Y.Z, с которым сверяемся")
    parser.add_argument(
        "--require-changelog",
        action="store_true",
        help="требовать раздел с датой в чейнджлоге",
    )
    args = parser.parse_args(argv)

    version = project_version()
    released = released_versions()

    print(f"версия в pyproject.toml: {version}")
    print(f"выпущенные разделы чейнджлога: {', '.join(sorted(released)) or 'нет ни одного'}")

    if args.tag is None:
        print("тег не задан — только отчёт, ничего не проверяю")
        return 0

    wanted = strip_prefix(args.tag)
    print(f"тег: {args.tag} (версия {wanted})")

    problems: list[str] = []
    if wanted != version:
        problems.append(
            f"версия в pyproject.toml ({version}) не совпадает с тегом ({wanted}). "
            "Магазин поставит одно, а приложение покажет другое"
        )
    if args.require_changelog and wanted not in released:
        problems.append(
            f"в CHANGELOG.md нет раздела «## [{wanted}] — ДАТА». "
            "Пока правки лежат под «Не выпущено», версия не готова"
        )

    if problems:
        print()
        for problem in problems:
            print(f"ОШИБКА: {problem}", file=sys.stderr)
        return 1

    print("сходится")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
