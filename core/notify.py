"""Уведомления: когда звать человека и что ему написать.

Обход работает без окна — в этом его смысл. Но позвать человека он мог
только через окно: значок в трее показывает всплывающее сообщение, а если
окно закрыто, беда остаётся в журнале, который никто не читает. За месяц
архив дважды молча простаивал.

Здесь решения: о чём говорить, какими словами и как собрать запрос к
Telegram. Сеть — в `runner/notify.py`.

**Ключ бота — тайна.** Он не лежит в настройках: в них лежит путь к файлу
с ключом. Настройки показывают на экране, копируют в переписку и кладут в
резервные копии; ключу там не место. И он никогда не попадает в журнал —
любой текст ошибки перед показом очищается.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

TELEGRAM_API = "https://api.telegram.org"

#: Вид ключа бота: номер, двоеточие, длинная строка. Проверка не для красоты:
#: файл с лишней строкой или с адресом вместо ключа дал бы невнятный отказ
#: сервера, а так причина называется сразу.
_КЛЮЧ = re.compile(r"^\d{5,}:[A-Za-z0-9_-]{30,}$")

#: Чем заменяется ключ в любом тексте, который увидит человек.
СКРЫТО = "<ключ скрыт>"


@dataclass(frozen=True)
class Notify:
    """Куда слать. Пусто — уведомления выключены."""

    #: Путь к файлу, в котором лежит ключ бота. Не сам ключ.
    telegram_token_file: str = ""
    #: Кому писать: номер беседы или @имя канала.
    telegram_chat: str = ""

    @property
    def enabled(self) -> bool:
        return bool(self.telegram_token_file and self.telegram_chat)


def read_token(text: str) -> str:
    """Ключ из содержимого файла. Пустая строка — в файле не ключ.

    Берётся первая непустая строка: редакторы дописывают перевод строки,
    а человек — пояснение ниже.
    """
    for строка in text.splitlines():
        очищенная = строка.strip()
        if очищенная:
            return очищенная if _КЛЮЧ.match(очищенная) else ""
    return ""


def scrub(text: str, token: str) -> str:
    """Убрать ключ из текста. Ключ стоит прямо в адресе запроса, и библиотека
    охотно печатает адрес в сообщении об ошибке."""
    return text.replace(token, СКРЫТО) if token else text


def telegram_request(token: str, chat: str, text: str) -> tuple[str, dict[str, str]]:
    """Адрес и поля запроса на отправку сообщения."""
    return (
        f"{TELEGRAM_API}/bot{token}/sendMessage",
        {"chat_id": chat, "text": text, "disable_web_page_preview": "true"},
    )


def parse_reply(body: str) -> tuple[bool, str]:
    """Разобрать ответ Telegram: (получилось, объяснение сервера)."""
    try:
        ответ = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return False, "ответ не разобрался"
    if not isinstance(ответ, dict):
        return False, "ответ не разобрался"
    if ответ.get("ok") is True:
        return True, ""
    return False, str(ответ.get("description") or "отказ без объяснения")


class Change:
    """Что изменилось с прошлого прохода."""

    NOTHING = "nothing"
    TROUBLE = "trouble"
    RECOVERED = "recovered"


def judge_change(told: str, current: str) -> str:
    """О чём сказать человеку после прохода.

    `told` — причина, о которой уже сказано; `current` — нынешняя.

    Говорим о новой беде и о том, что беда прошла. О той же беде второй раз
    не говорим: обход проверяет раз в час, и сообщение каждый час приучает
    выключить уведомления совсем.
    """
    if current and current != told:
        return Change.TROUBLE
    if told and not current:
        return Change.RECOVERED
    return Change.NOTHING
