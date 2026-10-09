"""Чем обновлять yt-dlp.

YouTube меняется чаще, чем выходят версии этой программы, и «yt-dlp устарел»
— самая частая причина, по которой выкачка встаёт. Чинится одной командой,
но какой именно — зависит от того, как yt-dlp попал на машину.

Здесь только выбор команды. Запускает её обёртка.
"""

from __future__ import annotations

from pathlib import PurePath

from core.install import YTDLP


def update_command(found: str | None, venv_bin: str, python: str) -> tuple[str, ...]:
    """Команда обновления. Пустая — yt-dlp не найден, обновлять нечего.

    * Лежит в окружении программы — ставили мы, обновляем тем же pip.
    * Лежит где-то ещё — ставил человек, и чем, мы не знаем. Просим сам
      yt-dlp: отдельный исполняемый файл обновится, а поставленный через
      pip или пакетный менеджер ответит, чем его обновлять. Этот ответ
      показывают человеку как есть — он точнее любой нашей догадки.
    """
    if not found:
        return ()
    if _внутри(found, venv_bin):
        # С довеском `[default]`: вместе с yt-dlp обновляется и решатель задач
        # YouTube. Они выходят парой, и отставший решатель — тот же отказ.
        return (python, "-m", "pip", "install", "--upgrade", YTDLP)
    return (found, "-U")


def _внутри(path: str, folder: str) -> bool:
    """Лежит ли файл прямо в этой папке. Регистр не важен: на Windows
    один и тот же путь приходит то `Scripts`, то `scripts`."""
    return str(PurePath(path).parent).casefold() == str(PurePath(folder)).casefold()
