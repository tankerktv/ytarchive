"""Проверки разбора настроек.

Настройки правит человек руками, поэтому здесь много проверок на отказ.
Молча принятая опечатка — это неделя недоумения: «я же задал потолок 720,
почему качается 1080».
"""

import pytest

from core.config import DEFAULT_CONFIG_TEXT, ConfigError, loads, parse_config


def настройки(**разделы):
    основа = {"paths": {"base": "F:/архив"}}
    основа.update(разделы)
    return основа


def test_список_исключений_живёт_отдельно_от_архива():
    """Попади снятые галочки в архив, вернуть ролик было бы нечем:
    он числился бы скачанным.
    """
    config = parse_config(настройки())
    assert config.paths.excluded == "_tools/excluded.txt"
    assert config.paths.excluded != config.paths.archive


def test_минимальные_настройки():
    config = parse_config(настройки())
    assert config.paths.base == "F:/архив"
    assert config.height == 1080
    assert config.prefer_av1 is True


def test_образец_настроек_разбирается():
    # Образец, который мы даём человеку, обязан быть годным.
    config = parse_config(loads(DEFAULT_CONFIG_TEXT))
    assert config.paths.base
    assert config.limits.silence_limit > config.limits.sleep_max


def test_без_базового_пути_отказ():
    with pytest.raises(ConfigError, match="base"):
        parse_config({"paths": {}})


def test_опечатка_в_ключе_не_проходит_молча():
    """Принятая молча опечатка — неделя недоумения, почему настройка не действует."""
    with pytest.raises(ConfigError, match="heigth"):
        parse_config(настройки(download={"heigth": 720}))


def test_опечатка_в_разделе_не_проходит_молча():
    with pytest.raises(ConfigError, match="downloads"):
        parse_config({"paths": {"base": "x"}, "downloads": {}})


def test_отказ_на_неизвестном_разрешении():
    with pytest.raises(ConfigError, match="720"):
        parse_config(настройки(download={"height": 999}))


def test_паузы_наоборот_это_отказ():
    with pytest.raises(ConfigError, match="наоборот"):
        parse_config(настройки(limits={"sleep_min": 60, "sleep_max": 10}))


def test_предел_молчания_меньше_паузы_между_роликами_это_отказ():
    """Иначе надзорщик начнёт убивать здоровую выкачку прямо на паузе.

    Ровно эта ошибка сделала шаткими наши же тесты обёртки: предел терпения
    оказался меньше законной задержки.
    """
    with pytest.raises(ConfigError, match="не зависание"):
        parse_config(настройки(limits={"silence_limit": 30, "sleep_max": 45}))


def test_языки_субтитров_списком():
    with pytest.raises(ConfigError, match="список строк"):
        parse_config(настройки(download={"sub_langs": "ru"}))


def test_быстрый_проход_по_умолчанию_выключен():
    # На недособранном архиве он обрывает выкачку на первом же скачанном.
    assert parse_config(настройки()).break_on_existing is False


# --- запись настроек --------------------------------------------------------


def test_запись_и_чтение_обратимы():
    """Окно правит этот файл. Если запись теряет значение, человек задаст
    качество, а качаться будет прежнее — молча.
    """
    from core.config import dump_config

    исходный = parse_config(loads(DEFAULT_CONFIG_TEXT))
    повторный = parse_config(loads(dump_config(исходный)))

    assert повторный == исходный


def test_путь_с_обратными_слэшами_переживает_запись():
    r"""Пути на Windows полны обратных слэшей, а в TOML это знак экранирования.

    Без обработки путь вида C:\Users\... при следующем чтении стал бы мусором,
    причём файл остался бы формально годным — то есть беда была бы молчаливой.
    """
    from core.config import dump_config

    исходный = parse_config(настройки(paths={"base": r"C:\Users\Example\Архив"}))
    повторный = parse_config(loads(dump_config(исходный)))

    assert повторный.paths.base == r"C:\Users\Example\Архив"


def test_в_записанном_файле_остаются_объяснения():
    # Файл правит человек руками, и объяснения в нём ценнее аккуратности.
    from core.config import dump_config

    текст = dump_config(parse_config(настройки()))
    assert "AV1 при равном разрешении" in текст
    assert "оборвётся на первом же скачанном" in текст
