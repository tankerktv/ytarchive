"""Решения хода работы: что делать после проверки доступа и как считать итог.

Чистая логика, отделённая от цикла намеренно. Главное, что здесь закреплено:
**повторять имеет смысл не всякую беду.**

За неделю выкачки это стоило времени дважды. Сетевые сбои проходят сами —
блокировка DNS отпускала через минуты, и 964 упавших ролика забрались
повторами без единого вмешательства. А вот отсутствие входа в аккаунт или
движка JavaScript само не починится никогда: три попытки с паузами по минуте
просто съедят три минуты и упрутся в тот же отказ. Такое надо не пережидать,
а показывать человеку сразу.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.probe import Diagnosis
from core.supervisor import RetryPolicy, next_delay


class Action(Enum):
    PROCEED = "качать"
    RETRY = "повторить проверку"
    STOP = "остановиться и позвать человека"


@dataclass(frozen=True)
class Decision:
    action: Action
    delay: float = 0.0
    reason: str = ""

    @property
    def needs_human(self) -> bool:
        return self.action is Action.STOP


#: Беды, которые не проходят от ожидания. Повторять их бессмысленно:
#: чинить должен человек, и сказать ему надо сразу.
HOPELESS = {
    Diagnosis.LOGIN_REQUIRED: "нужен вход в аккаунт YouTube — куки истекли или их нет",
    Diagnosis.NO_JS_RUNTIME: "не найден движок JavaScript — нужен node",
    Diagnosis.EMPTY_LISTING: "yt-dlp вернул пустой список при успешном коде — похоже, он устарел",
}


def decide_after_probe(
    diagnosis: Diagnosis, attempt: int, policy: RetryPolicy | None = None
) -> Decision:
    """Что делать после проверки доступа.

    `attempt` считается с 1. Возвращается либо «качать», либо «подождать
    столько-то и проверить снова», либо «остановиться» с внятной причиной —
    такой, чтобы её можно было показать человеку без перевода.
    """
    if attempt < 1:
        raise ValueError("номер попытки начинается с 1")
    policy = policy or RetryPolicy()

    if diagnosis is Diagnosis.OK:
        return Decision(action=Action.PROCEED)

    if diagnosis in HOPELESS:
        return Decision(action=Action.STOP, reason=HOPELESS[diagnosis])

    # Остальное — сетевое и неопознанное — пережидаем, но не бесконечно.
    if attempt >= policy.max_attempts:
        return Decision(
            action=Action.STOP,
            reason=f"{diagnosis.value}: не прошло за {policy.max_attempts} попыток",
        )

    return Decision(
        action=Action.RETRY,
        delay=next_delay(attempt + 1, policy),
        reason=diagnosis.value,
    )


@dataclass(frozen=True)
class ChannelResult:
    channel: str
    downloaded: int = 0
    failed: int = 0
    stopped_reason: str = ""

    @property
    def ok(self) -> bool:
        return not self.stopped_reason


@dataclass(frozen=True)
class SessionSummary:
    results: tuple[ChannelResult, ...] = ()

    @property
    def downloaded(self) -> int:
        return sum(r.downloaded for r in self.results)

    @property
    def failed(self) -> int:
        return sum(r.failed for r in self.results)

    @property
    def stopped(self) -> tuple[ChannelResult, ...]:
        return tuple(r for r in self.results if not r.ok)

    @property
    def needs_human(self) -> bool:
        return bool(self.stopped)

    def describe(self) -> str:
        """Одна строка для журнала и для интерфейса.

        Упавшие ролики называются отдельно от остановленных каналов: первое —
        обычное дело, забирается следующим проходом, второе требует человека.
        Слить их в одно число значит спрятать беду за обыденностью.
        """
        parts = [f"скачано {self.downloaded}"]
        if self.failed:
            parts.append(f"упало {self.failed} (заберутся следующим проходом)")
        if self.stopped:
            имена = ", ".join(f"{r.channel} — {r.stopped_reason}" for r in self.stopped)
            parts.append(f"остановлено: {имена}")
        return "; ".join(parts)
