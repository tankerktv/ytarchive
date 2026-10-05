"""Проверки того, в какую папку ложатся ролики канала.

Настоящий случай: в шаблоне пути стояло `%(channel)s` — название канала,
каким его отдаёт YouTube. Через месяц работы два канала из пяти
переименовались, и всё новое пошло в папки с новыми названиями: `SoyuzUS`
застыл на 210 роликах, рядом вырос `Soyuz`. Ничего не упало и ничего
не записалось в журнал — архив раскололся молча.

Папка обязана браться из имени в нашем списке: его меняет только хозяин.
"""

from pathlib import Path, PurePath

from core.channels import Channel
from core.supervisor import Verdict
from core.ytdlp_args import FILE_TEMPLATE, DownloadSettings, output_template_for
from runner import session
from runner.process import RunOutcome
from runner.session import SessionConfig, download_channel

# --- сам шаблон --------------------------------------------------------------


def test_папка_в_шаблоне_это_имя_из_списка():
    шаблон = output_template_for("D:/Архив", "SoyuzUS")
    assert PurePath(шаблон).parent.name == "SoyuzUS"
    assert шаблон.endswith(FILE_TEMPLATE)


def test_в_шаблоне_нет_названия_от_youtube():
    """Именно оно и раскололо архив: его меняет владелец канала."""
    assert "%(channel)s" not in output_template_for("D:/Архив", "SoyuzUS")
    assert "%(uploader)s" not in output_template_for("D:/Архив", "SoyuzUS")


def test_процент_в_имени_не_ломает_шаблон():
    """Для yt-dlp знак процента начинает подстановку. Канал «100% игры»
    без удвоения дал бы ошибку шаблона на каждом ролике.
    """
    шаблон = output_template_for("D:/Архив", "100% игры")
    assert PurePath(шаблон).parent.name == "100%% игры"


def test_кириллица_и_пробелы_в_имени_доходят_как_есть():
    шаблон = output_template_for("D:/Архив", "Уютный подвальчик")
    assert PurePath(шаблон).parent.name == "Уютный подвальчик"


# --- что уходит в yt-dlp на деле ---------------------------------------------


def _запуск_с_подменой(tmp_path: Path, monkeypatch, имя_канала: str) -> list[str]:
    """Прогнать канал, подменив запуск процессов, и вернуть доводы загрузки."""
    запуски: list[list[str]] = []

    def подделка(argv, policy, **kwargs):
        запуски.append(list(argv))
        if "--flat-playlist" in argv:
            строки = ["rbYUHA9ZOg8\t600\tРолик"]
            return RunOutcome(verdict=Verdict.OK, exit_code=0, lines=строки, stdout_lines=строки)
        return RunOutcome(verdict=Verdict.OK, exit_code=0)

    monkeypatch.setattr(session, "run_watched", подделка)

    архив = tmp_path / "downloaded.txt"
    архив.write_text("", encoding="utf-8")
    config = SessionConfig(
        base_dir=tmp_path,
        channels_file=tmp_path / "channels.txt",
        settings=DownloadSettings(
            archive_path=str(архив),
            # Нарочно старый шаблон: цикл обязан его перекрыть.
            output_template=str(tmp_path / "%(channel)s" / FILE_TEMPLATE),
        ),
    )
    download_channel(Channel(name=имя_канала, url="https://youtube.com/@x/videos"), config)

    загрузка = next(a for a in запуски if "--batch-file" in a)
    return загрузка


def test_загрузка_идёт_в_папку_по_имени_из_списка(tmp_path, monkeypatch):
    """Главная проверка: что бы ни стояло в общих настройках, в yt-dlp уходит
    путь с папкой канала из списка.
    """
    доводы = _запуск_с_подменой(tmp_path, monkeypatch, "SoyuzUS")
    путь = доводы[доводы.index("-o") + 1]

    assert PurePath(путь).parent == PurePath(tmp_path) / "SoyuzUS"
    assert "%(channel)s" not in путь, "в путь снова попало название от YouTube"


def test_у_каждого_канала_своя_папка(tmp_path, monkeypatch):
    # Общий шаблон на все каналы и был причиной: различать их оставалось YouTube.
    первый = _запуск_с_подменой(tmp_path, monkeypatch, "SoyuzUS")
    второй = _запуск_с_подменой(tmp_path, monkeypatch, "MurkPOWER")

    assert первый[первый.index("-o") + 1] != второй[второй.index("-o") + 1]
