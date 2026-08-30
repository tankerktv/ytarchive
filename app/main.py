"""Точка входа.

Режимы разведены намеренно: `plan` только считает и печатает, `run` качает.
Правило «сначала вхолостую, потом на живом» здесь буквальное — команда,
меняющая данные, называется отдельным словом, а не флагом к обычной.

    ytarchive init            создать настройки рядом с собой
    ytarchive check           достучаться до каналов, ничего не качая
    ytarchive plan            что будет скачано и сколько это займёт
    ytarchive run             качать
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import replace
from pathlib import Path

from core.archive import parse_archive
from core.channels import parse_channels
from core.config import DEFAULT_CONFIG_TEXT, Config, ConfigError, parse_config
from core.planner import estimate_range
from core.progress import Event, EventKind
from core.supervisor import WatchdogPolicy
from core.ytdlp_args import DownloadSettings
from runner.session import SessionConfig, probe_channel, run_session

CONFIG_NAME = "ytarchive.toml"


def resolve(base: Path, value: str) -> Path:
    """Пути в настройках считаются от base, если не заданы абсолютными."""
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_config(path: Path) -> tuple[Config, Path]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(
            f"нет файла настроек {path}. Создать образец: ytarchive init"
        ) from None
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"{path}: не разбирается как TOML — {error}") from None
    return parse_config(data), path


def build_session(config: Config, base: Path) -> SessionConfig:
    archive = resolve(base, config.paths.archive)
    cookies = resolve(base, config.paths.cookies)
    settings = DownloadSettings(
        archive_path=str(archive),
        output_template=str(base / "%(channel)s" / "%(upload_date>%Y-%m-%d)s - %(title).150B [%(id)s].%(ext)s"),
        cookies_file=str(cookies) if cookies.exists() else None,
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
    )


def cmd_init(args) -> int:
    target = Path(args.config)
    if target.exists() and not args.force:
        print(f"{target} уже есть. Перезаписать: --force", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"создал бы {target}:\n")
        print(DEFAULT_CONFIG_TEXT)
        return 0
    target.write_text(DEFAULT_CONFIG_TEXT, encoding="utf-8", newline="\n")
    print(f"создан {target} — поправьте пути и запустите: ytarchive check")
    return 0


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

    print(f"настройки:  {path}")
    print(f"архив:      {base}")
    print(f"каналов:    {len(parsed.channels)}")
    for problem in parsed.problems:
        print(f"  строка {problem.line_number} пропущена: {problem.reason}")
    print(f"уже скачано: {len(archive)} роликов")
    if archive.unreadable:
        print(f"  непонятных строк в архиве: {len(archive.unreadable)}")
    print(f"качество:   до {config.height}p" + (", предпочтение AV1" if config.prefer_av1 else ""))
    print(f"куки:       {session.settings.cookies_file or 'не заданы — YouTube откажет'}")
    print()
    print("Сколько займёт час материала при измеренных битрейтах:")
    низ, верх = estimate_range(3600)
    print(f"  {низ / 1024**3:.2f}–{верх / 1024**3:.2f} ГБ")
    print()
    print("Ничего не скачано и не изменено. Качать: ytarchive run")
    return 0


def cmd_check(args) -> int:
    config, _ = load_config(Path(args.config))
    base = Path(config.paths.base)
    session = build_session(config, base)
    parsed, _ = _state(session)

    плохих = 0
    for channel in parsed.channels:
        решение = probe_channel(channel, session, sleep=lambda _: None)
        if решение is None or решение.needs_human:
            причина = решение.reason if решение else "проверка не дала ответа"
            print(f"  {channel.name}: ОТКАЗ — {причина}")
            плохих += 1
        else:
            print(f"  {channel.name}: доступ есть")
    print()
    print("все каналы отвечают" if not плохих else f"каналов с бедой: {плохих}")
    return 1 if плохих else 0


def cmd_run(args) -> int:
    config, _ = load_config(Path(args.config))
    base = Path(config.paths.base)
    session = build_session(config, base)

    def on_event(event: Event) -> None:
        if event.kind is EventKind.DESTINATION:
            print(f"  качаю {Path(event.path).name}")
        elif event.kind is EventKind.COMPLETED and event.size_bytes:
            скорость = f", {event.speed_bps / 1024**2:.2f} МБ/с" if event.speed_bps else ""
            print(f"    готово {event.size_bytes / 1024**2:.1f} МБ{скорость}")
        elif event.kind is EventKind.ERROR:
            print(f"    отказ: {event.text[:120]}")

    итог = run_session(session, on_event=on_event, on_message=lambda m: print(m))
    print()
    print(итог.describe())
    return 1 if итог.needs_human else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ytarchive", description=__doc__)
    parser.add_argument("--config", default=CONFIG_NAME, help=f"файл настроек (по умолчанию {CONFIG_NAME})")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="создать образец настроек")
    p_init.add_argument("--force", action="store_true", help="перезаписать существующий")
    p_init.add_argument("--dry-run", action="store_true", help="показать, но не создавать")
    p_init.set_defaults(func=cmd_init)

    sub.add_parser("plan", help="что будет скачано, без изменений").set_defaults(func=cmd_plan)
    sub.add_parser("check", help="достучаться до каналов").set_defaults(func=cmd_check)
    sub.add_parser("run", help="качать").set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as error:
        print(f"настройки: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
