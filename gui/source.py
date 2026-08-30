"""Откуда окно берёт данные и как управляет заданием.

Отделено от окна намеренно: в тестах сюда подставляется поддельный источник,
и окно проверяется без файлов, без планировщика и без выкачки.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from core.locking import LockState, judge_lock
from runner.lockfile import STALE_AFTER, pid_alive, read_lock

#: Имя задания в планировщике. Менять только вместе с самим заданием.
TASK_NAME = "YouTube архив (непрерывная выкачка)"


@dataclass
class ArchiveSource:
    """Настоящий источник: файлы архива и задание планировщика."""

    base: Path
    archive_path: Path
    logs_dir: Path
    lock_path: Path
    task_name: str = TASK_NAME

    def log_tail(self, lines: int) -> list[str]:
        """Хвост самого свежего журнала.

        Отсутствие журналов — не беда: выкачка могла просто ни разу
        не запускаться. Возвращаем пустоту, а не жалобу.
        """
        try:
            журналы = sorted(
                self.logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True
            )
        except OSError:
            return []
        if not журналы:
            return []
        try:
            текст = журналы[0].read_text(encoding="utf-8", errors="replace")
        except OSError as ошибка:
            return [f"журнал не читается: {ошибка}"]
        return текст.splitlines()[-lines:]

    def archive_text(self) -> str:
        try:
            return self.archive_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def download_running(self) -> bool:
        """Идёт ли выкачка.

        Смотрим на замок, а не на свежесть журнала: журнал разрежен, и
        двухчасовой ролик выглядел бы в нём как многочасовой простой.
        Протухший замок считается свободным — его хозяин молчит слишком долго.
        """
        info = read_lock(self.lock_path)
        state = judge_lock(
            info,
            now=time.time(),
            pid_alive=pid_alive(info.pid) if info else False,
            stale_after=STALE_AFTER,
        )
        return state is LockState.HELD

    def start(self) -> str:
        return self._schtasks("/Run", "запустил задание")

    def stop(self) -> str:
        return self._schtasks("/End", "остановил задание")

    def _schtasks(self, ключ: str, успех: str) -> str:
        try:
            итог = subprocess.run(
                ["schtasks", ключ, "/TN", self.task_name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as ошибка:
            return f"не вышло: {ошибка}"
        if итог.returncode != 0:
            # Показываем ответ планировщика как есть: свои формулировки тут
            # только запутают, а его текст можно поискать в сети.
            return f"планировщик отказал: {(итог.stderr or итог.stdout).strip()[:200]}"
        return успех
