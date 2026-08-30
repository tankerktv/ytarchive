"""Проверки решений хода работы.

Главное свойство: **безнадёжная беда не пережидается.** Три попытки с паузами
по минуте против отсутствующего входа в аккаунт — это три минуты, потраченные
впустую, и человек всё это время не знает, что от него что-то нужно.
"""

import pytest

from core.flow import Action, ChannelResult, SessionSummary, decide_after_probe
from core.probe import Diagnosis
from core.supervisor import RetryPolicy

ПОЛИТИКА = RetryPolicy(max_attempts=3, first_delay=60.0, factor=2.0)


def test_доступ_есть_качаем():
    решение = decide_after_probe(Diagnosis.OK, 1, ПОЛИТИКА)
    assert решение.action is Action.PROCEED
    assert not решение.needs_human


def test_сетевое_пережидаем():
    решение = decide_after_probe(Diagnosis.NETWORK, 1, ПОЛИТИКА)
    assert решение.action is Action.RETRY
    assert решение.delay == 60.0


def test_паузы_между_повторами_растут():
    первая = decide_after_probe(Diagnosis.NETWORK, 1, ПОЛИТИКА)
    вторая = decide_after_probe(Diagnosis.NETWORK, 2, ПОЛИТИКА)
    assert вторая.delay > первая.delay


def test_сетевое_не_пережидаем_бесконечно():
    решение = decide_after_probe(Diagnosis.NETWORK, 3, ПОЛИТИКА)
    assert решение.action is Action.STOP
    assert "3 попыток" in решение.reason


@pytest.mark.parametrize(
    "диагноз,примета",
    [
        (Diagnosis.LOGIN_REQUIRED, "вход в аккаунт"),
        (Diagnosis.NO_JS_RUNTIME, "node"),
        (Diagnosis.EMPTY_LISTING, "устарел"),
    ],
)
def test_безнадёжное_не_пережидаем_вовсе(диагноз, примета):
    """Ни одной попытки: это чинит человек, и сказать ему надо сразу."""
    решение = decide_after_probe(диагноз, 1, ПОЛИТИКА)

    assert решение.action is Action.STOP
    assert решение.needs_human
    assert примета in решение.reason


def test_неопознанное_осторожно_повторяем():
    # Не знаем, что это — значит не знаем и что оно безнадёжно.
    решение = decide_after_probe(Diagnosis.UNKNOWN, 1, ПОЛИТИКА)
    assert решение.action is Action.RETRY


def test_ложная_проверка_прав_пережидается():
    # 29.08 она была следствием провала DNS и прошла сама.
    assert decide_after_probe(Diagnosis.TAB_AUTHCHECK, 1, ПОЛИТИКА).action is Action.RETRY


def test_отказ_на_нулевой_попытке():
    with pytest.raises(ValueError):
        decide_after_probe(Diagnosis.OK, 0, ПОЛИТИКА)


# --- итог сеанса ------------------------------------------------------------


def test_итог_складывает_каналы():
    итог = SessionSummary(
        results=(
            ChannelResult("SoyuzUS", downloaded=10, failed=2),
            ChannelResult("MurkPOWER", downloaded=5),
        )
    )
    assert итог.downloaded == 15
    assert итог.failed == 2
    assert not итог.needs_human


def test_остановленный_канал_требует_человека():
    итог = SessionSummary(
        results=(
            ChannelResult("SoyuzUS", downloaded=3),
            ChannelResult("MurkPOWER", stopped_reason="нужен вход в аккаунт"),
        )
    )
    assert итог.needs_human
    assert len(итог.stopped) == 1


def test_упавшие_ролики_и_остановленные_каналы_называются_врозь():
    """Упавший ролик — обычное дело, заберётся следующим проходом.
    Остановленный канал требует человека. Слить их в одно число значит
    спрятать беду за обыденностью.
    """
    итог = SessionSummary(
        results=(
            ChannelResult("SoyuzUS", downloaded=10, failed=57),
            ChannelResult("MurkPOWER", stopped_reason="куки истекли"),
        )
    )
    строка = итог.describe()

    assert "скачано 10" in строка
    assert "упало 57" in строка
    assert "следующим проходом" in строка
    assert "куки истекли" in строка


def test_настоящий_случай_2026_08_27_упавшие_не_повод_звать_человека():
    """За неделю сбоило 964 ролика, и все до одного забрались повторами.
    Звать человека на такое — приучать не верить предупреждениям.
    """
    итог = SessionSummary(results=(ChannelResult("SoyuzUS", downloaded=206, failed=964),))

    assert not итог.needs_human
    assert "следующим проходом" in итог.describe()
