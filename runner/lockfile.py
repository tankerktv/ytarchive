"""Замок файлом: запись, отметки, проверка живости процесса.

Решение принимает `core.locking.judge_lock`, здесь только работа с файлом
и с подсистемой процессов.

Формат — две строки: идентификатор процесса и отметка времени. Простой
намеренно: этот файл читают и когда всё сломалось, в том числе глазами.
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from core.locking import LockInfo, LockState, describe, judge_lock

#: Через сколько молчания замок считается протухшим. С запасом относительно
#: предела надзорщика (180 с): здоровый экземпляр отмечается куда чаще,
#: а отобрать замок у работающей выкачки хуже, чем подождать лишнее.
STALE_AFTER = 600.0


def pid_alive(pid: int) -> bool:
    """Числится ли процесс живым.

    На Windows `os.kill(pid, 0)` не годится: сигнала 0 там нет, вызов падает
    с WinError 87, и Python превращает это в SystemError мимо обычных
    перехватов. Поймано самопроверкой окна — до неё замок молча ронял всё,
    что его спрашивало. Поэтому здесь честная развилка по системе.
    """
    if pid <= 0:
        return False

    if sys.platform == "win32":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                # Завершившийся процесс ещё отдаёт дескриптор, пока его держат:
                # живым считаем только того, кто действительно не вышел.
                return code.value == STILL_ACTIVE
            return True
        finally:
            kernel32.CloseHandle(handle)

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Процесс есть, просто чужой — это тоже «жив».
        return True
    except OSError:
        return False
    return True


def read_lock(path: Path) -> LockInfo | None:
    """Прочитать замок. Испорченный файл — это отсутствие замка, а не отказ:
    иначе один битый байт остановит выкачку насовсем."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return LockInfo(pid=int(lines[0].strip()), heartbeat=float(lines[1].strip()))
    except (OSError, IndexError, ValueError):
        return None


@dataclass
class Lock:
    """Замок, который надо не забывать отмечать."""

    path: Path
    state: LockState
    previous: LockInfo | None

    def heartbeat(self) -> None:
        """Отметиться. Зовётся из цикла выкачки, чтобы замок не протух
        под живой работой."""
        self._write()

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(f"{os.getpid()}\n{time.time()}\n", encoding="utf-8", newline="\n")

    def release(self) -> None:
        """Отдать замок. Чужой не трогаем: если пока мы работали его забрал
        кто-то другой, удалять его файл — значит впустить третьего."""
        info = read_lock(self.path)
        if info is not None and info.pid != os.getpid():
            return
        try:
            self.path.unlink()
        except OSError:
            pass

    def __enter__(self) -> Lock:
        return self

    def __exit__(self, *_) -> None:
        self.release()


def acquire(path: Path, *, stale_after: float = STALE_AFTER) -> tuple[Lock | None, str]:
    """Попробовать взять замок. Возвращает (замок или None, объяснение)."""
    info = read_lock(path)
    state = judge_lock(
        info,
        now=time.time(),
        pid_alive=pid_alive(info.pid) if info else False,
        stale_after=stale_after,
    )
    reason = describe(state, info)
    if not state.can_take:
        return None, reason

    lock = Lock(path=path, state=state, previous=info)
    lock._write()
    return lock, reason
