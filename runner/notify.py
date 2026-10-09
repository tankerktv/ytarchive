"""Отправка уведомлений в Telegram.

Решения — в `core/notify.py`. Здесь только файл с ключом и сеть.

Отправка не имеет права уронить выкачку и не имеет права показать ключ:
любая ошибка возвращается текстом, уже очищенным от него.
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from core.notify import Notify, parse_reply, read_token, scrub, telegram_request
from runner.language import _

#: Сколько ждём Telegram. Уведомление — не то, ради чего стоит задерживать проход.
TIMEOUT = 20


def _прочитать_ключ(путь: Path) -> tuple[str, str]:
    """Ключ из файла и объяснение, если не вышло."""
    try:
        текст = путь.read_text(encoding="utf-8-sig")
    except OSError as ошибка:
        return "", _('файл с ключом бота не читается: {}').format(ошибка)
    ключ = read_token(текст)
    if not ключ:
        return "", _("в файле с ключом бота лежит не ключ: ждём строку вида 123456:ABC…")
    return ключ, ""


def send(notify: Notify, text: str, *, opener=urllib.request.urlopen) -> tuple[bool, str]:
    """Отправить сообщение. Возвращает (получилось, объяснение).

    `opener` подменяется в проверках: настоящая отправка требовала бы
    настоящего бота.
    """
    if not notify.enabled:
        return False, _("уведомления не настроены")
    ключ, беда = _прочитать_ключ(Path(notify.telegram_token_file))
    if not ключ:
        return False, беда

    адрес, поля = telegram_request(ключ, notify.telegram_chat, text)
    запрос = urllib.request.Request(
        адрес, data=urllib.parse.urlencode(поля).encode("utf-8"), method="POST"
    )
    try:
        with opener(запрос, timeout=TIMEOUT) as ответ:
            тело = ответ.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as ошибка:
        # Отказ сервера приходит ошибкой, но с телом: в нём и лежит причина
        # («chat not found», «bot was blocked by the user»).
        try:
            тело = ошибка.read().decode("utf-8", "replace")
        except OSError:
            тело = ""
        получилось, объяснение = parse_reply(тело)
        return False, scrub(объяснение or str(ошибка), ключ)
    except (urllib.error.URLError, OSError, ValueError) as ошибка:
        return False, scrub(str(ошибка), ключ)

    получилось, объяснение = parse_reply(тело)
    return получилось, scrub(объяснение, ключ)
