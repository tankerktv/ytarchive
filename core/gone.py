"""Ролики, которых больше нет на YouTube.

Ради этого архив и существует: ролик удалили, канал закрыли — а у нас он есть.
Но узнать об этом было неоткуда: программа скачивала и больше к ролику
не возвращалась.

Узнаём попутно. Каждый проход и так переписывает канал — остаётся сравнить
перепись с тем, что лежит на диске. Ролик на диске, которого нет в переписи,
с YouTube пропал: удалён, скрыт или закрыт.

**Перепись может врать.** Сетевой сбой обрывает её посередине, и тогда
«пропавшими» оказались бы сотни роликов разом. Поэтому приговор выносится
только по правдоподобной переписи; иначе прежние отметки остаются как были.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

#: Какая доля архива канала может пропасть разом, чтобы мы в это поверили.
#: Канал, с которого исчезла половина, — либо закрыт (и тогда перепись пуста,
#: это другой случай), либо перепись оборвалась, либо адрес стал вести не туда.
MAX_SHARE = 0.5


@dataclass(frozen=True)
class Verdict:
    gone: frozenset[str] = frozenset()
    #: Можно ли верить. False — отметки не трогать.
    reliable: bool = False


def judge(on_disk: frozenset[str], listed: frozenset[str]) -> Verdict:
    """Каких роликов с диска нет в переписи канала.

    Пустая перепись ненадёжна всегда: так выглядит и сбой сети, и истёкший
    вход, и закрытый канал. Различить их по одной пустоте нельзя, а объявить
    весь архив канала пропавшим из-за обрыва связи — худшая из ошибок.
    """
    if not listed or not on_disk:
        return Verdict()
    пропало = on_disk - listed
    if len(пропало) / len(on_disk) > MAX_SHARE:
        return Verdict()
    return Verdict(gone=frozenset(пропало), reliable=True)


def from_text(text: str) -> dict[str, frozenset[str]]:
    """Прочитать отметки: канал → пропавшие ролики.

    Испорченный файл — это отсутствие отметок, а не отказ: они восстановятся
    сами за один проход, и ронять из-за них выкачку незачем.
    """
    try:
        данные = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(данные, dict):
        return {}
    итог = {}
    for канал, ролики in данные.items():
        if isinstance(канал, str) and isinstance(ролики, list):
            итог[канал] = frozenset(р for р in ролики if isinstance(р, str))
    return итог


def to_text(marks: dict[str, frozenset[str]]) -> str:
    """Записать отметки. Порядок устойчивый: файл можно сравнивать глазами."""
    return json.dumps(
        {канал: sorted(ролики) for канал, ролики in sorted(marks.items())},
        ensure_ascii=False,
        indent=1,
    ) + "\n"


def update(
    marks: dict[str, frozenset[str]], channel: str, verdict: Verdict
) -> tuple[dict[str, frozenset[str]], frozenset[str]]:
    """Учесть приговор по каналу. Возвращает новые отметки и то, что пропало
    впервые — об этом стоит сказать человеку.

    Ненадёжный приговор отметок не меняет. Надёжный заменяет их целиком:
    ролик, вернувшийся на YouTube, из пропавших уходит.
    """
    if not verdict.reliable:
        return marks, frozenset()
    прежние = marks.get(channel, frozenset())
    итог = dict(marks)
    итог[channel] = verdict.gone
    return итог, verdict.gone - прежние


def all_gone(marks: dict[str, frozenset[str]]) -> frozenset[str]:
    return frozenset().union(*marks.values()) if marks else frozenset()
