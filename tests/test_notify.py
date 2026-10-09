"""Уведомления в Telegram.

Обход работает без окна, а позвать человека мог только через окно. За месяц
архив дважды молча простаивал: беда лежала в журнале, который никто не читал.

Сторожатся две вещи. Первая — когда писать: о новой беде и о её конце, но не
каждый час об одном и том же. Вторая — ключ бота: он не должен оказаться ни
в настройках, ни в журнале, ни в тексте ошибки.

Настоящая сеть сюда не заходит: отправка подменяется.
"""

import io
import json
import urllib.error

import pytest

from app import main as app_main
from core.config import ConfigError, dump_config, loads, parse_config
from core.flow import ChannelResult, SessionSummary
from core.notify import (
    СКРЫТО,
    Change,
    Notify,
    judge_change,
    parse_reply,
    read_token,
    scrub,
    telegram_request,
)
from runner import notify as отправка

КЛЮЧ = "1234567890:AAExampleExampleExampleExampleExample"


# --- когда писать ------------------------------------------------------------


def test_о_новой_беде_пишем():
    assert judge_change("", "истекли куки") == Change.TROUBLE


def test_о_той_же_беде_второй_раз_молчим():
    """Обход проверяет раз в час. Сообщение каждый час приучает выключить
    уведомления совсем."""
    assert judge_change("истекли куки", "истекли куки") == Change.NOTHING


def test_о_другой_беде_пишем_снова():
    assert judge_change("истекли куки", "не найден node") == Change.TROUBLE


def test_о_том_что_беда_прошла_пишем():
    """Иначе человек, починив куки, не узнает, помогло ли."""
    assert judge_change("истекли куки", "") == Change.RECOVERED


def test_когда_всё_хорошо_молчим():
    assert judge_change("", "") == Change.NOTHING


# --- ключ бота ---------------------------------------------------------------


def test_ключ_берётся_первой_непустой_строкой():
    """Редакторы дописывают перевод строки, а человек — пояснение ниже."""
    assert read_token(f"\n  {КЛЮЧ}  \nэто ключ бота архива\n") == КЛЮЧ


@pytest.mark.parametrize("текст", ["", "   \n", "не ключ", "https://t.me/mybot", "12:коротко"])
def test_не_ключ_ключом_не_считается(текст):
    """Файл с адресом вместо ключа дал бы невнятный отказ сервера."""
    assert read_token(текст) == ""


def test_ключ_вычищается_из_любого_текста():
    """Ключ стоит прямо в адресе запроса, и библиотека охотно печатает адрес
    в сообщении об ошибке."""
    текст = f"HTTP Error 404: https://api.telegram.org/bot{КЛЮЧ}/sendMessage"
    assert КЛЮЧ not in scrub(текст, КЛЮЧ) and СКРЫТО in scrub(текст, КЛЮЧ)
    assert scrub("обычный текст", "") == "обычный текст"


def test_запрос_собирается():
    адрес, поля = telegram_request(КЛЮЧ, "-100123", "привет")
    assert адрес == f"https://api.telegram.org/bot{КЛЮЧ}/sendMessage"
    assert поля["chat_id"] == "-100123" and поля["text"] == "привет"


def test_ответ_сервера_разбирается():
    assert parse_reply('{"ok": true, "result": {}}') == (True, "")
    assert parse_reply('{"ok": false, "description": "Bad Request: chat not found"}') == (
        False, "Bad Request: chat not found",
    )
    assert parse_reply("<html>шлюз</html>")[0] is False


# --- настройки ---------------------------------------------------------------


def test_по_умолчанию_уведомления_выключены():
    assert not parse_config({"paths": {"base": "/a"}}).notify.enabled


def test_настройки_уведомлений_переживают_запись():
    config = parse_config({
        "paths": {"base": "/a"},
        "notify": {"telegram_token_file": r"C:\Users\Example\bot.key", "telegram_chat": "-100123"},
    })
    assert config.notify.enabled
    assert parse_config(loads(dump_config(config))) == config


def test_в_настройках_лежит_путь_а_не_ключ():
    """Настройки показывают на экране, копируют в переписку и кладут в
    резервные копии. Поля для самого ключа в них нет вовсе."""
    with pytest.raises(ConfigError):
        parse_config({"paths": {"base": "/a"}, "notify": {"telegram_token": КЛЮЧ, "telegram_chat": "1"}})


def test_половина_настройки_это_отказ():
    """Половина настройки — выключенные уведомления, о которых человек думает,
    что они включены. Узнает он об этом, когда архив простоит неделю."""
    with pytest.raises(ConfigError):
        parse_config({"paths": {"base": "/a"}, "notify": {"telegram_chat": "-100123"}})


# --- отправка ----------------------------------------------------------------


class Ответ:
    def __init__(self, тело: str) -> None:
        self.тело = тело.encode("utf-8")

    def read(self) -> bytes:
        return self.тело

    def __enter__(self):
        return self

    def __exit__(self, *доводы) -> None:
        return None


@pytest.fixture
def куда(tmp_path) -> Notify:
    файл = tmp_path / "bot.key"
    файл.write_text(КЛЮЧ + "\n", encoding="utf-8")
    return Notify(telegram_token_file=str(файл), telegram_chat="-100123")


def test_сообщение_уходит(куда):
    запросы = []

    def открыть(запрос, timeout):
        запросы.append((запрос.full_url, запрос.data.decode("utf-8")))
        return Ответ('{"ok": true}')

    assert отправка.send(куда, "выкачка остановлена", opener=открыть) == (True, "")
    assert запросы[0][0].endswith("/sendMessage") and "chat_id=-100123" in запросы[0][1]


def test_отказ_сервера_объяснён_и_ключа_в_нём_нет(куда):
    def открыть(запрос, timeout):
        raise urllib.error.HTTPError(
            запрос.full_url, 400, "Bad Request", {}, io.BytesIO(b'{"ok": false, "description": "Bad Request: chat not found"}')
        )

    получилось, объяснение = отправка.send(куда, "текст", opener=открыть)
    assert not получилось and объяснение == "Bad Request: chat not found"


def test_сетевая_ошибка_не_показывает_ключ(куда):
    """Библиотека кладёт адрес запроса — а в нём ключ — прямо в текст ошибки."""
    def открыть(запрос, timeout):
        raise urllib.error.URLError(f"не достучался до {запрос.full_url}")

    получилось, объяснение = отправка.send(куда, "текст", opener=открыть)
    assert not получилось
    assert КЛЮЧ not in объяснение and СКРЫТО in объяснение


def test_нет_файла_с_ключом_это_объяснение_а_не_падение(tmp_path):
    куда = Notify(telegram_token_file=str(tmp_path / "нет.key"), telegram_chat="1")
    получилось, объяснение = отправка.send(куда, "текст", opener=lambda *а, **к: pytest.fail("в сеть не ходим"))
    assert not получилось and объяснение


def test_не_ключ_в_файле_в_сеть_не_уходит(tmp_path):
    файл = tmp_path / "bot.key"
    файл.write_text("https://t.me/mybot\n", encoding="utf-8")
    куда = Notify(telegram_token_file=str(файл), telegram_chat="1")
    получилось, _объяснение = отправка.send(куда, "текст", opener=lambda *а, **к: pytest.fail("в сеть не ходим"))
    assert not получилось


# --- обход -------------------------------------------------------------------


def _config(tmp_path):
    файл = tmp_path / "bot.key"
    файл.write_text(КЛЮЧ, encoding="utf-8")
    return parse_config({
        "paths": {"base": str(tmp_path)},
        "notify": {"telegram_token_file": str(файл), "telegram_chat": "1"},
    })


def беда(причина: str) -> SessionSummary:
    return SessionSummary(results=(ChannelResult(channel="К", stopped_reason=причина),))


ХОРОШО = SessionSummary(results=(ChannelResult(channel="К", downloaded=1),))


def test_обход_пишет_о_беде_один_раз_и_о_её_конце(tmp_path, monkeypatch):
    отправлено = []
    monkeypatch.setattr(отправка, "send", lambda куда, текст: (отправлено.append(текст), (True, ""))[1])
    config = _config(tmp_path)
    журнал = []

    сказано = app_main.уведомить(config, беда("сетевой сбой"), "", журнал.append)
    сказано = app_main.уведомить(config, беда("сетевой сбой"), сказано, журнал.append)
    сказано = app_main.уведомить(config, беда("сетевой сбой"), сказано, журнал.append)
    assert len(отправлено) == 1 and "сетевой сбой" in отправлено[0]

    сказано = app_main.уведомить(config, ХОРОШО, сказано, журнал.append)
    assert len(отправлено) == 2 and "снова работает" in отправлено[1]
    assert сказано == ""

    app_main.уведомить(config, ХОРОШО, сказано, журнал.append)
    assert len(отправлено) == 2, "о том, что всё хорошо, каждый проход не пишем"


def test_неотправленное_сообщение_пробуют_снова(tmp_path, monkeypatch):
    """Не ушло сейчас — попробуем после следующего прохода, а не промолчим
    навсегда: сеть могла лежать как раз потому, что лежит всё."""
    ответы = [(False, "сеть недоступна"), (True, "")]
    monkeypatch.setattr(отправка, "send", lambda куда, текст: ответы.pop(0))
    config = _config(tmp_path)
    журнал = []

    сказано = app_main.уведомить(config, беда("истекли куки"), "", журнал.append)
    assert сказано == "", "не сказано — значит, не сказано"
    assert any("не ушло" in строка and "сеть недоступна" in строка for строка in журнал)

    сказано = app_main.уведомить(config, беда("истекли куки"), сказано, журнал.append)
    assert сказано == "истекли куки" and not ответы
