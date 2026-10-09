#!/usr/bin/env python3
"""Пусковой файл.

Существует ради одной вещи: запуск скриптом кладёт каталог этого файла
в пути поиска модулей автоматически, а `python -m app.main` полагается на
текущий каталог. Планировщик задач с каталогами обращается по-своему —
задание падало с кодом 103, не дойдя до программы.

Настройки берутся рядом с этим файлом, если не указано иное: так задание
работает независимо от того, откуда его позвали.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import CONFIG_NAME, main  # noqa: E402
from core.install import extend_path  # noqa: E402

# Программы, поставленные в окружение (yt-dlp), лежат рядом с интерпретатором.
# С ярлыка окружение никто не «включает», и без этого их было бы не найти.
# Свой каталог — первым: работать должна та копия, которую программа ставит
# и обновляет сама.
os.environ["PATH"] = extend_path(
    os.environ.get("PATH", ""), str(Path(sys.executable).parent), os.pathsep
)

if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--config" not in argv:
        argv = ["--config", str(Path(__file__).resolve().parent / CONFIG_NAME), *argv]
    raise SystemExit(main(argv))
