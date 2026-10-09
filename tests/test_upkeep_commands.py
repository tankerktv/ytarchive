"""Команды ухода за архивом на настоящей файловой системе.

Ядро решает, что убрать; здесь проверяется, что команда без `--apply`
не трогает ничего, а с ним трогает ровно то, что показала.

Удаление — единственное, что в этой программе нельзя отменить, поэтому
главные проверки здесь про то, что осталось на месте.
"""

import os
import sys
import time

import pytest

from app import main as app_main
from core.supervisor import Verdict, WatchdogPolicy
from runner.process import run_watched

СУТКИ = 86400.0


@pytest.fixture
def архив(tmp_path):
    """Папка архива: канал с роликами и обломками, журналы, учёт."""
    (tmp_path / "_tools").mkdir()
    (tmp_path / "_logs").mkdir()
    канал = tmp_path / "Канал"
    канал.mkdir()
    настройки = tmp_path / "ytarchive.toml"
    настройки.write_text(
        f'[paths]\nbase = "{tmp_path.as_posix()}"\n[limits]\nkeep_logs_days = 30\n', encoding="utf-8"
    )

    def файл(папка, имя, возраст_суток=0.0, текст="x"):
        путь = папка / имя
        путь.write_text(текст, encoding="utf-8")
        когда = time.time() - возраст_суток * СУТКИ
        os.utime(путь, (когда, когда))
        return путь

    return tmp_path, настройки, файл


def команда(настройки, *доводы) -> int:
    return app_main.main(["--config", str(настройки), *доводы])


def test_clean_без_apply_ничего_не_трогает(архив, capsys):
    каталог, настройки, файл = архив
    for номер in range(30):
        файл(каталог / "_logs", f"старый-{номер:02d}.log", возраст_суток=60 + номер)
    обломок = файл(каталог / "Канал", "Ролик [aaaaaaaaaaa].f299.mp4.part", возраст_суток=20)

    assert команда(настройки, "clean") == 0
    assert len(list((каталог / "_logs").glob("*.log"))) == 30
    assert обломок.exists()
    assert "--apply" in capsys.readouterr().out, "сказано, как убрать на самом деле"


def test_clean_apply_убирает_старое_и_бережёт_остальное(архив):
    каталог, настройки, файл = архив
    for номер in range(30):
        файл(каталог / "_logs", f"старый-{номер:02d}.log", возраст_суток=60 + номер)
    свежий = файл(каталог / "_logs", "свежий.log", возраст_суток=1)
    (каталог / "_tools" / "downloaded.txt").write_text("youtube bbbbbbbbbbb\n", encoding="utf-8")

    брошенный = файл(каталог / "Канал", "А [aaaaaaaaaaa].f299.mp4.part", возраст_суток=20)
    от_скачанного = файл(каталог / "Канал", "Б [bbbbbbbbbbb].f299.mp4.part", возраст_суток=0)
    продолжение = файл(каталог / "Канал", "В [ccccccccccc].f299.mp4.part", возраст_суток=1)
    ролик = файл(каталог / "Канал", "Б [bbbbbbbbbbb].mkv", возраст_суток=400)

    assert команда(настройки, "clean", "--apply") == 0

    assert not брошенный.exists() and not от_скачанного.exists()
    assert продолжение.exists(), "свежий обломок нескачанного ролика — это продолжение загрузки"
    assert ролик.exists(), "целый ролик не трогается никогда"
    assert свежий.exists()
    # 31 журнал, 20 самых свежих неприкосновенны, остальные 11 старше срока.
    assert len(list((каталог / "_logs").glob("*.log"))) == 20


def test_clean_когда_убирать_нечего(архив, capsys):
    _каталог, настройки, _файл = архив
    assert команда(настройки, "clean", "--apply") == 0


def test_verify_сходящийся_архив(архив, capsys):
    каталог, настройки, файл = архив
    (каталог / "_tools" / "downloaded.txt").write_text("youtube aaaaaaaaaaa\n", encoding="utf-8")
    файл(каталог / "Канал", "А [aaaaaaaaaaa].mkv")
    assert команда(настройки, "verify") == 0


def test_verify_называет_расхождения_и_ничего_не_правит(архив, capsys):
    каталог, настройки, файл = архив
    учёт = каталог / "_tools" / "downloaded.txt"
    учёт.write_text("youtube aaaaaaaaaaa\nyoutube bbbbbbbbbbb\n", encoding="utf-8")
    файл(каталог / "Канал", "А [aaaaaaaaaaa].mkv")
    файл(каталог / "Канал", "В [ccccccccccc].mkv")

    assert команда(настройки, "verify") == 1
    вывод = capsys.readouterr().out
    assert "bbbbbbbbbbb" in вывод, "ролик без файла назван"
    assert "В [ccccccccccc].mkv" in вывод, "файл без учёта назван"
    assert учёт.read_text(encoding="utf-8") == "youtube aaaaaaaaaaa\nyoutube bbbbbbbbbbb\n"


def test_verify_apply_убирает_повторы_и_оставляет_копию(архив):
    каталог, настройки, файл = архив
    учёт = каталог / "_tools" / "downloaded.txt"
    прежний = "youtube aaaaaaaaaaa\nyoutube aaaaaaaaaaa\n"
    учёт.write_text(прежний, encoding="utf-8")
    файл(каталог / "Канал", "А [aaaaaaaaaaa].mkv")

    assert команда(настройки, "verify") == 0, "одни повторы — не расхождение"
    assert учёт.read_text(encoding="utf-8") == прежний, "без --apply учёт не тронут"

    assert команда(настройки, "verify", "--apply") == 0
    assert учёт.read_text(encoding="utf-8") == "youtube aaaaaaaaaaa\n"
    копии = list((каталог / "_tools").glob("downloaded.txt.*.bak"))
    assert len(копии) == 1 and копии[0].read_text(encoding="utf-8") == прежний


def test_verify_apply_не_трогает_учёт_пока_идёт_выкачка(архив):
    """yt-dlp дописывает учёт прямо во время работы. Перезаписав файл под
    ним, потеряли бы строки, которые он допишет в старый."""
    from runner.lockfile import acquire

    каталог, настройки, файл = архив
    учёт = каталог / "_tools" / "downloaded.txt"
    прежний = "youtube aaaaaaaaaaa\nyoutube aaaaaaaaaaa\n"
    учёт.write_text(прежний, encoding="utf-8")
    файл(каталог / "Канал", "А [aaaaaaaaaaa].mkv")

    замок, _объяснение = acquire(каталог / "_tools" / "ytarchive.lock")
    assert замок is not None
    with замок:
        assert команда(настройки, "verify", "--apply") == 1
    assert учёт.read_text(encoding="utf-8") == прежний


def test_проход_убирает_старые_журналы_но_не_свой(архив):
    каталог, _настройки, файл = архив
    for номер in range(30):
        файл(каталог / "_logs", f"старый-{номер:02d}.log", возраст_суток=60 + номер)
    свой = файл(каталог / "_logs", "свой.log", возраст_суток=90)

    убрано = app_main.убрать_старые_журналы(каталог / "_logs", 30, кроме=свой)
    assert убрано == 10
    assert свой.exists(), "журнал идущего прохода не убирается, каким бы старым ни казался"


def test_нулевой_срок_журналы_не_трогает(архив):
    каталог, _настройки, файл = архив
    for номер in range(30):
        файл(каталог / "_logs", f"старый-{номер:02d}.log", возраст_суток=600)
    assert app_main.убрать_старые_журналы(каталог / "_logs", 0) == 0


@pytest.mark.slow
def test_ползущий_потомок_снимается_хотя_говорит():
    """Тот самый случай: процесс печатает без остановки, молчанием его не
    взять. Снимает его второе мерило."""
    болтун = "import time\nwhile True:\n    print('жив', flush=True)\n    time.sleep(0.05)\n"
    начало = time.monotonic()
    итог = run_watched(
        [sys.executable, "-c", болтун],
        WatchdogPolicy(silence_limit=60.0, kill_grace=5.0),
        is_crawling=lambda now: now - начало > 1.0,
    )
    assert итог.verdict is Verdict.CRAWLING
    assert итог.killed and not итог.kill_failed
    assert time.monotonic() - начало < 20
