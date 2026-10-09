"""Точка входа.

Режимы разведены намеренно: `plan` только считает и печатает, `run` качает.
Правило «сначала вхолостую, потом на живом» здесь буквальное — команда,
меняющая данные, называется отдельным словом, а не флагом к обычной.

    ytarchive init            создать настройки рядом с собой
    ytarchive check           достучаться до каналов, ничего не качая
    ytarchive plan            что будет скачано и сколько это займёт
    ytarchive run             качать — один проход и выход
    ytarchive daemon          качать непрерывно, своим расписанием
    ytarchive stop            попросить работающий экземпляр остановиться
    ytarchive verify          сверить учёт с файлами на диске
    ytarchive clean           показать, что из старого можно убрать
    ytarchive update          обновить yt-dlp
    ytarchive nfo             описания для медиасервера (Jellyfin, Kodi, Plex)
    ytarchive notify          проверить уведомления в Telegram
    ytarchive gui             окно наблюдения
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from dataclasses import replace
from pathlib import Path

from core.archive import parse_archive
from core.channels import parse_channels
from core.crawl import CrawlPolicy
from core.config import (
    DEFAULT_CONFIG_TEXT,
    HOME_MARK,
    Config,
    ConfigError,
    TomlError,
    loads,
    parse_config,
)
from core.cleanup import FileInfo, is_leftover, old_logs, stale_leftovers, total_size
from core.exclusions import Exclusions, parse_exclusions
from core.update import update_command
from core.verify import compare, without_duplicates
from core.flow import SessionSummary
from core.planner import estimate_range
from core.livestate import (
    LiveState,
    apply_event,
    should_write,
    start_channel,
    stop_channel,
    to_text,
)
from core.progress import Event, EventKind
from core.supervisor import WatchdogPolicy
from core.ytdlp_args import FILE_TEMPLATE, DownloadSettings
from runner.daemon import ask_stop, daemon_running, run_forever
from runner.lockfile import acquire
from runner.language import _
from runner.session import SessionConfig, probe_channel, run_session

CONFIG_NAME = "ytarchive.toml"


def resolve(base: Path, value: str) -> Path:
    """Пути в настройках считаются от base, если не заданы абсолютными."""
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_config(path: Path) -> tuple[Config, Path]:
    try:
        data = loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(
            _('нет файла настроек {}. Создать образец: ytarchive init').format(path)
        ) from None
    except TomlError as error:
        raise ConfigError(_('{}: не разбирается как TOML — {}').format(path, error)) from None
    return parse_config(data), path


def build_session(config: Config, base: Path) -> SessionConfig:
    archive = resolve(base, config.paths.archive)
    cookies = resolve(base, config.paths.cookies)
    settings = DownloadSettings(
        archive_path=str(archive),
        # Запасной шаблон: цикл выкачки подставляет свой на каждый канал, с
        # папкой по имени из списка (см. core.ytdlp_args.output_template_for).
        output_template=str(base / "%(channel)s" / FILE_TEMPLATE),
        # Браузер перевешивает файл: человек выбрал его явно, а файл мог
        # остаться с прежних времён. Оба сразу yt-dlp не принимает.
        cookies_file=str(cookies) if (cookies.exists() and not config.cookies_browser) else None,
        cookies_browser=config.cookies_browser or None,
        rate_limit=config.rate_limit,
        write_comments=config.write_comments,
        write_thumbnail=config.media_server,
        height=config.height,
        prefer_av1=config.prefer_av1,
        write_subs=config.write_subs,
        sub_langs=config.sub_langs,
        sleep_min=config.limits.sleep_min,
        sleep_max=config.limits.sleep_max,
        sleep_requests=config.limits.sleep_requests,
        socket_timeout=config.limits.socket_timeout,
        break_on_existing=config.break_on_existing,
    )
    return SessionConfig(
        base_dir=base,
        channels_file=resolve(base, config.paths.channels),
        settings=settings,
        watchdog=WatchdogPolicy(silence_limit=config.limits.silence_limit),
        crawl=CrawlPolicy(
            window=config.limits.crawl_minutes * 60,
            min_speed=config.limits.crawl_speed * 1024,
        ),
    )


def cmd_init(args) -> int:
    target = Path(args.config)
    if target.exists() and not args.force:
        print(_('{} уже есть. Перезаписать: --force').format(target), file=sys.stderr)
        return 1
    # В образце стоит метка, а не чей-то рабочий путь: чужой не подойдёт
    # никому и расскажет о прежнем владельце больше, чем нужно.
    образец = DEFAULT_CONFIG_TEXT.replace(HOME_MARK, Path.home().as_posix())

    if args.dry_run:
        print(_('создал бы {}:\n').format(target))
        print(образец)
        return 0
    target.write_text(образец, encoding="utf-8", newline="\n")
    print(_('создан {} — поправьте пути и запустите: ytarchive check').format(target))
    return 0


def load_exclusions(path: Path, скажи=None) -> Exclusions:
    """Прочитать снятые галочки.

    Отсутствие файла — обычное дело: галочек ещё не снимали. А вот
    нечитаемый файл замалчивать нельзя: выкачка молча заберёт всё, что
    человек убрал, и он узнает об этом по забитому диску.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return Exclusions()
    except OSError as ошибка:
        if скажи is not None:
            скажи(_('список исключений не прочитан ({}) — качаю всё').format(ошибка))
        return Exclusions()

    итог = parse_exclusions(text)
    if итог.unreadable and скажи is not None:
        скажи(
            _('в списке исключений непонятых строк {}: {}').format(len(итог.unreadable), ', '.join(итог.unreadable[:3]))
        )
    return итог


def _state(session: SessionConfig):
    """Прочитать состояние: каналы и архив. Ничего не меняет."""
    channels_text = session.channels_file.read_text(encoding="utf-8")
    parsed = parse_channels(channels_text)
    archive_path = Path(session.settings.archive_path)
    archive = parse_archive(archive_path.read_text(encoding="utf-8")) if archive_path.exists() else parse_archive("")
    return parsed, archive


def cmd_plan(args) -> int:
    config, path = load_config(Path(args.config))
    base = Path(config.paths.base)
    session = build_session(config, base)
    parsed, archive = _state(session)

    print(_('настройки:  {}').format(path))
    print(_('архив:      {}').format(base))
    print(_('каналов:    {}').format(len(parsed.channels)))
    for problem in parsed.problems:
        print(_('  строка {} пропущена: {}').format(problem.line_number, problem.reason))
    print(_('уже скачано: {} роликов').format(len(archive)))
    if archive.unreadable:
        print(_('  непонятных строк в архиве: {}').format(len(archive.unreadable)))
    print(_('качество:   до {}p').format(config.height) + (_(", предпочтение AV1") if config.prefer_av1 else ""))
    print(_('куки:       {}').format(
        session.settings.cookies_file
        or (_('из браузера {}').format(config.cookies_browser) if config.cookies_browser else "")
        or _('не заданы — YouTube откажет')
    ))
    print()
    print(_("Сколько займёт час материала при измеренных битрейтах:"))
    низ, верх = estimate_range(3600)
    print(_('  {:.2f}–{:.2f} ГБ').format(низ / 1024**3, верх / 1024**3))
    print()
    print(_("Ничего не скачано и не изменено. Качать: ytarchive run"))
    return 0


def cmd_check(args) -> int:
    config, _путь = load_config(Path(args.config))
    base = Path(config.paths.base)
    session = build_session(config, base)
    parsed, _архив = _state(session)

    from runner.preflight import чего_не_хватает

    нехватки = чего_не_хватает()
    for нехватка in нехватки:
        print(f"  {нехватка}")
    if нехватки:
        print()

    плохих = 0
    for channel in parsed.channels:
        # Пара, а не одно значение: диагноз нужен циклу выкачки, чтобы не
        # перебирать все каналы на общей беде. Здесь он не нужен.
        решение, _диагноз = probe_channel(channel, session, sleep=lambda _пауза: None)
        if решение is None or решение.needs_human:
            причина = решение.reason if решение else _("проверка не дала ответа")
            print(_('  {}: ОТКАЗ — {}').format(channel.name, причина))
            плохих += 1
        else:
            print(_('  {}: доступ есть').format(channel.name))
    print()
    print(_("все каналы отвечают") if not плохих else _('каналов с бедой: {}').format(плохих))
    return 1 if (плохих or нехватки) else 0


def один_проход(config: Config, base: Path, session: SessionConfig, should_stop=None):
    """Один проход по каналам: замок, журнал, живое состояние, выкачка.

    Отделён от команды, потому что проходов теперь два хозяина: разовый
    `run` и непрерывный `daemon`. Всё, что здесь есть, нужно обоим.
    """
    logs_dir = resolve(base, config.paths.logs)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{datetime.now():%Y-%m-%d_%H%M}.log"
    log = log_path.open("a", encoding="utf-8", newline="\n")

    def скажи(текст: str) -> None:
        строка = f"{datetime.now():%H:%M:%S}  {текст}"
        # Задание идёт под pythonw, у которого стандартный поток может
        # отсутствовать. На этой машине он есть и печать проходит, но
        # полагаться на это нельзя: журнал важнее консоли, и падение
        # из-за неё стоило бы ночи выкачки.
        if sys.stdout is not None:
            try:
                print(строка, flush=True)
            except (OSError, ValueError):
                pass
        log.write(строка + "\n")
        log.flush()

    # Живое состояние — отдельным файлом: в журнал проценты не пишем,
    # он бы распух до сотен тысяч строк, а окну они нужны каждую секунду.
    live_path = logs_dir.parent / "_tools" / "ytarchive-live.json"
    live = LiveState()
    last_write = 0.0

    def записать_состояние(force: bool = False) -> None:
        nonlocal last_write
        now = time.time()
        if not force and not should_write(last_write, now):
            return
        try:
            live_path.write_text(to_text(live), encoding="utf-8", newline="\n")
        except OSError:
            pass  # окно переживёт отсутствие файла; выкачка важнее
        last_write = now

    lock, объяснение = acquire(logs_dir.parent / "_tools" / "ytarchive.lock")
    if lock is None:
        скажи(объяснение)
        log.close()
        # Не беда: работает другой экземпляр. Пустой итог — «работы не было»,
        # и демон подождёт обычную холостую паузу.
        return SessionSummary()
    скажи(объяснение)

    # Каждый проход заводит свой журнал, и за месяц их набирается под две
    # тысячи. Убираем здесь, под замком прохода, и говорим об этом в журнал:
    # молча исчезающие файлы — то, чего в этой программе быть не должно.
    убрано = убрать_старые_журналы(logs_dir, config.limits.keep_logs_days, кроме=log_path)
    if убрано:
        скажи(_('убрано журналов старше {} суток: {}').format(config.limits.keep_logs_days, убрано))

    try:
        with lock:
            def on_event(event: Event) -> None:
                nonlocal live
                # Отмечаемся на каждом событии: пока выкачка говорит,
                # замок не должен протухнуть под живой работой.
                lock.heartbeat()
                live = apply_event(live, event, now=time.time())
                записать_состояние()
                if event.kind is EventKind.DESTINATION:
                    скажи(_('  качаю {}').format(Path(event.path).name))
                elif event.kind is EventKind.COMPLETED and event.size_bytes:
                    скорость = _(', {:.2f} МБ/с').format(event.speed_bps / 1024**2) if event.speed_bps else ""
                    скажи(_('    готово {:.1f} МБ{}').format(event.size_bytes / 1024**2, скорость))
                elif event.kind is EventKind.ERROR:
                    скажи(_('    отказ: {}').format(event.text[:120]))

            def на_остановку(имя: str, причина: str) -> None:
                nonlocal live
                live = stop_channel(live, причина, now=time.time())
                записать_состояние(force=True)

            def на_канал(имя: str, номер: int, всего: int) -> None:
                nonlocal live
                live = start_channel(live, имя, номер, всего, now=time.time())
                записать_состояние(force=True)

            исключения = load_exclusions(resolve(base, config.paths.excluded), скажи)
            if исключения:
                скажи(_('снято галочками роликов: {}').format(len(исключения)))

            итог = run_session(
                session,
                exclusions=исключения,
                on_event=on_event,
                on_message=скажи,
                on_channel=на_канал,
                should_stop=should_stop,
            )
            скажи(итог.describe(_))
            if config.media_server and not (should_stop is not None and should_stop()):
                # Описания дописываются под тем же замком: иначе их писали бы
                # сразу и проход, и команда `nfo`, запущенная рядом.
                from runner.library import write_nfo

                записано, _не_вышло = write_nfo(base, should_stop=should_stop)
                if записано:
                    скажи(_('дописано описаний для медиасервера: {}').format(записано))
            # Причину остановки и счёт отказов ОСТАВЛЯЕМ: проход кончился,
            # но человеку надо увидеть, почему он кончился так. Обнули мы их —
            # окно показало бы бодрое «не запущена» вместо «истекли куки».
            live = LiveState(
                updated_at=time.time(),
                stopped_reason=live.stopped_reason,
                errors=live.errors,
            )
            записать_состояние(force=True)
            return итог
    finally:
        log.close()


def _сведения(путь: Path) -> FileInfo | None:
    try:
        сведения = путь.stat()
    except OSError:
        return None
    return FileInfo(name=str(путь), modified=сведения.st_mtime, size=сведения.st_size)


def старые_журналы(logs_dir: Path, keep_days: float, кроме: Path | None = None) -> list[FileInfo]:
    файлы = [с for с in map(_сведения, logs_dir.glob("*.log")) if с is not None]
    if кроме is not None:
        файлы = [файл for файл in файлы if Path(файл.name) != кроме]
    return old_logs(файлы, time.time(), keep_days)


def убрать_старые_журналы(logs_dir: Path, keep_days: float, кроме: Path | None = None) -> int:
    """Убрать журналы старше срока. Возвращает, сколько убрано."""
    убрано = 0
    for файл in старые_журналы(logs_dir, keep_days, кроме):
        try:
            Path(файл.name).unlink()
            убрано += 1
        except OSError:
            pass  # не убрался сейчас — уберётся следующим проходом
    return убрано


def _папки_каналов(base: Path) -> list[Path]:
    """Папки с роликами: всё в папке архива, кроме служебного."""
    try:
        return sorted(
            папка for папка in base.iterdir()
            if папка.is_dir() and not папка.name.startswith(("_", "."))
        )
    except OSError:
        return []


def обломки(base: Path, скачано: frozenset[str]) -> list[FileInfo]:
    файлы = []
    for папка in _папки_каналов(base):
        try:
            содержимое = list(папка.iterdir())
        except OSError:
            continue
        for путь in содержимое:
            if путь.is_file() and is_leftover(путь.name):
                сведения = _сведения(путь)
                if сведения is not None:
                    файлы.append(сведения)
    return stale_leftovers(файлы, time.time(), скачано)


def cmd_clean(args) -> int:
    """Показать, что можно убрать; убрать — только с --apply."""
    config, _путь = load_config(Path(args.config))
    base = Path(config.paths.base)
    logs_dir = resolve(base, config.paths.logs)
    archive = resolve(base, config.paths.archive)
    try:
        скачано = parse_archive(archive.read_text(encoding="utf-8")).video_ids
    except OSError:
        скачано = frozenset()

    журналы = старые_журналы(logs_dir, config.limits.keep_logs_days)
    лишнее = обломки(base, скачано)

    print(_('журналов старше {} суток: {} ({:.1f} МБ)').format(
        config.limits.keep_logs_days, len(журналы), total_size(журналы) / 1024**2
    ))
    print(_('обломков загрузок, которые уже не пригодятся: {} ({:.1f} МБ)').format(
        len(лишнее), total_size(лишнее) / 1024**2
    ))
    for файл in лишнее:
        print(f"  {файл.name}")

    if not (журналы or лишнее):
        print(_("Убирать нечего."))
        return 0
    if not args.apply:
        print()
        print(_("Ничего не тронуто. Убрать: ytarchive clean --apply"))
        return 0

    убрано = не_вышло = 0
    for файл in (*журналы, *лишнее):
        try:
            Path(файл.name).unlink()
            убрано += 1
        except OSError as ошибка:
            не_вышло += 1
            print(_('  не убрался {}: {}').format(файл.name, ошибка))
    print(_('убрано файлов: {}').format(убрано))
    return 1 if не_вышло else 0


def cmd_verify(args) -> int:
    """Сверить учёт с диском. Чинит только повторы и только с --apply."""
    config, _путь = load_config(Path(args.config))
    base = Path(config.paths.base)
    archive = resolve(base, config.paths.archive)
    try:
        текст = archive.read_text(encoding="utf-8")
    except FileNotFoundError:
        текст = ""
    except OSError as ошибка:
        print(_('учёт не прочитан: {}').format(ошибка), file=sys.stderr)
        return 1

    имена = []
    for папка in _папки_каналов(base):
        try:
            имена += [f"{папка.name}/{путь.name}" for путь in папка.iterdir() if путь.is_file()]
        except OSError as ошибка:
            print(_('папка {} не прочитана: {}').format(папка, ошибка), file=sys.stderr)

    отчёт = compare(текст, имена)
    print(_('в учёте строк: {}, роликов на диске: {}').format(отчёт.records, отчёт.files))

    def перечень(заголовок: str, строки: list[str]) -> None:
        if not строки:
            return
        print()
        print(заголовок.format(len(строки)))
        for строка in строки[: args.limit]:
            print(f"  {строка}")
        if len(строки) > args.limit:
            print(_('  … и ещё {} (показать все: --limit 0)').format(len(строки) - args.limit))

    if args.limit <= 0:
        args.limit = 10**9
    перечень(
        _("В учёте есть, файла нет — такие ролики заново не скачаются: {}"),
        [f"https://www.youtube.com/watch?v={ролик}" for ролик in отчёт.missing_files],
    )
    перечень(
        _("Файл есть, в учёте нет — такие ролики скачаются второй раз: {}"),
        [имя for _ролик, имя in отчёт.unrecorded],
    )
    перечень(
        _("Один ролик в нескольких файлах: {}"),
        [" + ".join(имена_ролика) for _ролик, имена_ролика in отчёт.twins],
    )
    if отчёт.duplicates:
        print()
        print(_('Повторных строк в учёте: {} (безвредно)').format(отчёт.extra_lines))

    if отчёт.clean:
        print(_("Учёт и диск сходятся."))
        return 0

    if not args.apply:
        if отчёт.duplicates:
            print()
            print(_("Ничего не тронуто. Убрать повторные строки: ytarchive verify --apply"))
        # Одни повторы — не расхождение: учёт и диск согласны, в файле лишь
        # лишние строки. Код возврата говорит о том, что требует человека.
        return 1 if (отчёт.missing_files or отчёт.unrecorded or отчёт.twins) else 0

    if not отчёт.duplicates:
        print()
        print(_("Чинить нечего: остальное — решение человека, а не программы."))
        return 1

    # Учёт дописывает yt-dlp прямо во время выкачки. Перезаписать файл под
    # ним значит потерять строки, которые он допишет в старый.
    lock, объяснение = acquire(archive.parent / "ytarchive.lock")
    if lock is None:
        print(_('идёт выкачка — учёт сейчас править нельзя ({})').format(объяснение), file=sys.stderr)
        return 1
    with lock:
        копия = archive.with_name(f"{archive.name}.{datetime.now():%Y%m%d-%H%M%S}.bak")
        try:
            копия.write_text(текст, encoding="utf-8", newline="\n")
            archive.write_text(without_duplicates(текст), encoding="utf-8", newline="\n")
        except OSError as ошибка:
            print(_('учёт не записан: {}').format(ошибка), file=sys.stderr)
            return 1
    print(_('убрано повторных строк: {}; прежний учёт сохранён как {}').format(отчёт.extra_lines, копия.name))
    return 0


def cmd_nfo(args) -> int:
    """Описания для медиасервера: показать, чего не хватает; записать — с --apply."""
    from runner.library import nfo_todo, write_nfo

    config, _путь = load_config(Path(args.config))
    base = Path(config.paths.base)
    роликам, каналам = nfo_todo(base)
    print(_('роликов без описания: {}; каналов без описания: {}').format(len(роликам), len(каналам)))
    if not (роликам or каналам):
        print(_("Описания есть у всего."))
        return 0
    if not args.apply:
        print()
        print(_("Ничего не записано. Записать: ytarchive nfo --apply"))
        print(_("Существующие описания не трогаются. На большом архиве это минуты: из каждого ролика читается его описание."))
        return 0

    def ход(номер: int, всего: int) -> None:
        if номер == 1 or номер % 50 == 0 or номер == всего:
            print(f"  {номер} / {всего}", flush=True)

    записано, не_вышло = write_nfo(base, on_progress=ход)
    print(_('записано описаний: {}').format(записано))
    if не_вышло:
        print(_('не записалось: {}').format(не_вышло))
    return 1 if не_вышло else 0


def cmd_update(args) -> int:
    """Обновить yt-dlp тем способом, каким он был поставлен."""
    import shutil
    import subprocess

    найден = shutil.which("yt-dlp")
    команда = update_command(найден, str(Path(sys.executable).parent), sys.executable)
    if not команда:
        from runner.preflight import чего_не_хватает

        for нехватка in чего_не_хватает():
            if нехватка.чего == "yt-dlp":
                print(f"  {нехватка}")
        return 1

    # Из окна команда идёт без консоли, а yt-dlp — консольная программа:
    # без этого флага на каждый его запуск мигало бы чёрное окно.
    без_окна = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}

    def версия() -> str:
        try:
            ответ = subprocess.run(
                [найден, "--version"], capture_output=True, text=True, errors="replace",
                timeout=60, **без_окна,
            )
        except (OSError, subprocess.SubprocessError):
            return "?"
        return ответ.stdout.strip() or "?"

    было = версия()
    print(_('yt-dlp {} — {}').format(было, найден))
    print("> " + " ".join(команда), flush=True)
    try:
        # Вывод забираем и печатаем сами. Унаследованным он терялся, когда
        # команду звало окно: там нет консоли, и ответ yt-dlp «я поставлен
        # через pip, обновляйте им» — самое важное здесь — уходил в никуда.
        ответ = subprocess.run(
            list(команда), capture_output=True, text=True, encoding="utf-8",
            errors="replace", stdin=subprocess.DEVNULL, **без_окна,
        )
    except OSError as ошибка:
        print(str(ошибка), file=sys.stderr)
        return 1
    for кусок in (ответ.stdout, ответ.stderr):
        if кусок.strip():
            print(кусок.strip())
    код = ответ.returncode
    стало = версия()
    if стало != было:
        print(_('обновлён: {} → {}').format(было, стало))
    elif код == 0:
        print(_('уже последняя версия: {}').format(стало))
    elif команда[-1] == "-U":
        # yt-dlp отказался обновлять себя сам — значит, ставили его пакетным
        # менеджером или pip, и он сам назвал чем. Повторяем это по-человечески.
        print(_("yt-dlp поставлен не этой программой — обновите его тем же способом, каким ставили."))
    return код


def cmd_run(args) -> int:
    config, _путь = load_config(Path(args.config))
    base = Path(config.paths.base)
    итог = один_проход(config, base, build_session(config, base))
    return 1 if итог.needs_human else 0


def _дописать_в_журнал(logs_dir: Path, строка: str) -> None:
    """Дописать строку в самый свежий журнал.

    Своего журнала у демона нет намеренно: заведи он отдельный, окно читало
    бы один файл, а половина событий лежала бы в другом.
    """
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        журналы = sorted(logs_dir.glob("*.log"))
        путь = журналы[-1] if журналы else logs_dir / f"{datetime.now():%Y-%m-%d_%H%M}.log"
        with путь.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(строка + "\n")
    except OSError:
        pass  # журнал — не повод останавливать выкачку


def cmd_daemon(args) -> int:
    """Непрерывная работа своими силами: цикл проходов вместо планировщика."""
    config, _путь = load_config(Path(args.config))
    base = Path(config.paths.base)
    session = build_session(config, base)
    tools = resolve(base, config.paths.archive).parent

    logs_dir = resolve(base, config.paths.logs)
    #: Причина, о которой уже сказано в Telegram. Живёт, пока жив обход.
    сказано = ""

    def проход(should_stop):
        nonlocal сказано
        итог = один_проход(config, base, session, should_stop=should_stop)
        # Пустой итог — прохода не было (замок занят другим экземпляром).
        # По нему нельзя судить ни о беде, ни о том, что она прошла.
        if config.notify.enabled and итог.results:
            сказано = уведомить(config, итог, сказано, скажи)
        return итог

    def скажи(текст: str) -> None:
        строка = f"{datetime.now():%H:%M:%S}  {текст}"
        if sys.stdout is not None:
            try:
                print(строка, flush=True)
            except (OSError, ValueError):
                pass
        # И в журнал: между проходами своего журнала нет, а окно читает
        # именно его. Без этого «жду следующего прохода» видно только тому,
        # кто смотрит в консоль, — то есть никому.
        _дописать_в_журнал(logs_dir, строка)

    сделано = run_forever(
        проход,
        tools_dir=tools,
        rhythm=config.rhythm,
        hours=config.hours,
        on_message=скажи,
        passes=args.passes,
    )
    return 0 if сделано or args.passes == 0 else 1


def уведомить(config: Config, итог: SessionSummary, сказано: str, скажи) -> str:
    """Сказать в Telegram о новой беде или о том, что она прошла.

    Возвращает причину, о которой теперь сказано. Если отправить не вышло,
    считаем, что не сказано: попробуем после следующего прохода, а не
    промолчим навсегда.
    """
    from core.notify import Change, judge_change
    from runner.notify import send

    причина = итог.stopped[0].stopped_reason if итог.stopped else ""
    перемена = judge_change(сказано, причина)
    if перемена == Change.NOTHING:
        return сказано
    if перемена == Change.TROUBLE:
        текст = _('Архив YouTube: выкачка остановлена — {}').format(_(причина))
    else:
        текст = _("Архив YouTube: выкачка снова работает")
    получилось, объяснение = send(config.notify, текст)
    if получилось:
        скажи(_("сообщение в Telegram отправлено"))
        return причина
    скажи(_('сообщение в Telegram не ушло: {}').format(объяснение))
    return сказано


def cmd_notify(args) -> int:
    """Проверить уведомления: послать пробное сообщение и сказать, что вышло."""
    from runner.notify import send

    config, _путь = load_config(Path(args.config))
    if not config.notify.enabled:
        print(_("Уведомления не настроены: в разделе [notify] нужны telegram_token_file и telegram_chat."))
        return 1
    получилось, объяснение = send(config.notify, _("Архив YouTube: проверка уведомлений. Если вы это читаете — всё настроено."))
    if получилось:
        print(_("Пробное сообщение отправлено — проверьте Telegram."))
        return 0
    print(_('Не отправилось: {}').format(объяснение))
    return 1


def cmd_stop(args) -> int:
    """Попросить работающий демон остановиться."""
    config, _путь = load_config(Path(args.config))
    tools = resolve(Path(config.paths.base), config.paths.archive).parent
    if not daemon_running(tools):
        print(_("никто не работает"))
        return 0
    ask_stop(tools)
    print(_("попросил остановиться — демон уйдёт, договорив текущий ролик"))
    return 0


def первый_запуск(путь: Path) -> int:
    """Спросить язык и рабочую папку, когда настроек ещё нет.

    Иначе программа, скачанная из репозитория, встречает человека отказом
    «нет файла настроек» и советом сходить в командную строку. Для того,
    кто пришёл за окном, это тупик.
    """
    try:
        from PySide6.QtWidgets import QApplication

        from gui.firstrun import настройки_для, спросить
    except ImportError as error:
        from runner.preflight import как_поставить_qt

        print(_('окно требует PySide6, а его нет: {}').format(error), file=sys.stderr)
        print(_('поставить:  {}').format(как_поставить_qt()), file=sys.stderr)
        return 2

    from core.i18n import СИСТЕМНЫЙ
    from runner.language import настроить

    # До первого разговора языка ещё нет — берём у системы.
    настроить(СИСТЕМНЫЙ)
    QApplication.instance() or QApplication(sys.argv)

    ответ = спросить()
    if ответ is None:
        print(_("настройки не созданы — запустите ещё раз, когда решите, куда качать"))
        return 0  # отказ это право человека, а не беда

    папка, язык = ответ
    try:
        папка.mkdir(parents=True, exist_ok=True)
        путь.write_text(настройки_для(папка, язык), encoding="utf-8", newline="\n")
    except OSError as ошибка:
        print(_('настройки не записались: {}').format(ошибка), file=sys.stderr)
        return 1

    print(_('создан {}: архив в {}').format(путь, папка))
    return 0


def cmd_gui(args) -> int:
    """Окно наблюдения. Qt подтягивается только здесь: командная строка
    и фоновое задание не должны требовать его установки."""
    путь = Path(args.config)
    if not путь.exists():
        код = первый_запуск(путь)
        if код != 0 or not путь.exists():
            return код

    config, _путь = load_config(путь)
    base = Path(config.paths.base)
    archive = resolve(base, config.paths.archive)
    session = build_session(config, base)

    # Язык выбирается ДО постройки окна: надписи берутся при создании
    # виджетов, и опоздав, мы получили бы наполовину переведённое окно.
    from runner.language import настроить

    настроить(config.language)

    try:
        from gui.source import ArchiveSource
        from gui.window import run
    except ImportError as error:
        from runner.preflight import как_поставить_qt

        print(_('окно требует PySide6, а его нет: {}').format(error), file=sys.stderr)
        print(_('поставить:  {}').format(как_поставить_qt()), file=sys.stderr)
        return 2

    source = ArchiveSource(
        base=base,
        archive_path=archive,
        logs_dir=resolve(base, config.paths.logs),
        lock_path=archive.parent / "ytarchive.lock",
        channels_path=resolve(base, config.paths.channels),
        excluded_path=resolve(base, config.paths.excluded),
        config_path=путь,
        live_path=archive.parent / "ytarchive-live.json",
        settings=session.settings,
        ytdlp=session.ytdlp,
    )
    return run(source, selftest=args.selftest)


def выбрать_язык(argv: list[str] | None) -> None:
    """Выбрать язык до всего остального.

    До того, как строится разбор доводов: подсказки к командам берутся
    в момент построения, и опоздав, мы получили бы русскую справку при
    английских настройках.

    Путь к настройкам ищем в доводах руками — разбора ещё нет. Настроек
    может не быть вовсе (первый запуск), и тогда берём язык у системы.
    """
    from core.i18n import СИСТЕМНЫЙ
    from runner.language import настроить

    доводы = list(sys.argv[1:] if argv is None else argv)
    путь = Path(CONFIG_NAME)
    for номер, довод in enumerate(доводы):
        if довод == "--config" and номер + 1 < len(доводы):
            путь = Path(доводы[номер + 1])
        elif довод.startswith("--config="):
            путь = Path(довод.split("=", 1)[1])

    try:
        config, _файл = load_config(путь)
    except ConfigError:
        настроить(СИСТЕМНЫЙ)
        return
    настроить(config.language)


def main(argv: list[str] | None = None) -> int:
    выбрать_язык(argv)
    parser = argparse.ArgumentParser(prog="ytarchive", description=__doc__)
    parser.add_argument("--config", default=CONFIG_NAME, help=_('файл настроек (по умолчанию {})').format(CONFIG_NAME))
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help=_("создать образец настроек"))
    p_init.add_argument("--force", action="store_true", help=_("перезаписать существующий"))
    p_init.add_argument("--dry-run", action="store_true", help=_("показать, но не создавать"))
    p_init.set_defaults(func=cmd_init)

    sub.add_parser("plan", help=_("что будет скачано, без изменений")).set_defaults(func=cmd_plan)
    sub.add_parser("check", help=_("достучаться до каналов")).set_defaults(func=cmd_check)
    sub.add_parser("run", help=_("качать — один проход и выход")).set_defaults(func=cmd_run)

    p_daemon = sub.add_parser("daemon", help=_("качать непрерывно, без планировщика задач"))
    p_daemon.add_argument(
        "--passes", type=int, default=None,
        help=_("сделать столько проходов и выйти (по умолчанию — пока не остановят)"),
    )
    p_daemon.set_defaults(func=cmd_daemon)

    sub.add_parser("stop", help=_("попросить работающий экземпляр остановиться")).set_defaults(
        func=cmd_stop
    )

    p_verify = sub.add_parser("verify", help=_("сверить учёт с файлами на диске"))
    p_verify.add_argument("--apply", action="store_true", help=_("убрать повторные строки учёта"))
    p_verify.add_argument("--limit", type=int, default=20, help=_("сколько строк каждого перечня показать (0 — все)"))
    p_verify.set_defaults(func=cmd_verify)

    p_clean = sub.add_parser("clean", help=_("старые журналы и обломки загрузок"))
    p_clean.add_argument("--apply", action="store_true", help=_("убрать, а не только показать"))
    p_clean.set_defaults(func=cmd_clean)

    sub.add_parser("update", help=_("обновить yt-dlp")).set_defaults(func=cmd_update)

    sub.add_parser("notify", help=_("проверить уведомления в Telegram")).set_defaults(func=cmd_notify)

    p_nfo = sub.add_parser("nfo", help=_("описания для медиасервера"))
    p_nfo.add_argument("--apply", action="store_true", help=_("записать, а не только посчитать"))
    p_nfo.set_defaults(func=cmd_nfo)

    p_gui = sub.add_parser("gui", help=_("окно наблюдения"))
    p_gui.add_argument("--selftest", action="store_true",
                       help=_("построить окно и выйти — для сборки"))
    p_gui.set_defaults(func=cmd_gui)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as error:
        print(_('настройки: {}').format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
