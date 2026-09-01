"""Надзор за долгим потомком: когда считать его зависшим и когда снимать.

Здесь только политика — арифметика над отметками времени. Ни одного вызова
подсистемы процессов: запуск и снятие живут в обёртке, а сюда передаются
факты «когда начали», «когда последний раз что-то сказал», «завершился ли».
Поэтому всё проверяется без единого настоящего процесса, за миллисекунды.

**Зависание опознаётся по молчанию, а не по длительности.** Это оплачено
двумя сутками простоя: 27–29.08.2026 процессы yt-dlp висели по 9 часов
с нулевым временем ЦП и нулём сетевых соединений, а предел времени внутри
самого yt-dlp их не брал. При этом здоровая загрузка ролика на 4,7 ГБ идёт
два часа сорок девять минут — предел по общей длительности убил бы её ни за что.
Различает эти два случая только тишина: живой процесс всё время что-то говорит.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    """Что надзорщик думает о потомке прямо сейчас."""

    RUNNING = "работает"
    OK = "завершился успешно"
    FAILED = "завершился с ошибкой"
    STALLED = "завис — молчит дольше допустимого"
    TIMED_OUT = "превысил общий предел времени"
    #: Работу прекратили снаружи — например, человек закрыл окно, не дождавшись
    #: переписи. Не беда и не успех: спрашивать у такого ответа нечего.
    CANCELLED = "прекращён по просьбе"

    @property
    def is_final(self) -> bool:
        return self is not Verdict.RUNNING

    @property
    def needs_kill(self) -> bool:
        """Приговоры, после которых потомка надо снимать: сам он не уйдёт."""
        return self in (Verdict.STALLED, Verdict.TIMED_OUT)


@dataclass(frozen=True)
class WatchdogPolicy:
    """Пределы терпения.

    `silence_limit` — сколько секунд без единой строки вывода считаем зависанием.
    Ставится с запасом относительно самой долгой законной паузы: у yt-dlp это
    паузы между роликами (15–45 с) и повторы после отказа сети.

    `total_limit` — потолок на всю операцию, `None` значит без потолка.
    Нужен как последняя страховка, а не как основной механизм: длительность
    здоровой загрузки заранее неизвестна и зависит от размера ролика.
    """

    silence_limit: float
    total_limit: float | None = None
    kill_grace: float = 10.0

    def __post_init__(self) -> None:
        if self.silence_limit <= 0:
            raise ValueError("silence_limit должен быть положительным")
        if self.total_limit is not None and self.total_limit <= 0:
            raise ValueError("total_limit должен быть положительным или None")
        if self.kill_grace < 0:
            raise ValueError("kill_grace не может быть отрицательным")


@dataclass(frozen=True)
class ProcessState:
    """Снимок состояния потомка в момент проверки.

    Все отметки — в секундах монотонных часов. Настенное время не годится:
    перевод часов или синхронизация времени сдвинули бы пределы.
    """

    started_at: float
    last_output_at: float
    now: float
    exited: bool = False
    exit_code: int | None = None

    def __post_init__(self) -> None:
        if self.last_output_at < self.started_at:
            raise ValueError("последний вывод не может быть раньше запуска")
        if self.now < self.started_at:
            raise ValueError("«сейчас» не может быть раньше запуска")

    @property
    def silence(self) -> float:
        return self.now - self.last_output_at

    @property
    def elapsed(self) -> float:
        return self.now - self.started_at


def judge(state: ProcessState, policy: WatchdogPolicy) -> Verdict:
    """Вынести приговор потомку.

    Порядок проверок важен. Завершившийся процесс судим по коду возврата,
    даже если он перед этим долго молчал: результат уже получен, снимать нечего.

    Границы: приговор выносится при **строгом** превышении предела. Ровно на
    пределе процесс ещё жив — иначе на границе поведение зависело бы от того,
    успела ли проверка на миллисекунду раньше или позже.
    """
    if state.exited:
        return Verdict.OK if state.exit_code == 0 else Verdict.FAILED

    if policy.total_limit is not None and state.elapsed > policy.total_limit:
        return Verdict.TIMED_OUT

    if state.silence > policy.silence_limit:
        return Verdict.STALLED

    return Verdict.RUNNING


@dataclass(frozen=True)
class RetryPolicy:
    """Сколько раз и через сколько повторять после неудачи."""

    max_attempts: int = 3
    first_delay: float = 60.0
    factor: float = 2.0
    max_delay: float = 900.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts должен быть не меньше 1")
        if self.first_delay < 0:
            raise ValueError("first_delay не может быть отрицательным")
        if self.factor < 1:
            raise ValueError("factor меньше 1 означал бы сокращение пауз")


def next_delay(attempt: int, policy: RetryPolicy) -> float:
    """Пауза перед попыткой номер `attempt` (нумерация с 1).

    Растёт с каждым разом и упирается в потолок: если YouTube отказывает
    подряд, долбить его чаще — верный способ получить блокировку надолго.
    """
    if attempt < 1:
        raise ValueError("номер попытки начинается с 1")
    if attempt == 1:
        return 0.0
    delay = policy.first_delay * (policy.factor ** (attempt - 2))
    return min(delay, policy.max_delay)


def should_retry(attempt: int, verdict: Verdict, policy: RetryPolicy) -> bool:
    """Повторять ли после этого приговора.

    Успех не повторяем. Всё остальное — пока не кончились попытки: и отказ,
    и зависание, и превышение времени одинаково лечатся повтором, потому что
    причина у них чаще всего одна и та же — сеть.
    """
    if verdict is Verdict.OK:
        return False
    if verdict is Verdict.RUNNING:
        raise ValueError("нельзя решать о повторе, пока потомок работает")
    return attempt < policy.max_attempts
