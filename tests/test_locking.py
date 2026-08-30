"""Проверки замка единственного экземпляра.

Цена ошибки здесь несимметрична в обе стороны, и потому проверок много.
Отдали замок зря — запустится вторая выкачка, и две копии полезут писать
в один файл архива. Не отдали вовремя — повторится простой на двое суток,
когда зависший экземпляр держал замок девять часов подряд.
"""

import pytest

from core.locking import LockInfo, LockState, describe, judge_lock

ПОРОГ = 600.0  # заметно больше предела молчания надзорщика (180 с)


def test_пустой_замок_свободен():
    состояние = judge_lock(None, now=1000.0, pid_alive=False, stale_after=ПОРОГ)
    assert состояние is LockState.FREE
    assert состояние.can_take


def test_живой_и_отмечавшийся_держит_замок():
    замок = LockInfo(pid=1234, heartbeat=1000.0)
    состояние = judge_lock(замок, now=1100.0, pid_alive=True, stale_after=ПОРОГ)
    assert состояние is LockState.HELD
    assert not состояние.can_take


def test_мёртвый_процесс_отдаёт_замок_сразу():
    """Ждать протухания незачем — хозяина уже нет."""
    замок = LockInfo(pid=1234, heartbeat=1000.0)
    состояние = judge_lock(замок, now=1001.0, pid_alive=False, stale_after=ПОРОГ)

    assert состояние is LockState.ORPHANED
    assert состояние.can_take


def test_живой_но_молчащий_отдаёт_замок_по_протуханию():
    """Тот самый случай: процесс формально жив, но не отмечается.

    27–29.08 зависший экземпляр числился живым девять часов и держал замок,
    пока планировщик покорно пропускал каждый получасовой запуск.
    """
    замок = LockInfo(pid=1234, heartbeat=1000.0)
    состояние = judge_lock(замок, now=1000.0 + ПОРОГ + 1, pid_alive=True, stale_after=ПОРОГ)

    assert состояние is LockState.STALE
    assert состояние.can_take


def test_ровно_на_пороге_замок_ещё_держится():
    # Строгое превышение: иначе на границе исход зависел бы от миллисекунд.
    замок = LockInfo(pid=1234, heartbeat=1000.0)
    состояние = judge_lock(замок, now=1000.0 + ПОРОГ, pid_alive=True, stale_after=ПОРОГ)
    assert состояние is LockState.HELD


def test_отказ_на_неположительном_пороге():
    with pytest.raises(ValueError):
        judge_lock(None, now=0.0, pid_alive=False, stale_after=0)


def test_порог_протухания_больше_предела_молчания():
    """Порог обязан быть с запасом относительно того, как долго здоровый
    экземпляр может молчать. Иначе отберём замок у работающей выкачки
    и запустим вторую в тот же архив.
    """
    предел_молчания_надзорщика = 180.0
    assert ПОРОГ > предел_молчания_надзорщика * 3


@pytest.mark.parametrize(
    "состояние,примета",
    [
        (LockState.FREE, "свободен"),
        (LockState.HELD, "уже работает"),
        (LockState.ORPHANED, "брошен"),
        (LockState.STALE, "протух"),
    ],
)
def test_описание_объясняет_что_происходит(состояние, примета):
    строка = describe(состояние, LockInfo(pid=42, heartbeat=0.0))
    assert примета in строка
