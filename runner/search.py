"""Поиск канала и его перепись — то, что требует сети.

Разделено на два шага намеренно. Поиск отвечает за секунды и даёт список
названий; перепись канала может занять минуты — у канала на 2111 роликов
она шла заметно дольше поиска. Показывать человеку пустое окно всё это время
нельзя, поэтому окно рисует найденное сразу, а числа подставляет по мере
готовности.
"""

from __future__ import annotations

from collections.abc import Callable

from core.search import Candidate, parse_search_output, with_measurement
from core.supervisor import WatchdogPolicy
from core.ytdlp_args import DownloadSettings
from runner.process import run_watched

#: Поиск обязан отвечать быстро либо не отвечать вовсе: человек ждёт у окна.
SEARCH_WATCHDOG = WatchdogPolicy(silence_limit=45.0, total_limit=120.0)

#: Перепись большого канала идёт минутами, и это законно.
MEASURE_WATCHDOG = WatchdogPolicy(silence_limit=90.0, total_limit=900.0)

#: Сколько роликов просматривать в поиске. Больше — дольше и без пользы:
#: нужный канал почти всегда в первых.
SEARCH_LIMIT = 20


def _cookie_args(settings: DownloadSettings) -> list[str]:
    if settings.cookies_file:
        return ["--cookies", settings.cookies_file]
    if settings.cookies_browser:
        return ["--cookies-from-browser", settings.cookies_browser]
    return []


def search_channels(
    query: str,
    settings: DownloadSettings,
    *,
    ytdlp: tuple[str, ...] = ("yt-dlp",),
    limit: int = SEARCH_LIMIT,
) -> tuple[list[Candidate], str]:
    """Найти каналы по названию. Возвращает (кандидаты, объяснение).

    Пустой запрос — не повод идти в сеть.
    """
    query = query.strip()
    if not query:
        return [], "пустой запрос"

    args = [
        *_cookie_args(settings),
        "--js-runtimes", "node",
        "--socket-timeout", str(settings.socket_timeout),
        "--flat-playlist",
        "--print", "%(channel)s|%(channel_id)s",
        "--no-warnings",
        f"ytsearch{limit}:{query}",
    ]
    outcome = run_watched([*ytdlp, *args], SEARCH_WATCHDOG)
    кандидаты = parse_search_output(outcome.lines)

    if not кандидаты:
        # Отличаем «не нашлось» от «не смогли спросить»: человеку это
        # разные новости, и вторая требует от него действий.
        if outcome.exit_code not in (0, None) or outcome.killed:
            return [], f"поиск не удался: {_первая_беда(outcome.lines)}"
        return [], "ничего не нашлось"
    return кандидаты, f"нашлось каналов: {len(кандидаты)}"


def measure_channel(
    candidate: Candidate,
    settings: DownloadSettings,
    *,
    ytdlp: tuple[str, ...] = ("yt-dlp",),
) -> tuple[Candidate, str]:
    """Переписать канал, чтобы узнать объём.

    Это и есть та работа, ради которой всё затевалось: объём должен быть
    известен ДО добавления.
    """
    args = [
        *_cookie_args(settings),
        "--js-runtimes", "node",
        "--extractor-args", "youtubetab:skip=authcheck",
        "--socket-timeout", str(settings.socket_timeout),
        "--flat-playlist",
        "--print", "%(duration)s",
        "--no-warnings",
        candidate.url,
    ]
    # Вывод здесь — данные, по строке на ролик, и нужны все: с пределом журнала
    # канал на две тысячи роликов измерялся как канал на четыреста, и окно
    # обещало «влезет» про впятеро больший объём.
    outcome = run_watched(
        [*ytdlp, *args], MEASURE_WATCHDOG, separate_streams=True, keep_all_stdout=True
    )

    длительности: list[float] = []
    for строка in outcome.stdout_lines:
        значение = строка.strip()
        try:
            длительности.append(float(значение))
        except ValueError:
            continue  # NA у трансляций и премьер — это законно

    if not длительности:
        return candidate, f"перепись не удалась: {_первая_беда(outcome.lines)}"
    return with_measurement(candidate, длительности), "измерено"


def measure_all(
    candidates: list[Candidate],
    settings: DownloadSettings,
    *,
    ytdlp: tuple[str, ...] = ("yt-dlp",),
    on_measured: Callable[[int, Candidate, str], None] | None = None,
    stop: Callable[[], bool] | None = None,
) -> list[Candidate]:
    """Перемерить всех по очереди, сообщая о каждом.

    `stop` позволяет бросить работу, если человек закрыл окно или начал
    новый поиск: досчитывать ненужное — значит держать его в ожидании зря.
    """
    итог = list(candidates)
    for номер, кандидат in enumerate(итог):
        if stop is not None and stop():
            break
        измеренный, ответ = measure_channel(кандидат, settings, ytdlp=ytdlp)
        итог[номер] = измеренный
        if on_measured is not None:
            on_measured(номер, измеренный, ответ)
    return итог


def _первая_беда(lines: list[str]) -> str:
    for строка in lines:
        if строка.strip().upper().startswith("ERROR"):
            return строка.strip()[:160]
    return lines[-1][:160] if lines else "без объяснения"
