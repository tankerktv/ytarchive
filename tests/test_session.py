"""Проверки цикла выкачки целиком.

Вместо настоящего yt-dlp подставляется поддельный: он разбирает те же ключи
и печатает строки, взятые дословно из наших журналов. Так проверяется вся
склейка — чтение списка, проверка доступа, загрузка, учёт — не выходя в сеть
и не завися от того, что сегодня отвечает YouTube.
"""

import sys
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest

from core.supervisor import RetryPolicy, WatchdogPolicy
from core.ytdlp_args import DownloadSettings
from runner.session import SessionConfig, run_session

pytestmark = pytest.mark.slow

#: Поддельный yt-dlp. Что он ответит, задаётся файлом рядом с ним, поэтому
#: один и тот же скрипт умеет и отдавать ролики, и требовать вход, и молчать
#: с нулевым кодом, как устаревшая версия.
ПОДДЕЛКА = textwrap.dedent(
    """
    import sys, pathlib

    args = sys.argv[1:]
    сценарий = (pathlib.Path(__file__).with_name('scenario.txt')
                .read_text(encoding='utf-8').strip())

    if '--flat-playlist' in args:
        if сценарий == 'login':
            sys.stderr.write("ERROR: Sign in to confirm you're not a bot.\\n")
            sys.exit(1)
        if сценарий == 'network':
            sys.stderr.write('ERROR: [Errno 11001] getaddrinfo failed\\n')
            sys.exit(1)
        if сценарий == 'stale':
            sys.exit(0)
        # Проверка доступа просит один идентификатор, перепись — ещё
        # длительность и название. Различаем по шаблону печати.
        шаблон = args[args.index('--print') + 1]
        if '%(title)s' in шаблон:
            # Настоящая строка yt-dlp 2026.7.4 под Python 3.10. Идёт в stderr
            # при каждом запуске и раньше засчитывалась в потерянные ролики.
            sys.stderr.write('Deprecated Feature: Support for Python version '
                             '3.10 has been deprecated.\\n')
            sys.stdout.write('rbYUHA9ZOg8\\t2796\\tПервый ролик\\n')
            sys.stdout.write('G02jtMoGy2g\\t1200\\tВторой ролик\\n')
        else:
            sys.stdout.write('rbYUHA9ZOg8\\n')
        sys.exit(0)

    archive = args[args.index('--download-archive') + 1]
    # Качаем только то, что подано списком — как настоящий yt-dlp.
    # Иначе проверка исключений была бы бессмысленной: подделка скачала бы
    # снятый ролик, и тест этого не заметил.
    заказ = [
        s.strip()
        for s in pathlib.Path(args[args.index('--batch-file') + 1])
        .read_text(encoding='utf-8').splitlines()
        if s.strip()
    ]

    for номер, ролик in enumerate(заказ, start=1):
        sys.stdout.write('[download] Downloading item %d of %d\\n' % (номер, len(заказ)))
        if ролик == 'G02jtMoGy2g':
            sys.stderr.write("ERROR: [youtube] G02jtMoGy2g: Sign in to confirm.\\n")
            continue
        sys.stdout.write('[download] Destination: /tmp/ролик.f399.mp4\\n')
        sys.stdout.write('[download] 100% of  462.12MiB in 00:01:46 at 4.35MiB/s\\n')
        sys.stdout.write('[Merger] Merging formats into "/tmp/ролик.mkv"\\n')
        with open(archive, 'a', encoding='utf-8') as fh:
            fh.write('youtube %s\\n' % ролик)
    sys.exit(0)
    """
)


@pytest.fixture
def стенд(tmp_path: Path):
    """Готовая площадка: поддельный yt-dlp, список каналов, пустой архив."""
    подделка = tmp_path / "fake_ytdlp.py"
    подделка.write_text(ПОДДЕЛКА, encoding="utf-8")
    (tmp_path / "scenario.txt").write_text("ok", encoding="utf-8")

    каналы = tmp_path / "channels.txt"
    каналы.write_text("SoyuzUS|https://www.youtube.com/@SoyuzUS/videos\n", encoding="utf-8")
    архив = tmp_path / "downloaded.txt"
    архив.write_text("", encoding="utf-8")

    config = SessionConfig(
        base_dir=tmp_path,
        channels_file=каналы,
        settings=DownloadSettings(
            archive_path=str(архив),
            output_template=str(tmp_path / "%(title)s.%(ext)s"),
        ),
        ytdlp=(sys.executable, str(подделка)),
        watchdog=WatchdogPolicy(silence_limit=20.0),
        probe_watchdog=WatchdogPolicy(silence_limit=20.0),
        retries=RetryPolicy(max_attempts=2, first_delay=0.0),
    )
    return config, tmp_path


def сценарий(каталог: Path, значение: str) -> None:
    (каталог / "scenario.txt").write_text(значение, encoding="utf-8")


def запуск(config: SessionConfig, **kwargs):
    return run_session(config, sleep=lambda _: None, **kwargs)


# --- обычный ход ------------------------------------------------------------


def test_канал_проходится_и_ролик_учитывается(стенд):
    config, каталог = стенд
    итог = запуск(config)

    assert итог.downloaded == 1, "скачанное считается по приросту архива"
    assert итог.failed == 1, "упавший ролик посчитан отдельно"
    assert not итог.needs_human, "упавший ролик — не повод звать человека"


def test_учёт_идёт_по_архиву_а_не_по_строкам_вывода(стенд):
    """В архив попадают только целиком собранные ролики — это единственный
    источник, которому можно верить. Строк «Destination» в выводе две,
    а скачанный ролик один.
    """
    config, каталог = стенд
    запуск(config)
    архив = (каталог / "downloaded.txt").read_text(encoding="utf-8")
    assert архив.count("youtube ") == 1


def test_события_прогресса_доходят_до_интерфейса(стенд):
    config, _ = стенд
    события = []
    запуск(config, on_event=события.append)

    виды = {e.kind.name for e in события}
    assert "COMPLETED" in виды
    assert "MERGING" in виды
    размеры = [e.size_bytes for e in события if e.size_bytes]
    assert размеры and размеры[0] == int(462.12 * 1024**2)


# --- беды, требующие человека -----------------------------------------------


def test_нужен_вход_останавливает_канал_сразу(стенд):
    """Ни одной попытки повтора: куки сами не появятся, и три минуты ожидания
    только оттянут момент, когда человек узнает, что от него что-то нужно.
    """
    config, каталог = стенд
    сценарий(каталог, "login")
    итог = запуск(config)

    assert итог.needs_human
    assert итог.downloaded == 0
    assert "вход в аккаунт" in итог.stopped[0].stopped_reason


def test_устаревший_ytdlp_опознаётся(стенд):
    """Пустая выдача при нулевом коде — это не «канал без роликов»."""
    config, каталог = стенд
    сценарий(каталог, "stale")
    итог = запуск(config)

    assert итог.needs_human
    assert "устарел" in итог.stopped[0].stopped_reason


def test_сетевое_пережидается_и_только_потом_сдаётся(стенд):
    config, каталог = стенд
    сценарий(каталог, "network")
    сообщения = []
    итог = запуск(config, on_message=сообщения.append)

    проверок = [m for m in сообщения if "проверка" in m]
    assert len(проверок) == 2, "должно быть ровно столько попыток, сколько разрешено"
    assert итог.needs_human
    assert "2 попыток" in итог.stopped[0].stopped_reason


# --- беды со списком каналов ------------------------------------------------


def test_нечитаемый_список_каналов_не_проходит_молча(стенд):
    """Пустой список — законное состояние, нечитаемый файл — беда.
    Спутать их значит тихо не делать ничего.
    """
    config, каталог = стенд
    config = replace(config, channels_file=каталог / "нет-такого-файла.txt")
    итог = запуск(config)

    assert итог.needs_human
    assert "не удалось прочитать" in итог.stopped[0].stopped_reason


def test_непонятая_строка_списка_попадает_в_сообщения(стенд):
    config, каталог = стенд
    (каталог / "channels.txt").write_text(
        "SoyuzUS|https://www.youtube.com/@SoyuzUS/videos\nстрока без разделителя\n",
        encoding="utf-8",
    )
    сообщения = []
    итог = запуск(config, on_message=сообщения.append)

    assert any("строка 2 пропущена" in m for m in сообщения)
    assert итог.downloaded == 1, "хорошая строка отработала несмотря на плохую"


def test_настоящий_случай_2026_08_30_общая_беда_не_перебирает_каналы(стенд):
    """30.08 сеть отвалилась, и цикл честно потратил шесть минут: SoyuzUS,
    MurkPOWER, MaddyMurk, «Подвальчик» — по три попытки на каждый, четыре
    одинаковых «остановлено — сетевой сбой».

    Убедившись на первом, остальные проверять незачем.
    """
    config, каталог = стенд
    (каталог / "channels.txt").write_text(
        "SoyuzUS|https://www.youtube.com/@SoyuzUS/videos\n"
        "MurkPOWER|https://www.youtube.com/@MurkPOWER/videos\n"
        "MaddyMurk|https://www.youtube.com/@MaddyMurk/videos\n",
        encoding="utf-8",
    )
    сценарий(каталог, "network")
    сообщения = []
    итог = запуск(config, on_message=сообщения.append)

    проверенных = {m.split(":")[0] for m in сообщения if "проверка" in m}
    assert проверенных == {"SoyuzUS"}, f"полезли в остальные каналы: {проверенных}"
    assert len(итог.stopped) == 1
    assert any("общая для всех" in m for m in сообщения)


def test_подробность_отказа_попадает_в_журнал(стенд):
    """Без неё по журналу нельзя понять, что ответил yt-dlp, и разбираться
    приходится, воспроизводя сбой руками. Проверено на себе 30.08.
    """
    config, каталог = стенд
    сценарий(каталог, "network")
    сообщения = []
    запуск(config, on_message=сообщения.append)

    проверка = next(m for m in сообщения if "проверка" in m)
    assert "getaddrinfo" in проверка, f"подробности нет: {проверка}"


def test_исключённый_ролик_не_качается(стенд):
    """Снятая галочка обязана убрать ролик из очереди. Иначе весь выбор
    в окне — украшение: человек снял, а оно всё равно скачалось.
    """
    from core.exclusions import parse_exclusions

    config, каталог = стенд
    итог = запуск(config, exclusions=parse_exclusions("rbYUHA9ZOg8\n"))
    архив = (каталог / "downloaded.txt").read_text(encoding="utf-8")

    assert "rbYUHA9ZOg8" not in архив
    assert итог.downloaded == 0


def test_про_пропущенное_по_выбору_говорим_вслух(стенд):
    # Иначе человек решит, что канал сломался: роликов нет, а почему — молчок.
    from core.exclusions import parse_exclusions

    config, _ = стенд
    сообщения = []
    запуск(config, exclusions=parse_exclusions("rbYUHA9ZOg8\n"), on_message=сообщения.append)

    assert any("по вашему выбору" in m for m in сообщения)


def test_без_исключений_качается_всё_как_раньше(стенд):
    config, каталог = стенд
    итог = запуск(config)

    assert итог.downloaded == 1
    assert "rbYUHA9ZOg8" in (каталог / "downloaded.txt").read_text(encoding="utf-8")


def test_ворчание_ytdlp_не_считается_потерянным_роликом(стенд):
    """Настоящий случай 02.09: в журнале ALEX M появилось «непонятых строк
    в переписи 1», хотя все 37 роликов разобрались. Это была строка из stderr,
    попавшая в перепись через слитый поток.

    Ложная тревога опаснее молчания: привыкнув к ней, настоящую пропажу
    ролика тоже сочтут ворчанием.
    """
    config, _ = стенд
    сообщения = []
    итог = запуск(config, on_message=сообщения.append)

    assert not any("непонятых строк" in m for m in сообщения), сообщения
    assert итог.downloaded == 1, "разделение потоков не должно ломать выкачку"


def test_список_очереди_убирается_за_собой(стенд):
    """Оставленный список собьёт с толку при разборе беды — покажет
    вчерашнюю очередь как сегодняшнюю.
    """
    config, каталог = стенд
    запуск(config)
    assert list(каталог.glob("batch-*.txt")) == []
