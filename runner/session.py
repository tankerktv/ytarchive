"""Цикл выкачки: перепись → очередь → загрузка под надзором → архив.

Склейка, а не новая логика. Каждое решение принимает ядро:
`flow.decide_after_probe` решает, качать или звать человека, `supervisor.judge` —
снимать ли зависшего, `ytdlp_args` собирает ключи. Здесь только исполнение.

Путь к yt-dlp передаётся снаружи — иначе цикл не проверить, не выходя в сеть.
В тестах вместо него подставляется поддельный, печатающий настоящие строки
из наших журналов.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path

from core.archive import parse_archive
from core.channels import Channel, parse_channels
from core.exclusions import Exclusions, apply_to
from core.flow import Action, ChannelResult, SessionSummary, decide_after_probe
from core.probe import diagnose
from core.progress import Event, EventKind, parse_line
from core.supervisor import RetryPolicy, WatchdogPolicy
from core.videos import Listing, parse_listing
from core.ytdlp_args import (
    DownloadSettings,
    build_batch_args,
    build_enumerate_args,
    build_probe_args,
    output_template_for,
)
from runner.process import run_watched
from runner.language import _


@dataclass(frozen=True)
class SessionConfig:
    base_dir: Path
    channels_file: Path
    settings: DownloadSettings
    #: Команда запуска, а не путь: списком, чтобы yt-dlp можно было звать
    #: через обёртку или интерпретатор. Без этого цикл не проверить,
    #: не выходя в сеть.
    ytdlp: tuple[str, ...] = ("yt-dlp",)
    watchdog: WatchdogPolicy = field(default_factory=lambda: WatchdogPolicy(silence_limit=180.0))
    retries: RetryPolicy = field(default_factory=RetryPolicy)
    #: Проверка доступа терпит меньше самой загрузки: она обязана либо
    #: ответить быстро, либо считаться зависшей. Именно её отсутствие
    #: стопорило задание на часы.
    probe_watchdog: WatchdogPolicy = field(
        default_factory=lambda: WatchdogPolicy(silence_limit=60.0, total_limit=180.0)
    )


def _read_text(path: Path) -> str | None:
    """Прочитать файл. `None` значит «не смог», а не «пусто».

    Различать это обязательно: пустой список каналов — законное состояние,
    а нечитаемый файл — беда, из-за которой выкачка тихо не сделает ничего.
    """
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _archive_ids(path: Path) -> frozenset[str]:
    text = _read_text(path)
    return parse_archive(text).video_ids if text is not None else frozenset()


def probe_channel(
    channel: Channel,
    config: SessionConfig,
    *,
    on_event: Callable[[str], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
):
    """Достучаться до канала, пережидая проходящие беды.

    Возвращает решение ядра: качать, или остановиться с причиной,
    которую можно показать человеку без перевода.
    """
    решение = None
    диагноз = None
    for attempt in range(1, config.retries.max_attempts + 1):
        args = build_probe_args(config.settings, channel.url)
        outcome = run_watched([*config.ytdlp, *args], config.probe_watchdog)
        result = diagnose(outcome.text, outcome.exit_code if outcome.exit_code is not None else 1)
        диагноз = result.diagnosis
        решение = decide_after_probe(result.diagnosis, attempt, config.retries)

        if on_event is not None:
            # Подробность обязательна: без неё по журналу нельзя понять,
            # что именно ответил yt-dlp, и разбираться приходится заново,
            # воспроизводя сбой руками. Проверено на себе 30.08.
            хвост = f" ({result.detail[:120]})" if result.detail else ""
            on_event(_('{}: проверка — {}{}').format(channel.name, result.diagnosis.value, хвост))

        if решение.action is not Action.RETRY:
            return решение, диагноз
        sleep(решение.delay)

    return решение, диагноз


def enumerate_channel(
    channel: Channel,
    config: SessionConfig,
    *,
    should_stop: Callable[[], bool] | None = None,
) -> Listing:
    """Переписать канал: идентификаторы, длительности, названия.

    Раньше перепись делал сам yt-dlp внутри загрузки, и вмешаться было
    некуда. Теперь она наша — только так можно вычесть исключённые ролики.
    """
    args = build_enumerate_args(config.settings, channel.url)
    # Потоки разделяем: в stderr yt-dlp пишет своё («Deprecated Feature: ...»),
    # и в слитом тексте эти строки засчитываются в потерянные ролики.
    outcome = run_watched(
        [*config.ytdlp, *args],
        config.probe_watchdog,
        separate_streams=True,
        should_stop=should_stop,
    )
    return parse_listing(outcome.stdout_text)


def download_channel(
    channel: Channel,
    config: SessionConfig,
    *,
    exclusions: Exclusions | None = None,
    on_event: Callable[[Event], None] | None = None,
    on_message: Callable[[str], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> tuple[int, int]:
    """Пройти по каналу. Возвращает (скачано, упало).

    Скачанное считается по приросту файла архива, а не по строкам вывода:
    в архив попадают только целиком собранные ролики, и это единственный
    источник, которому можно верить.
    """
    archive_path = Path(config.settings.archive_path)
    было = _archive_ids(archive_path)
    исключения = exclusions or Exclusions()

    перепись = enumerate_channel(channel, config, should_stop=should_stop)
    if перепись.unreadable and on_message is not None:
        on_message(
            _('{}: непонятых строк в переписи {}').format(channel.name, len(перепись.unreadable))
        )

    очередь = [v.video_id for v in перепись.videos if v.video_id not in было]
    всего_до = len(очередь)
    очередь = apply_to(очередь, исключения)
    снято = всего_до - len(очередь)

    if снято and on_message is not None:
        on_message(_('{}: пропущено по вашему выбору {}').format(channel.name, снято))

    if not очередь:
        return 0, 0

    # Список подаётся файлом: у канала бывает шестьсот роликов, и в командную
    # строку они не влезут.
    batch = archive_path.parent / f"batch-{channel.name}.txt"
    try:
        batch.write_text("\n".join(очередь) + "\n", encoding="utf-8", newline="\n")
    except OSError as ошибка:
        if on_message is not None:
            on_message(_('{}: не удалось записать список — {}').format(channel.name, ошибка))
        return 0, 0

    упало = 0

    def on_line(line: str) -> None:
        nonlocal упало
        event = parse_line(line)
        if event.kind is EventKind.ERROR:
            упало += 1
        if on_event is not None:
            on_event(event)

    try:
        # Папка — по имени из нашего списка, а не по названию канала на YouTube:
        # иначе переименование канала его владельцем раскалывает архив надвое.
        settings = replace(
            config.settings,
            output_template=output_template_for(str(config.base_dir), channel.name),
        )
        args = build_batch_args(settings, str(batch))
        run_watched(
            [*config.ytdlp, *args],
            config.watchdog,
            on_line=on_line,
            should_stop=should_stop,
        )
    finally:
        # Список — вещь одноразовая: оставленный, он собьёт с толку при
        # разборе беды, показав вчерашнюю очередь как сегодняшнюю.
        try:
            batch.unlink()
        except OSError:
            pass

    стало = _archive_ids(archive_path)
    return len(стало - было), упало


def run_session(
    config: SessionConfig,
    *,
    exclusions: Exclusions | None = None,
    on_event: Callable[[Event], None] | None = None,
    on_message: Callable[[str], None] | None = None,
    on_channel: Callable[[str, int, int], None] | None = None,
    on_stopped: Callable[[str, str], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    should_stop: Callable[[], bool] | None = None,
) -> SessionSummary:
    """Пройти по всем каналам списка.

    `should_stop` спрашивается перед каждым каналом и передаётся вглубь,
    к самому yt-dlp: остановка, доходящая только до конца текущего канала,
    может думать часами, а человек в это время смотрит на кнопку.
    """
    text = _read_text(config.channels_file)
    if text is None:
        return SessionSummary(
            results=(
                ChannelResult(
                    channel=str(config.channels_file),
                    stopped_reason="не удалось прочитать список каналов",
                ),
            )
        )

    parsed = parse_channels(text)
    # Непонятые строки не выбрасываем молча: иначе канал просто перестанет
    # качаться, и заметят это через недели.
    for problem in parsed.problems:
        if on_message is not None:
            on_message(_('строка {} пропущена: {}').format(problem.line_number, problem.reason))

    results: list[ChannelResult] = []
    for номер, channel in enumerate(parsed.channels, start=1):
        if should_stop is not None and should_stop():
            if on_message is not None:
                on_message(_("остановлено по просьбе — остальные каналы ждут следующего прохода"))
            break
        if on_channel is not None:
            on_channel(channel.name, номер, len(parsed.channels))
        решение, диагноз = probe_channel(channel, config, on_event=on_message, sleep=sleep)
        if решение is None or решение.action is Action.STOP:
            причина = решение.reason if решение else "проверка не дала ответа"
            results.append(ChannelResult(channel=channel.name, stopped_reason=причина))
            # Отдельно от журнала: окно узнаёт причину из живого состояния,
            # а не разбором текста — текст переводится, разбор перевода это
            # гадание.
            if on_stopped is not None:
                on_stopped(channel.name, причина)
            if on_message is not None:
                on_message(_('{}: остановлено — {}').format(channel.name, _(причина)))
                # Счёт попыток — отдельной строкой, а не приклеенным к причине:
                # склеенная, она становится непереводимой, а в шапке окна
                # число попыток и не нужно — там нужно, что чинить.
                if решение is not None and решение.attempts:
                    on_message(_('{}: не прошло за {} попыток').format(channel.name, решение.attempts))

            # Общая беда — сеть, куки, устаревший yt-dlp — одинакова для всех
            # каналов. Перебирать остальные значит потратить минуты и получить
            # четыре одинаковых записи вместо одной внятной.
            if диагноз is not None and диагноз.is_global:
                оставшиеся = [c for c in parsed.channels if c.name != channel.name
                              and not any(r.channel == c.name for r in results)]
                if оставшиеся and on_message is not None:
                    on_message(
                        _('беда общая для всех каналов — остальные ({}) не проверяю, ждём следующего прохода').format(len(оставшиеся))
                    )
                break
            continue

        скачано, упало = download_channel(
            channel, config, exclusions=exclusions,
            on_event=on_event, on_message=on_message, should_stop=should_stop,
        )
        results.append(ChannelResult(channel=channel.name, downloaded=скачано, failed=упало))
        if on_message is not None:
            on_message(_('{}: скачано {}, упало {}').format(channel.name, скачано, упало))

    return SessionSummary(results=tuple(results))
