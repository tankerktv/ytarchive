"""Разбор настроек.

Чистый: на входе разобранный словарь, на выходе проверенные значения или
внятная жалоба. Чтение файла — в точке входа, здесь только смысл.

Правило то же, что везде: **ничего не принимается молча.** Неизвестный ключ
в настройках — это опечатка, из-за которой человек будет неделю думать,
что задал потолок разрешения, а качается по-прежнему 1080p.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.i18n import НАЗВАНИЯ, СИСТЕМНЫЙ
from core.schedule import Hours, Rhythm, format_hours, parse_hours

# tomllib появился в 3.11. На машине, где это писалось, настоящий
# интерпретатор только 3.10 — а привязываться к тому, чего нет,
# значит получить задание, падающее до первой строки Python.
try:
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover — ветка для 3.10
    import tomli as _toml


from core.ytdlp_args import ALLOWED_HEIGHTS

#: Ключи, которые мы понимаем. Всё остальное — повод пожаловаться.
KNOWN_SECTIONS = {"paths", "download", "limits", "schedule", "interface"}
#: Язык интерфейса. Отдельным разделом, а не в [download]: он про окно,
#: а не про то, что и как качать.
KNOWN_INTERFACE = {"language"}
#: Паузы задаются минутами: секунды в настройках, которые правит человек,
#: читаются плохо — «1800» надо ещё поделить в уме.
KNOWN_SCHEDULE = {"pause_idle", "pause_busy", "pause_trouble", "hours"}
KNOWN_PATHS = {"base", "channels", "archive", "cookies", "logs", "excluded"}
KNOWN_DOWNLOAD = {
    "height", "prefer_av1", "write_subs", "sub_langs", "break_on_existing",
    "cookies_browser", "rate_limit",
}
KNOWN_LIMITS = {
    "silence_limit", "sleep_min", "sleep_max", "sleep_requests", "socket_timeout",
    "crawl_minutes", "crawl_speed", "keep_logs_days",
}

#: Браузеры, из которых yt-dlp умеет брать куки. Список его, не наш:
#: опечатку лучше поймать при чтении настроек, чем увидеть ночью отказом
#: «unsupported browser» на каждом канале.
BROWSERS = ("brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi", "whale")


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
    #: Загрузка, которая говорит, но идёт медленнее `crawl_speed` КиБ/с дольше
    #: `crawl_minutes` минут, снимается и откладывается до следующего прохода.
    #: Ноль в скорости выключает проверку — на медленной линии так и надо.
    crawl_minutes: float = 10.0
    crawl_speed: int = 100
    #: Сколько суток хранить журналы проходов. Ноль — не убирать никогда.
    keep_logs_days: int = 30


@dataclass(frozen=True)
class Config:
    paths: Paths
    height: int = 1080
    prefer_av1: bool = True
    write_subs: bool = True
    sub_langs: tuple[str, ...] = ("ru", "en")
    break_on_existing: bool = False
    limits: Limits = Limits()
    #: Ритм проходов. Раньше его задавал планировщик Windows — «каждые
    #: полчаса», одинаково на все случаи.
    rhythm: Rhythm = field(default_factory=Rhythm)
    #: Браузер, из которого брать куки. Пусто — из файла `paths.cookies`.
    cookies_browser: str = ""
    #: Потолок скорости, КиБ/с. Ноль — без потолка.
    rate_limit: int = 0
    #: Часы, когда качать можно. None — всегда.
    hours: Hours | None = None
    #: Язык интерфейса. «system» значит «спросить у системы» — так и стоит
    #: по умолчанию: чужой язык на первом запуске хуже отсутствия выбора.
    language: str = СИСТЕМНЫЙ


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

    if limits.crawl_minutes <= 0:
        raise ConfigError(
            "crawl_minutes должен быть больше нуля; чтобы выключить проверку, поставьте crawl_speed = 0"
        )
    if limits.crawl_speed < 0 or limits.keep_logs_days < 0:
        raise ConfigError("crawl_speed и keep_logs_days не могут быть отрицательными")

    cookies_browser = str(raw_download.get("cookies_browser", "")).strip().lower()
    if cookies_browser and cookies_browser not in BROWSERS:
        raise ConfigError(
            f"cookies_browser = {cookies_browser!r} — такого браузера yt-dlp не знает. "
            f"Понятные: {', '.join(BROWSERS)}; пусто — брать куки из файла"
        )

    rate_limit = raw_download.get("rate_limit", 0)
    if not isinstance(rate_limit, int) or isinstance(rate_limit, bool) or rate_limit < 0:
        raise ConfigError("rate_limit — целое число КиБ/с; 0 значит без потолка")
    if rate_limit and limits.crawl_speed and rate_limit < limits.crawl_speed * 2:
        # Иначе потолок сам делал бы каждую загрузку «ползущей», и надзорщик
        # снимал бы ровно то, что человек попросил качать помедленнее.
        raise ConfigError(
            f"rate_limit ({rate_limit}) слишком близко к crawl_speed ({limits.crawl_speed}): "
            "потолок скорости должен быть хотя бы вдвое выше порога ползущей загрузки, "
            "иначе выкачка будет снимать сама себя. Поднимите rate_limit или "
            "уменьшите crawl_speed (0 выключает проверку)"
        )

    raw_schedule = data.get("schedule", {})
    if not isinstance(raw_schedule, dict):
        raise ConfigError("раздел [schedule] должен быть таблицей")
    _check_unknown("schedule", raw_schedule, KNOWN_SCHEDULE)
    по_умолчанию = Rhythm()
    try:
        rhythm = Rhythm(
            idle=float(raw_schedule.get("pause_idle", по_умолчанию.idle / 60)) * 60,
            busy=float(raw_schedule.get("pause_busy", по_умолчанию.busy / 60)) * 60,
            trouble=float(raw_schedule.get("pause_trouble", по_умолчанию.trouble / 60)) * 60,
        )
        hours = parse_hours(str(raw_schedule.get("hours", "")))
    except (TypeError, ValueError) as ошибка:
        raise ConfigError(f"раздел [schedule]: {ошибка}") from ошибка

    raw_interface = data.get("interface", {})
    if not isinstance(raw_interface, dict):
        raise ConfigError("раздел [interface] должен быть таблицей")
    _check_unknown("interface", raw_interface, KNOWN_INTERFACE)
    language = str(raw_interface.get("language", СИСТЕМНЫЙ)).strip() or СИСТЕМНЫЙ
    if language != СИСТЕМНЫЙ and language not in НАЗВАНИЯ:
        # Опечатку тут молча не прощаем: «ne» вместо «de» дало бы английский,
        # и человек до последнего думал бы, что перевода просто нет.
        raise ConfigError(
            f"language = {language!r} — такого языка не знаю. Понятные значения: "
            f"{СИСТЕМНЫЙ}, {', '.join(sorted(НАЗВАНИЯ))}"
        )

    return Config(
        paths=paths,
        rhythm=rhythm,
        hours=hours,
        cookies_browser=cookies_browser,
        rate_limit=rate_limit,
        language=language,
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
# Откуда брать куки YouTube. Пусто — из файла cookies (см. [paths]).
# Иначе имя браузера: firefox, chrome, edge, brave и другие. Из Firefox
# работает надёжно; Chrome и Edge на Windows куки шифруют, и yt-dlp
# часто не может их прочитать.
cookies_browser = {_toml_str(config.cookies_browser)}
# Потолок скорости, КиБ/с. 0 — без потолка.
rate_limit = {config.rate_limit}

[limits]
# Молчание дольше этого считается зависанием. Должно быть заметно больше
# паузы между роликами, иначе живую выкачку будут убивать.
silence_limit = {config.limits.silence_limit:g}
sleep_min = {config.limits.sleep_min}
sleep_max = {config.limits.sleep_max}
sleep_requests = {config.limits.sleep_requests}
socket_timeout = {config.limits.socket_timeout}
# Загрузку, которая идёт медленнее crawl_speed КиБ/с дольше crawl_minutes
# минут, снимаем и откладываем до следующего прохода: скачанное не теряется.
# На медленной линии поставьте crawl_speed = 0 — проверка выключится.
crawl_minutes = {config.limits.crawl_minutes:g}
crawl_speed = {config.limits.crawl_speed}
# Сколько суток хранить журналы проходов. 0 — не убирать.
keep_logs_days = {config.limits.keep_logs_days}

[schedule]
# Паузы между проходами, в минутах. Программа держит их сама — планировщик
# задач больше не нужен.
# Ничего нового не нашлось:
pause_idle = {config.rhythm.idle / 60:g}
# Что-то скачали — в очереди почти наверняка есть ещё:
pause_busy = {config.rhythm.busy / 60:g}
# Нужен человек (истёкшие куки, устаревший yt-dlp): долбиться в стену незачем.
pause_trouble = {config.rhythm.trouble / 60:g}
# Часы, когда качать можно: "23-7" или "23:00-07:30". Пусто — всегда.
# Вне этих часов обход ждёт, а идущую загрузку прерывает — она продолжится.
hours = {_toml_str(format_hours(config.hours))}

[interface]
# Язык окна. «system» — взять у системы. Иначе код языка: ru, en, de, es, fr.
language = {_toml_str(config.language)}
"""


#: Место, куда `init` подставит домашний каталог хозяина машины. Держать
#: в образце чужой рабочий путь нельзя: он не подойдёт никому другому и
#: расскажет о прежнем владельце больше, чем нужно.
HOME_MARK = "ДОМАШНИЙ-КАТАЛОГ"

DEFAULT_CONFIG_TEXT = """\
# Настройки архиватора. Единственное обязательное — куда складывать.
[paths]
base = "ДОМАШНИЙ-КАТАЛОГ/Архив YouTube"
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
# Откуда брать куки YouTube. Пусто — из файла cookies (см. [paths]).
# Иначе имя браузера: firefox, chrome, edge, brave и другие. Из Firefox
# работает надёжно; Chrome и Edge на Windows куки шифруют, и yt-dlp
# часто не может их прочитать.
cookies_browser = ""
# Потолок скорости, КиБ/с. 0 — без потолка.
rate_limit = 0

[limits]
# Молчание дольше этого считается зависанием. Должно быть заметно больше
# паузы между роликами, иначе живую выкачку будут убивать.
silence_limit = 180
sleep_min = 15
sleep_max = 45
sleep_requests = 2
socket_timeout = 30
# Загрузку, которая идёт медленнее crawl_speed КиБ/с дольше crawl_minutes
# минут, снимаем и откладываем до следующего прохода: скачанное не теряется.
# На медленной линии поставьте crawl_speed = 0 — проверка выключится.
crawl_minutes = 10
crawl_speed = 100
# Сколько суток хранить журналы проходов. 0 — не убирать.
keep_logs_days = 30

[schedule]
# Паузы между проходами, в минутах. Программа держит их сама — планировщик
# задач больше не нужен.
pause_idle = 30
pause_busy = 1
pause_trouble = 60
# Часы, когда качать можно: "23-7" или "23:00-07:30". Пусто — всегда.
# Вне этих часов обход ждёт, а идущую загрузку прерывает — она продолжится.
hours = ""

[interface]
# Язык окна. «system» — взять у системы. Иначе код языка: ru, en, de, es, fr.
language = "system"
"""
