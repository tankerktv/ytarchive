"""Разбор настроек.

Чистый: на входе разобранный словарь, на выходе проверенные значения или
внятная жалоба. Чтение файла — в точке входа, здесь только смысл.

Правило то же, что везде: **ничего не принимается молча.** Неизвестный ключ
в настройках — это опечатка, из-за которой человек будет неделю думать,
что задал потолок разрешения, а качается по-прежнему 1080p.
"""

from __future__ import annotations

from dataclasses import dataclass

# tomllib появился в 3.11. На машине, где это писалось, настоящий
# интерпретатор только 3.10 — а привязываться к тому, чего нет,
# значит получить задание, падающее до первой строки Python.
try:
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover — ветка для 3.10
    import tomli as _toml


from core.ytdlp_args import ALLOWED_HEIGHTS

#: Ключи, которые мы понимаем. Всё остальное — повод пожаловаться.
KNOWN_SECTIONS = {"paths", "download", "limits"}
KNOWN_PATHS = {"base", "channels", "archive", "cookies", "logs", "excluded"}
KNOWN_DOWNLOAD = {"height", "prefer_av1", "write_subs", "sub_langs", "break_on_existing"}
KNOWN_LIMITS = {"silence_limit", "sleep_min", "sleep_max", "sleep_requests", "socket_timeout"}


@dataclass(frozen=True)
class Paths:
    base: str
    channels: str = "_tools/channels.txt"
    archive: str = "_tools/downloaded.txt"
    cookies: str = "_tools/cookies.txt"
    logs: str = "_logs"
    #: Ролики, снятые галочкой. Отдельно от `archive` намеренно: в архиве
    #: лежит скачанное, и попади исключения туда, вернуть ролик было бы уже
    #: нечем — он числился бы забранным.
    excluded: str = "_tools/excluded.txt"


@dataclass(frozen=True)
class Limits:
    #: Предел молчания. По умолчанию сильно больше самой длинной законной
    #: паузы (45 с между роликами) и повторов после отказа сети.
    silence_limit: float = 180.0
    sleep_min: int = 15
    sleep_max: int = 45
    sleep_requests: int = 2
    socket_timeout: int = 30


@dataclass(frozen=True)
class Config:
    paths: Paths
    height: int = 1080
    prefer_av1: bool = True
    write_subs: bool = True
    sub_langs: tuple[str, ...] = ("ru", "en")
    break_on_existing: bool = False
    limits: Limits = Limits()


def loads(text: str) -> dict:
    """Разобрать TOML. Единственное место, где это делается."""
    return _toml.loads(text)


TomlError = _toml.TOMLDecodeError


class ConfigError(ValueError):
    """Настройки не годятся. Текст пишется так, чтобы его можно было
    показать человеку без перевода."""


def _check_unknown(section: str, given: dict, known: set[str]) -> None:
    unknown = sorted(set(given) - known)
    if unknown:
        raise ConfigError(
            f"в разделе [{section}] неизвестные ключи: {', '.join(unknown)}. "
            f"Понятные: {', '.join(sorted(known))}"
        )


def parse_config(data: dict) -> Config:
    """Разобрать настройки. Единственный обязательный ключ — `paths.base`."""
    if not isinstance(data, dict):
        raise ConfigError("настройки должны быть таблицей")

    _check_unknown("верхний уровень", data, KNOWN_SECTIONS)

    raw_paths = data.get("paths")
    if not isinstance(raw_paths, dict) or not raw_paths.get("base"):
        raise ConfigError("нужен раздел [paths] с ключом base — куда складывать архив")
    _check_unknown("paths", raw_paths, KNOWN_PATHS)
    paths = Paths(**raw_paths)

    raw_download = data.get("download", {})
    if not isinstance(raw_download, dict):
        raise ConfigError("раздел [download] должен быть таблицей")
    _check_unknown("download", raw_download, KNOWN_DOWNLOAD)

    height = raw_download.get("height", 1080)
    if height not in ALLOWED_HEIGHTS:
        raise ConfigError(
            f"height = {height} не годится. Понятные значения: "
            f"{', '.join(str(h) for h in ALLOWED_HEIGHTS)}"
        )

    langs = raw_download.get("sub_langs", ["ru", "en"])
    if not isinstance(langs, list) or not all(isinstance(x, str) for x in langs):
        raise ConfigError("sub_langs — список строк, например [\"ru\", \"en\"]")

    raw_limits = data.get("limits", {})
    if not isinstance(raw_limits, dict):
        raise ConfigError("раздел [limits] должен быть таблицей")
    _check_unknown("limits", raw_limits, KNOWN_LIMITS)
    limits = Limits(**raw_limits)

    if limits.sleep_min > limits.sleep_max:
        raise ConfigError("sleep_min больше sleep_max — паузы заданы наоборот")
    if limits.silence_limit <= limits.sleep_max:
        # Иначе надзорщик начнёт убивать здоровую выкачку на паузе между роликами.
        raise ConfigError(
            f"silence_limit ({limits.silence_limit}) должен быть заметно больше "
            f"sleep_max ({limits.sleep_max}): пауза между роликами — не зависание"
        )

    return Config(
        paths=paths,
        height=height,
        prefer_av1=bool(raw_download.get("prefer_av1", True)),
        write_subs=bool(raw_download.get("write_subs", True)),
        sub_langs=tuple(langs),
        break_on_existing=bool(raw_download.get("break_on_existing", False)),
        limits=limits,
    )


def _toml_str(value: str) -> str:
    """Строка в кавычках, с экранированием того, что его требует.

    Пути на Windows содержат обратные слэши, а в TOML это знак экранирования.
    Без обработки `C:\\Users\\...` превратился бы при следующем чтении
    в мусор — молча, потому что файл остался бы формально годным.
    """
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dump_config(config: Config) -> str:
    """Собрать текст настроек из значений.

    Комментарии сохраняются: файл правит человек руками, и объяснения в нём
    ценнее аккуратности. Обратимость проверена тестом — что записали,
    то и прочитается.
    """
    langs = ", ".join(_toml_str(x) for x in config.sub_langs)
    return f"""\
# Настройки архиватора. Единственное обязательное — куда складывать.
[paths]
base = {_toml_str(config.paths.base)}
# Остальные пути считаются от base, если не заданы абсолютными.
channels = {_toml_str(config.paths.channels)}
archive  = {_toml_str(config.paths.archive)}
cookies  = {_toml_str(config.paths.cookies)}
logs     = {_toml_str(config.paths.logs)}
# Ролики, снятые галочкой в окне выбора. Не путать с archive: там скачанное.
excluded = {_toml_str(config.paths.excluded)}

[download]
height = {config.height}
# AV1 при равном разрешении даёт заметно меньший файл.
prefer_av1 = {str(config.prefer_av1).lower()}
write_subs = {str(config.write_subs).lower()}
sub_langs = [{langs}]
# Быстрый проход: включать ТОЛЬКО когда архив собран целиком, иначе
# он оборвётся на первом же скачанном ролике и остальное не заберёт.
break_on_existing = {str(config.break_on_existing).lower()}

[limits]
# Молчание дольше этого считается зависанием. Должно быть заметно больше
# паузы между роликами, иначе живую выкачку будут убивать.
silence_limit = {config.limits.silence_limit:g}
sleep_min = {config.limits.sleep_min}
sleep_max = {config.limits.sleep_max}
sleep_requests = {config.limits.sleep_requests}
socket_timeout = {config.limits.socket_timeout}
"""


DEFAULT_CONFIG_TEXT = """\
# Настройки архиватора. Единственное обязательное — куда складывать.
[paths]
base = "D:/Video/Архивы с YouTube"
# Остальные пути считаются от base, если не заданы абсолютными.
channels = "_tools/channels.txt"
archive  = "_tools/downloaded.txt"
cookies  = "_tools/cookies.txt"
logs     = "_logs"
# Ролики, снятые галочкой в окне выбора. Не путать с archive: там скачанное.
excluded = "_tools/excluded.txt"

[download]
height = 1080
# AV1 при равном разрешении даёт заметно меньший файл.
prefer_av1 = true
write_subs = true
sub_langs = ["ru", "en"]
# Быстрый проход: включать ТОЛЬКО когда архив собран целиком, иначе
# он оборвётся на первом же скачанном ролике и остальное не заберёт.
break_on_existing = false

[limits]
# Молчание дольше этого считается зависанием. Должно быть заметно больше
# паузы между роликами, иначе живую выкачку будут убивать.
silence_limit = 180
sleep_min = 15
sleep_max = 45
sleep_requests = 2
socket_timeout = 30
"""
