"""Живое состояние выкачки: что происходит прямо сейчас.

Отдельно от журнала намеренно. В журнал проценты не пишутся — на архиве
в две тысячи роликов это сотни тысяч строк, среди которых уже ничего
не найдёшь. А окну проценты нужны каждую секунду.

Поэтому живое состояние — маленький файл, который переписывается целиком:
кто читает, тот всегда видит целую картину, а не половину предыдущей
и половину новой.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace

from core.progress import Event, EventKind

#: Как часто переписывать файл. Чаще незачем: глаз всё равно не различит,
#: а запись на каждую строку прогресса — это тысячи обращений к диску
#: на один ролик.
WRITE_INTERVAL = 1.0


@dataclass(frozen=True)
class LiveState:
    """Снимок происходящего. Всё необязательное: в начале прохода
    большая часть ещё неизвестна, и это законно."""

    channel: str = ""
    channel_index: int = 0
    channel_total: int = 0
    item_index: int = 0
    item_total: int = 0
    file_name: str = ""
    percent: float = 0.0
    size_bytes: int = 0
    speed_bps: float = 0.0
    eta: str = ""
    updated_at: float = 0.0
    #: Отказов за проход. Раньше окно считало их, разбирая журнал, — а журнал
    #: теперь переводится, и считать в нём стало нечего.
    errors: int = 0
    #: Пауза между роликами. Не то же самое, что простой: выкачка жива.
    sleeping: bool = False
    #: Почему остановились, если остановились. Пустая строка — работаем.
    #: Хранится по-русски: это ключ перевода, а не готовая надпись.
    stopped_reason: str = ""

    @property
    def has_file(self) -> bool:
        return bool(self.file_name)

    def item_fraction(self) -> float:
        """Доля пройденного по каналу, от 0 до 1."""
        if self.item_total <= 0:
            return 0.0
        # Текущий ролик считается наполовину сделанным по своему проценту:
        # иначе полоса дёргалась бы скачками на длинных роликах.
        сделано = max(0, self.item_index - 1) + self.percent / 100.0
        return min(1.0, сделано / self.item_total)


def apply_event(state: LiveState, event: Event, *, now: float) -> LiveState:
    """Сложить событие в состояние.

    Неизвестные события состояние не портят — просто не меняют его.
    """
    if event.kind is EventKind.DESTINATION:
        return replace(
            state,
            file_name=_basename(event.path),
            percent=0.0,
            speed_bps=0.0,
            eta="",
            sleeping=False,
            updated_at=now,
        )
    if event.kind is EventKind.ERROR:
        return replace(state, errors=state.errors + 1, updated_at=now)
    if event.kind is EventKind.SLEEPING:
        return replace(state, sleeping=True, updated_at=now)
    if event.kind is EventKind.PROGRESS:
        return replace(
            state,
            percent=event.percent or 0.0,
            size_bytes=event.size_bytes or state.size_bytes,
            speed_bps=event.speed_bps or 0.0,
            eta=event.eta,
            updated_at=now,
        )
    if event.kind is EventKind.COMPLETED:
        return replace(
            state,
            percent=100.0,
            size_bytes=event.size_bytes or state.size_bytes,
            speed_bps=event.speed_bps or state.speed_bps,
            eta="",
            updated_at=now,
        )
    if event.kind is EventKind.ITEM:
        return replace(
            state,
            item_index=event.index or 0,
            item_total=event.total or 0,
            updated_at=now,
        )
    return state


def stop_channel(state: LiveState, reason: str, *, now: float) -> LiveState:
    """Остановились и нужен человек. Причина хранится по-русски: она ключ
    перевода, а не готовая надпись — язык окна и язык выкачки могут
    отличаться, если их запускали порознь."""
    return replace(state, stopped_reason=reason, file_name="", updated_at=now)


def start_channel(state: LiveState, name: str, index: int, total: int, *, now: float) -> LiveState:
    """Перешли к следующему каналу — счётчики роликов начинаются заново."""
    return replace(
        state,
        channel=name,
        channel_index=index,
        channel_total=total,
        item_index=0,
        item_total=0,
        file_name="",
        percent=0.0,
        speed_bps=0.0,
        eta="",
        updated_at=now,
    )


def should_write(last_write: float, now: float, interval: float = WRITE_INTERVAL) -> bool:
    """Пора ли переписывать файл."""
    if interval <= 0:
        raise ValueError("промежуток записи должен быть положительным")
    return now - last_write >= interval


def to_text(state: LiveState) -> str:
    return json.dumps(asdict(state), ensure_ascii=False, indent=1)


def from_text(text: str) -> LiveState | None:
    """Прочитать состояние.

    Испорченный или недописанный файл — это отсутствие состояния, а не отказ:
    окно должно пережить попадание на середину записи, а не падать.
    """
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    # Типы проверяем сами: датакласс их не сторожит, и строка вместо числа
    # прошла бы насквозь. Окно потом посчитало бы по ней арифметику и упало —
    # а оно окно наблюдения, падать ему нельзя.
    известные: dict[str, object] = {}
    for имя, поле in LiveState.__dataclass_fields__.items():
        if имя not in data:
            continue
        значение = data[имя]

        ожидается = str(поле.type)

        # `bool` в Python — подвид `int`, и без разбора `true` молча стал бы
        # единицей. Поэтому булево принимается только там, где объявлено.
        if ожидается == "bool":
            if not isinstance(значение, bool):
                return None
        elif isinstance(значение, bool):
            return None
        elif ожидается == "str":
            if not isinstance(значение, str):
                return None
        elif ожидается == "int":
            if not isinstance(значение, int):
                return None
        elif ожидается == "float":
            if not isinstance(значение, (int, float)):
                return None
            значение = float(значение)

        известные[имя] = значение

    try:
        return LiveState(**известные)
    except TypeError:
        return None


def _basename(path: str) -> str:
    for sep in ("\\", "/"):
        if sep in path:
            path = path.rsplit(sep, 1)[1]
    return path
