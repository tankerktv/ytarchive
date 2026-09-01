"""Проверка доступа к YouTube — разбор ответа yt-dlp.

**Проверяется то свойство, которое ломается.** Это оплачено сутками простоя:
первая версия проверки спрашивала «отдаёт ли YouTube хоть что-нибудь» и
пробовала посторонний популярный ролик. Тот отдавался, проверка печатала
«пройдено» и пускала задание в ночь — а ролики нужных каналов при этом
требовали входа в аккаунт. Проверять надо ролик ИЗ СПИСКА КАНАЛОВ.

Второй урок здесь же: **код возврата 0 не означает успех.** yt-dlp версии
2023 года на современном YouTube завершался успешно и печатал пустой список.
Пустая выдача при нулевом коде — отдельный диагноз, а не «канал без роликов».
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Diagnosis(Enum):
    """Что именно не так с доступом."""

    OK = "доступ есть, форматы отдаются"
    LOGIN_REQUIRED = "нужен вход в аккаунт YouTube"
    NO_JS_RUNTIME = "нет движка JavaScript"
    CHALLENGE_FAILED = "не решается задача YouTube — нужен решатель EJS"
    NETWORK = "сетевой сбой"
    TAB_AUTHCHECK = "yt-dlp сомневается в правах на вкладку канала"
    EMPTY_LISTING = "пустая выдача при успешном коде возврата"
    UNKNOWN = "неопознанный отказ"

    @property
    def is_ok(self) -> bool:
        return self is Diagnosis.OK

    @property
    def is_global(self) -> bool:
        """Беда общая для всех каналов, а не этого одного.

        Сеть либо есть, либо нет: убедившись на первом канале, перебирать
        остальные бессмысленно. 30.08 это стоило шести минут и четырёх
        одинаковых записей «остановлено» вместо одной внятной.

        Отсутствие входа и устаревший yt-dlp — тоже общие: они про нашу
        сторону, а не про конкретный канал.
        """
        return self in (
            Diagnosis.NETWORK,
            Diagnosis.LOGIN_REQUIRED,
            Diagnosis.NO_JS_RUNTIME,
            Diagnosis.EMPTY_LISTING,
        )

    @property
    def is_transient(self) -> bool:
        """Пройдёт ли само со временем.

        Сетевые сбои проходят — блокировка DNS у нас отпускала через минуты.
        Отсутствие входа или движка само не починится, ждать бессмысленно.
        """
        return self in (
            Diagnosis.NETWORK,
            Diagnosis.CHALLENGE_FAILED,
            Diagnosis.TAB_AUTHCHECK,
        )


#: Идентификатор ролика в выводе `--print %(id)s`.
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")

#: Приметы в выводе yt-dlp. Порядок важен: сначала то, что чинится точечно,
#: потом общее. Сетевой сбой проверяется раньше входа в аккаунт, потому что
#: при обрыве связи YouTube тоже отвечает «подтвердите, что вы не бот».
SIGNS: tuple[tuple[Diagnosis, tuple[str, ...]], ...] = (
    (
        Diagnosis.NETWORK,
        (
            "getaddrinfo failed",
            "temporary failure in name resolution",
            "connection refused",
            "timed out",
            "unable to download webpage",
            "handshake operation timed out",
            "forcibly closed by the remote host",
        ),
    ),
    (
        # Отдельный диагноз, а не сетевой сбой. Мы видели это сообщение только
        # как следствие обрыва связи (29.08, при провале DNS), но доказательства,
        # что так всегда, нет: оно же появится при настоящей нехватке прав.
        # Приписать ему причину значило бы гадать, поэтому просто «повторить».
        Diagnosis.TAB_AUTHCHECK,
        ("skip=authcheck", "playlists that require authentication"),
    ),
    (
        Diagnosis.NO_JS_RUNTIME,
        ("no supported javascript runtime",),
    ),
    (
        Diagnosis.CHALLENGE_FAILED,
        ("n challenge solving failed", "challenge solver script"),
    ),
    (
        Diagnosis.LOGIN_REQUIRED,
        ("sign in to confirm", "login_required", "not a bot"),
    ),
)


@dataclass(frozen=True)
class ProbeResult:
    diagnosis: Diagnosis
    video_ids: tuple[str, ...] = ()
    detail: str = ""

    @property
    def is_ok(self) -> bool:
        return self.diagnosis.is_ok


def diagnose(output: str, exit_code: int) -> ProbeResult:
    """Разобрать вывод пробного запуска yt-dlp.

    Приметы ищутся раньше, чем разбираются идентификаторы: частичная выдача
    вперемешку с отказом — это отказ, а не успех.
    """
    lowered = output.lower()

    for diagnosis, marks in SIGNS:
        for mark in marks:
            if mark in lowered:
                return ProbeResult(diagnosis=diagnosis, detail=_line_with(output, mark))

    ids = tuple(
        line.strip() for line in output.splitlines() if VIDEO_ID.match(line.strip())
    )

    if ids:
        return ProbeResult(diagnosis=Diagnosis.OK, video_ids=ids)

    # Пусто. Нулевой код тут ничего не гарантирует — ровно так вела себя
    # устаревшая версия yt-dlp: успех и ни одной строки.
    if exit_code == 0:
        return ProbeResult(
            diagnosis=Diagnosis.EMPTY_LISTING,
            detail="код возврата 0, но ни одного идентификатора — похоже на устаревший yt-dlp",
        )

    return ProbeResult(diagnosis=Diagnosis.UNKNOWN, detail=_first_error(output))


def _line_with(output: str, mark: str) -> str:
    for line in output.splitlines():
        if mark in line.lower():
            return line.strip()[:200]
    return ""


def _first_error(output: str) -> str:
    for line in output.splitlines():
        if line.strip().upper().startswith("ERROR"):
            return line.strip()[:200]
    return output.strip().splitlines()[-1][:200] if output.strip() else ""
