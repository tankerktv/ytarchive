"""Откуда окно берёт данные и как управляет заданием.

Отделено от окна намеренно: в тестах сюда подставляется поддельный источник,
и окно проверяется без файлов, без планировщика и без выкачки.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from core.locking import LockState, judge_lock
from runner.lockfile import STALE_AFTER, pid_alive, read_lock

#: Имя задания в планировщике. Менять только вместе с самим заданием.
TASK_NAME = "YouTube архив (непрерывная выкачка)"


@dataclass
class ArchiveSource:
    """Настоящий источник: файлы архива и задание планировщика."""

    base: Path
    archive_path: Path
    logs_dir: Path
    lock_path: Path
    channels_path: Path
    config_path: Path
    live_path: Path
    #: Снятые галочки. Не задан — кладём рядом со списком каналов, чтобы
    #: пришедший править файлы руками нашёл оба в одном месте.
    excluded_path: Path | None = None
    #: Нужны поиску: откуда брать куки и чем звать yt-dlp.
    settings: object | None = None
    ytdlp: tuple[str, ...] = ("yt-dlp",)
    task_name: str = TASK_NAME

    def avatar(self, channel_name: str):
        """Логотип канала из кэша. В сеть не ходим — это зовётся из отрисовки,
        а она случается каждые две секунды."""
        from core.channels import parse_channels
        from runner.avatars import cached_avatar

        for канал in parse_channels(self.channels_text()).channels:
            if канал.name == channel_name:
                опознание = канал.url.rstrip("/").split("/")
                for кусок in опознание:
                    if кусок.startswith("UC") and len(кусок) == 24:
                        return cached_avatar(self.avatars_dir, кусок)
                return cached_avatar(self.avatars_dir, channel_name)
        return None

    @property
    def avatars_dir(self) -> Path:
        return self.channels_path.parent / "avatars"

    def free_bytes(self) -> int:
        """Сколько места на диске архива. Ноль значит «не смогли узнать» —
        и тогда лучше не утверждать, что канал влезет."""
        import shutil

        try:
            return shutil.disk_usage(self.base).free
        except OSError:
            return 0

    def add_channel(self, name: str, url: str) -> str:
        """Добавить канал в список, не потеряв остальных."""
        from core.channels import Channel, format_channels, parse_channels

        разбор = parse_channels(self.channels_text())
        if any(c.name == name for c in разбор.channels):
            return f"«{name}» уже в списке"
        if разбор.problems:
            # Не переписываем файл, в котором есть непонятое: перезапись
            # потеряла бы эти строки молча.
            return "в списке есть непонятые строки — сначала поправьте их"
        стало = (*разбор.channels, Channel(name=name, url=url))
        ответ = self.write_channels(format_channels(стало))
        return f"{ответ}: добавлен «{name}»" if "сохранён" in ответ else ответ

    def log_tail(self, lines: int) -> list[str]:
        """Хвост самого свежего журнала.

        Отсутствие журналов — не беда: выкачка могла просто ни разу
        не запускаться. Возвращаем пустоту, а не жалобу.
        """
        try:
            журналы = sorted(
                self.logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True
            )
        except OSError:
            return []
        if not журналы:
            return []
        try:
            текст = журналы[0].read_text(encoding="utf-8", errors="replace")
        except OSError as ошибка:
            return [f"журнал не читается: {ошибка}"]
        return текст.splitlines()[-lines:]

    def archive_text(self) -> str:
        try:
            return self.archive_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def channels_text(self) -> str:
        try:
            return self.channels_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def write_channels(self, text: str) -> str:
        """Записать список каналов. Сначала копия — файл правит человек,
        и потерять его из-за нашей ошибки нельзя."""
        return self._write(self.channels_path, text, "список каналов сохранён")

    # --- снятые галочки -----------------------------------------------------

    @property
    def excluded_file(self) -> Path:
        return self.excluded_path or (self.channels_path.parent / "excluded.txt")

    def exclusions(self):
        """Прочитать снятые галочки. Нет файла — значит их не снимали."""
        from core.exclusions import Exclusions, parse_exclusions

        try:
            return parse_exclusions(self.excluded_file.read_text(encoding="utf-8"))
        except OSError:
            return Exclusions()

    def write_exclusions(self, video_ids) -> str:
        """Записать снятые галочки.

        Пишем весь список целиком, а не правим построчно: окно знает полную
        картину, и дописывание по одному рано или поздно разойдётся с ней.
        """
        from core.exclusions import format_exclusions

        return self._write(
            self.excluded_file, format_exclusions(set(video_ids)), "выбор сохранён"
        )

    @property
    def thumbs_dir(self) -> Path:
        return self.channels_path.parent / "thumbs"

    def listing(self, channel_name: str, should_stop=None):
        """Переписать канал: идентификаторы, названия, длительности.

        Ходит в сеть — звать только из отдельного потока, иначе окно замрёт
        на те секунды, что yt-dlp обходит шестьсот роликов.

        `should_stop` обязателен для окна: закрытое окно должно уметь
        прекратить перепись, а не ждать её минуту.
        """
        from core.channels import parse_channels
        from core.videos import Listing
        from runner.session import SessionConfig, enumerate_channel

        if self.settings is None:
            return Listing()
        for канал in parse_channels(self.channels_text()).channels:
            if канал.name == channel_name:
                config = SessionConfig(
                    base_dir=self.base,
                    channels_file=self.channels_path,
                    settings=self.settings,
                    ytdlp=self.ytdlp,
                )
                return enumerate_channel(канал, config, should_stop=should_stop)
        return Listing()

    def config_text(self) -> str:
        try:
            return self.config_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def write_config(self, text: str) -> str:
        return self._write(self.config_path, text, "настройки сохранены — вступят в силу со следующего прохода")

    def _write(self, path: Path, text: str, успех: str) -> str:
        try:
            if path.exists():
                path.with_suffix(path.suffix + ".bak").write_text(
                    path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
                )
            path.write_text(text, encoding="utf-8", newline="\n")
        except OSError as ошибка:
            return f"не сохранилось: {ошибка}"
        return успех

    def channel_stats(self) -> list[tuple[str, int, int]]:
        """Сколько файлов и байт лежит в папке каждого канала.

        Считаем по файлам, а не по переписи YouTube: перепись требует сети
        и занимает минуты, а окно должно отвечать сразу.
        """
        итог: list[tuple[str, int, int]] = []
        try:
            папки = sorted(p for p in self.base.iterdir() if p.is_dir())
        except OSError:
            return итог
        for папка in папки:
            if папка.name.startswith("_"):
                continue  # служебные: _tools, _logs
            файлов = байт = 0
            for файл in папка.rglob("*"):
                if файл.suffix.lower() in (".mkv", ".mp4", ".webm"):
                    файлов += 1
                    try:
                        байт += файл.stat().st_size
                    except OSError:
                        pass
            итог.append((папка.name, файлов, байт))
        return итог

    def live_state(self):
        """Живое состояние выкачки. Отсутствие файла — не беда: выкачка
        могла ещё не запускаться."""
        from core.livestate import from_text

        try:
            return from_text(self.live_path.read_text(encoding="utf-8"))
        except OSError:
            return None

    def download_running(self) -> bool:
        """Идёт ли выкачка.

        Смотрим на замок, а не на свежесть журнала: журнал разрежен, и
        двухчасовой ролик выглядел бы в нём как многочасовой простой.
        Протухший замок считается свободным — его хозяин молчит слишком долго.
        """
        info = read_lock(self.lock_path)
        state = judge_lock(
            info,
            now=time.time(),
            pid_alive=pid_alive(info.pid) if info else False,
            stale_after=STALE_AFTER,
        )
        return state is LockState.HELD

    def start(self) -> str:
        return self._schtasks("/Run", "запустил задание")

    def stop(self) -> str:
        return self._schtasks("/End", "остановил задание")

    def _schtasks(self, ключ: str, успех: str) -> str:
        try:
            итог = subprocess.run(
                ["schtasks", ключ, "/TN", self.task_name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                # Иначе кнопка в окне мигает консолью.
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired) as ошибка:
            return f"не вышло: {ошибка}"
        if итог.returncode != 0:
            # Показываем ответ планировщика как есть: свои формулировки тут
            # только запутают, а его текст можно поискать в сети.
            return f"планировщик отказал: {(итог.stderr or итог.stdout).strip()[:200]}"
        return успех
