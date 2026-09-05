"""Есть ли то, без чего программа не работает.

Спрашивается один раз при запуске, а не выясняется через полчаса по невнятному
отказу yt-dlp. Цена вопроса — миллисекунды, а без проверки человек, поставивший
программу из репозитория, получает «сетевой сбой» вместо «поставьте node».

Отдельно от `core`: здесь смотрят на файловую систему и переменную PATH,
а ядро обязано проверяться без того и другого.
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Нехватка:
    """Чего не хватает и как это поставить именно на этой системе."""

    чего: str
    зачем: str
    как: str

    def __str__(self) -> str:
        return f"нет {self.чего} — {self.зачем}\n    поставить: {self.как}"


def _как_поставить(что: str) -> str:
    """Совет по системе. Одинаковый для всех был бы бесполезен ровно там,
    где он нужен: человек читает его, потому что не знает, что делать."""
    if sys.platform == "win32":
        подсказки = {
            "yt-dlp": "winget install yt-dlp  (или pip install yt-dlp)",
            "node": "winget install OpenJS.NodeJS",
            "ffmpeg": "winget install Gyan.FFmpeg",
        }
    elif sys.platform == "darwin":
        подсказки = {
            "yt-dlp": "brew install yt-dlp",
            "node": "brew install node",
            "ffmpeg": "brew install ffmpeg",
        }
    else:
        подсказки = {
            "yt-dlp": "pipx install yt-dlp  (или apt install yt-dlp)",
            "node": "apt install nodejs",
            "ffmpeg": "apt install ffmpeg",
        }
    return подсказки.get(что, что)


#: Что нужно и для чего. Порядок — по тому, насколько без этого всё встанет.
НУЖНОЕ = (
    ("yt-dlp", "качать нечем"),
    ("node", "без него YouTube отдаёт только раскадровки, а не сам ролик"),
    ("ffmpeg", "видео и звук приходят порознь, склеивать нечем"),
)


def чего_не_хватает(искать=shutil.which) -> list[Нехватка]:
    """Список нехваток. Пустой — всё на месте.

    `искать` подменяется в проверках: иначе они зависели бы от того,
    что установлено на машине, где их гоняют.
    """
    итог = []
    for что, зачем in НУЖНОЕ:
        if искать(что) is None:
            итог.append(Нехватка(чего=что, зачем=зачем, как=_как_поставить(что)))
    return итог


def как_поставить_qt() -> str:
    """Чем ставить окно. Путь к интерпретатору берём настоящий: советовать
    `.venv/Scripts/python.exe` тому, у кого Linux, — издевательство."""
    return f'{sys.executable} -m pip install "PySide6-Essentials"'
