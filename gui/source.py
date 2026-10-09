"""Откуда окно берёт данные и как заводит выкачку.

Отделено от окна намеренно: в тестах сюда подставляется поддельный источник,
и окно проверяется без файлов, без процессов и без выкачки.
"""

from __future__ import annotations

import itertools
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from core.locking import LockState, judge_lock
from runner.lockfile import STALE_AFTER, pid_alive, read_lock
from runner.language import _


@dataclass(frozen=True)
class Записано:
    """Чем кончилась попытка записи: признаком, а не текстом.

    Раньше успех отличали по началу сообщения — `startswith("не сохранилось")`.
    Пока сообщение было одно на всех, это работало. С переводом интерфейса
    сломалось бы молча и худшим образом: текст на другом языке под проверку
    не подходит, и окно решило бы, что несохранённое сохранено.
    """

    ok: bool
    text: str

    def __str__(self) -> str:  # чтобы годилось прямо в setText
        return self.text


def доступна_запись(путь: Path) -> bool:
    """Проверяем записью, а не правами: на сетевых дисках и в OneDrive
    права говорят одно, а запись кончается отказом."""
    проба = путь / ".ytarchive-проба"
    try:
        проба.write_text("", encoding="utf-8")
    except OSError:
        return False
    try:
        проба.unlink()
    except OSError:
        pass
    return True


def осмотреть_папку(path: Path, *, учёт: str, нынешняя: Path | None = None):
    """Годится ли папка под архив и чем грозит.

    Свободной функцией, а не методом источника: у мастера первого запуска
    источника ещё нет — настроек, из которых его собрать, тоже.

    Факты собираются здесь, решение принимает `core.workdir` — так его можно
    проверить без дисков и без прав.
    """
    from core.archive import parse_archive
    from core.workdir import judge_folder

    путь = Path(path)
    существует = путь.exists()
    каталог = путь.is_dir() if существует else False

    файл_учёта = (путь / учёт) if учёт else None
    есть_учёт = bool(файл_учёта and файл_учёта.is_file())
    сколько = 0
    if есть_учёт:
        try:
            сколько = len(parse_archive(файл_учёта.read_text(encoding="utf-8")).video_ids)
        except OSError:
            есть_учёт = False

    внутри = 0
    if каталог:
        try:
            # Считать всё дерево незачем: хватает знания «пусто или нет».
            внутри = sum(1 for _файл in itertools.islice(путь.iterdir(), 1))
        except OSError:
            внутри = 0

    та_же = False
    if каталог and нынешняя is not None:
        try:
            та_же = путь.resolve() == Path(нынешняя).resolve()
        except OSError:
            та_же = False

    return judge_folder(
        exists=существует,
        is_dir=каталог,
        writable=доступна_запись(путь) if каталог else False,
        has_archive=есть_учёт,
        archive_count=сколько,
        files_inside=внутри,
        same_as_now=та_же,
    )


#: Сколько секунд верить сохранённому счёту файлов, если архив не менялся.
STATS_TTL = 60.0


@dataclass
class ArchiveSource:
    """Настоящий источник: файлы архива и отдельный процесс выкачки."""

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
            return _('«{}» уже в списке').format(name)
        if разбор.problems:
            # Не переписываем файл, в котором есть непонятое: перезапись
            # потеряла бы эти строки молча.
            return _("в списке есть непонятые строки — сначала поправьте их")
        # Новую строку проверяем тем же разбором, что и файл. Иначе канал с
        # двоеточием в названии записался бы, при чтении оказался «непонятой
        # строкой», и окно отказалось бы править список вовсе.
        проба = parse_channels(format_channels((Channel(name=name, url=url),)))
        if проба.problems:
            return _('не добавлен: {}').format(проба.problems[0].reason)
        стало = (*разбор.channels, проба.channels[0])
        ответ = self.write_channels(format_channels(стало))
        return _('{}: добавлен «{}»').format(ответ, name) if ответ.ok else ответ.text

    def has_cookies(self) -> bool:
        """Есть ли откуда взять вход в YouTube: файл на месте или выбран браузер.

        Читаем настройки заново, а не помним с запуска: человек кладёт файл,
        глядя на подсказку, и она должна исчезнуть сама. Не смогли понять —
        считаем, что есть: ложная подсказка хуже отсутствующей.
        """
        from core.config import loads, parse_config

        try:
            config = parse_config(loads(self.config_text()))
        except Exception:  # noqa: BLE001 — о битых настройках скажет вкладка настроек
            return True
        if config.cookies_browser:
            return True
        путь = Path(config.paths.cookies)
        return (путь if путь.is_absolute() else Path(config.paths.base) / путь).exists()

    def file_dates(self, channel_name: str) -> dict[str, str]:
        """Точные даты скачанных роликов канала: идентификатор → ГГГГММДД.

        Берутся из имён файлов — туда их пишет yt-dlp при загрузке. Перепись
        отдаёт дату лишь примерно, а здесь она настоящая.
        """
        from core.videos import date_from_filename

        итог: dict[str, str] = {}
        try:
            имена = [путь.name for путь in (self.base / channel_name).iterdir()]
        except OSError:
            return итог  # папки ещё нет — канал ни разу не качался
        for имя in имена:
            найдено = date_from_filename(имя)
            if найдено is not None:
                итог.setdefault(*найдено)
        return итог

    def set_rules(self, index: int, rules) -> Записано:
        """Задать каналу правила отбора."""
        from core.channels import format_channels, parse_channels, set_rules

        разбор = parse_channels(self.channels_text())
        if разбор.problems:
            return Записано(False, _("в списке есть непонятые строки — сначала поправьте их"))
        if not 0 <= index < len(разбор.channels):
            return Записано(False, _("такого канала в списке нет"))
        return self.write_channels(format_channels(set_rules(разбор.channels, index, rules)))

    def rename_channel(self, index: int, new_name: str) -> Записано:
        """Переименовать канал вместе с его папкой.

        Именно вместе. Имя канала задаёт папку, и переименование одного только
        имени раскололо бы архив: новое пошло бы в новую папку, старое осталось
        бы в прежней. Ровно это уже случалось, когда имя папки брали у YouTube.
        """
        from core.channels import (
            FolderMove,
            RenameVerdict,
            check_rename,
            format_channels,
            judge_folder_rename,
            parse_channels,
            rename_channel,
        )

        # Идущий проход держит прежнее имя в памяти: переименуй мы папку сейчас,
        # он завёл бы старую заново и доложил остаток канала туда.
        if self.download_running():
            return Записано(
                False, _("идёт проход выкачки — дождитесь его конца или остановите выкачку")
            )

        разбор = parse_channels(self.channels_text())
        if разбор.problems:
            return Записано(False, _("в списке есть непонятые строки — сначала поправьте их"))

        отказы = {
            RenameVerdict.NO_SUCH: _("такого канала в списке нет"),
            RenameVerdict.EMPTY: _("название не может быть пустым"),
            RenameVerdict.FORBIDDEN: _("в названии есть символы, недопустимые в имени папки"),
            RenameVerdict.SAME: _("название то же самое"),
            RenameVerdict.DUPLICATE: _("канал с таким названием уже есть"),
        }
        приговор = check_rename(разбор.channels, index, new_name)
        if приговор is not RenameVerdict.OK:
            return Записано(False, отказы[приговор])

        старое = разбор.channels[index].name
        новое = new_name.strip()
        откуда, куда = self.base / старое, self.base / новое
        ход = judge_folder_rename(
            old_exists=откуда.is_dir(),
            new_exists=куда.exists(),
            same_folder=старое.casefold() == новое.casefold(),
        )
        if ход is FolderMove.CONFLICT:
            return Записано(
                False,
                _("папка «{}» уже есть — сливать две папки молча нельзя").format(новое),
            )

        # Сначала папка, потом список. Наоборот было бы хуже: список уже говорит
        # новое имя, папка не переименовалась — и следующий проход начнёт
        # складывать ролики в пустую новую папку.
        if ход is FolderMove.MOVE:
            try:
                откуда.rename(куда)
            except OSError as ошибка:
                return Записано(False, _("папку переименовать не вышло: {}").format(ошибка))

        self.forget_stats()
        ответ = self.write_channels(format_channels(rename_channel(разбор.channels, index, новое)))
        if not ответ.ok:
            # Список не записался — возвращаем папку, иначе имя и папка разойдутся.
            if ход is FolderMove.MOVE:
                try:
                    куда.rename(откуда)
                except OSError:
                    pass
            return ответ
        return Записано(True, _("канал переименован: «{}» → «{}»").format(старое, новое))

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
            return [_('журнал не читается: {}').format(ошибка)]
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

    def write_channels(self, text: str) -> Записано:
        """Записать список каналов. Сначала копия — файл правит человек,
        и потерять его из-за нашей ошибки нельзя."""
        return self._write(self.channels_path, text, _("список каналов сохранён"))

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

    def write_exclusions(self, video_ids) -> Записано:
        """Записать снятые галочки.

        Пишем весь список целиком, а не правим построчно: окно знает полную
        картину, и дописывание по одному рано или поздно разойдётся с ней.
        """
        from core.exclusions import format_exclusions

        return self._write(
            self.excluded_file, format_exclusions(set(video_ids)), _("выбор сохранён")
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

    # --- рабочая папка ------------------------------------------------------

    @property
    def archive_relative(self) -> str:
        """Где лежит учёт внутри рабочей папки — например `_tools/downloaded.txt`.

        Нужно, чтобы предсказать судьбу учёта в ДРУГОЙ папке, ещё не став ею.
        """
        try:
            return self.archive_path.relative_to(self.base).as_posix()
        except ValueError:
            # Учёт вынесен наружу рабочей папки — законно, и тогда смена
            # папки его не касается.
            return ""

    def check_folder(self, path: Path):
        """Осмотреть папку под архив: годится ли и чем грозит."""
        return осмотреть_папку(
            path, учёт=self.archive_relative, нынешняя=self.base
        )

    def config_text(self) -> str:
        try:
            return self.config_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def write_config(self, text: str) -> Записано:
        return self._write(self.config_path, text, _("настройки сохранены — вступят в силу со следующего прохода"))

    def _write(self, path: Path, text: str, успех: str) -> Записано:
        try:
            if path.exists():
                path.with_suffix(path.suffix + ".bak").write_text(
                    path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
                )
            path.write_text(text, encoding="utf-8", newline="\n")
        except OSError as ошибка:
            return Записано(False, _('не сохранилось: {}').format(ошибка))
        return Записано(True, успех)

    def _ключ_архива(self) -> tuple:
        """То, что меняется вместе с архивом: учёт и список каналов."""
        ключ = []
        for путь in (self.archive_path, self.channels_path):
            try:
                сведения = путь.stat()
                ключ.append((сведения.st_mtime_ns, сведения.st_size))
            except OSError:
                ключ.append(None)
        return tuple(ключ)

    def forget_stats(self) -> None:
        """Сбросить сохранённый счёт: папки только что поменялись нашими руками."""
        self._счёт = None

    def channel_stats(self, fresh: bool = False) -> list[tuple[str, int, int]]:
        """Сколько файлов и байт лежит в папке каждого канала.

        Считаем по файлам, а не по переписи YouTube: перепись требует сети
        и занимает минуты, а окно должно отвечать сразу.

        Счёт сохраняется: см. `core.status.is_fresh`. `fresh` требует
        пересчитать — после переименования канала или по просьбе человека.
        """
        from core.status import is_fresh

        ключ = self._ключ_архива()
        сохранённый = getattr(self, "_счёт", None)
        if not fresh and сохранённый is not None:
            когда, прежний_ключ, значение = сохранённый
            if is_fresh(saved_at=когда, saved_key=прежний_ключ, now=time.time(), key=ключ, ttl=STATS_TTL):
                return значение
        значение = self._посчитать_папки()
        self._счёт = (time.time(), ключ, значение)
        return значение

    def _посчитать_папки(self) -> list[tuple[str, int, int]]:
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

    # --- пуск и остановка ---------------------------------------------------

    @property
    def tools_dir(self) -> Path:
        return self.archive_path.parent

    def worker_running(self) -> bool:
        """Заведён ли непрерывный обход. Не то же самое, что `download_running`:
        между проходами он работает, но ничего не качает."""
        from runner.daemon import daemon_running

        return daemon_running(self.tools_dir)

    def start(self) -> str:
        """Завести выкачку отдельным процессом.

        Именно отдельным: окно не качает, иначе закрыть его значило бы
        оборвать выкачку. Второй экземпляр не заведётся — не пустит замок,
        но проверяем и здесь, чтобы ответить человеку словами, а не молчанием.
        """
        from runner.daemon import clear_stop, daemon_running

        if daemon_running(self.tools_dir):
            return _("уже работает")

        # Просьба остановиться могла остаться с прошлого раза: не сняв её,
        # новый экземпляр встанет сразу же.
        clear_stop(self.tools_dir)

        запуск = self._worker_argv()
        флаги = 0
        if sys.platform == "win32":
            # Без консоли и отвязанным от окна: закрытие окна не должно
            # уводить выкачку за собой.
            флаги = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
                subprocess, "DETACHED_PROCESS", 0
            )
        try:
            subprocess.Popen(
                запуск,
                cwd=str(Path(__file__).resolve().parents[1]),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=флаги,
                start_new_session=sys.platform != "win32",
            )
        except OSError as ошибка:
            return _('не вышло запустить: {}').format(ошибка)
        return _("запустил")

    def stop(self) -> str:
        from runner.daemon import ask_stop, daemon_running

        if not daemon_running(self.tools_dir):
            return _("никто не работает")
        try:
            ask_stop(self.tools_dir)
        except OSError as ошибка:
            return _('не вышло остановить: {}').format(ошибка)
        return _("попросил остановиться — уйдёт, договорив текущий ролик")

    def _worker_argv(self) -> list[str]:
        """Чем запускать обход. Без консольного окна там, где это различают."""
        корень = Path(__file__).resolve().parents[1]
        питон = Path(sys.executable)
        без_окна = питон.with_name("pythonw.exe")
        if sys.platform == "win32" and без_окна.exists():
            питон = без_окна
        return [
            str(питон),
            str(корень / "ytarchive.py"),
            "--config",
            str(self.config_path),
            "daemon",
        ]
