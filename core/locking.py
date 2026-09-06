"""Замок единственного экземпляра: решение, можно ли забрать его себе.

Чистая логика. Проверка «жив ли процесс» и чтение файла — снаружи.

Зачем вообще: две копии выкачки пишут в один файл архива и в одни и те же
временные файлы. Но запрет параллельных копий, сделанный в лоб, однажды уже
вышел боком — зависший экземпляр держал замок девять часов, и планировщик
покорно пропускал каждый получасовой запуск. Простоя вышло на двое суток.

Отсюда правило: **замок протухает.** Экземпляр обязан регулярно отмечаться;
перестал — значит его можно забрать, даже если процесс формально ещё числится
живым. Мёртвый процесс отдаёт замок сразу, без ожидания.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LockState(Enum):
    FREE = "свободен"
    HELD = "занят живым экземпляром"
    STALE = "протух — прежний хозяин молчит"
    ORPHANED = "брошен — процесса больше нет"

    @property
    def can_take(self) -> bool:
        return self is not LockState.HELD


@dataclass(frozen=True)
class LockInfo:
    """Что записано в замке."""

    pid: int
    heartbeat: float


def judge_lock(
    info: LockInfo | None,
    *,
    now: float,
    pid_alive: bool,
    stale_after: float,
) -> LockState:
    """Можно ли забрать замок.

    `stale_after` обязан быть заметно больше предела молчания надзорщика:
    здоровый экземпляр отмечается регулярно, но если взять порог слишком
    тесным, мы начнём отбирать замок у работающей выкачки и запустим вторую.

    Мёртвый процесс отдаёт замок немедленно: ждать протухания незачем,
    хозяина уже нет.
    """
    if stale_after <= 0:
        raise ValueError("порог протухания должен быть положительным")

    if info is None:
        return LockState.FREE
    if not pid_alive:
        return LockState.ORPHANED
    if now - info.heartbeat > stale_after:
        return LockState.STALE
    return LockState.HELD


def describe(state: LockState, info: LockInfo | None, перевод=str) -> str:
    """Строка для журнала — такая, чтобы по ней было понятно, что делать.

    Переводчик доводом: ядру нельзя знать про язык интерфейса.
    """
    кто = info.pid if info else "?"
    if state is LockState.FREE:
        return перевод("замок свободен")
    if state is LockState.HELD:
        return перевод("уже работает экземпляр {} — второй не нужен").format(кто)
    if state is LockState.ORPHANED:
        return перевод("замок брошен процессом {} — забираю").format(кто)
    return перевод("замок протух: {} молчит слишком долго — забираю").format(кто)
