"""Библиотека скачанного, отметки о пропавших с YouTube и описания для
медиасерверов.

Программа умела скачать, но не помогала ни смотреть, ни узнать главное —
каких роликов из архива на YouTube уже нет. Ради второго архив и ведётся.
"""

import json
import os
from pathlib import Path

import pytest

from core.channels import Channel
from core.config import dump_config, loads, parse_config
from core.gone import MAX_SHARE, Verdict, all_gone, from_text, judge, to_text, update
from core.library import Item, build, description_from_tags, matches, parse_name
from core.nfo import episode_nfo, episode_numbers, missing_nfo, nfo_name, show_nfo
from core.supervisor import Verdict as Приговор
from core.ytdlp_args import DownloadSettings, build_args, thumbnail_template
from runner import session
from runner.library import ids_on_disk, mark_gone, nfo_todo, read_marks, scan, write_nfo
from runner.process import RunOutcome
from runner.session import SessionConfig, download_channel

# --- запись из имени файла ---------------------------------------------------


def test_запись_из_имени_файла():
    запись = parse_name("MurkPOWER", "2024-04-11 - BMW E87 - МЕЧТА [oxd5IAl-o3Q].mkv", 1500)
    assert запись == Item(
        video_id="oxd5IAl-o3Q", title="BMW E87 - МЕЧТА", channel="MurkPOWER",
        path="MurkPOWER/2024-04-11 - BMW E87 - МЕЧТА [oxd5IAl-o3Q].mkv", date="20240411", size_bytes=1500,
    )
    assert запись.date_text == "2024-04-11"
    assert запись.url.endswith("oxd5IAl-o3Q")


@pytest.mark.parametrize(
    "имя",
    [
        "2024-04-11 - Ролик [oxd5IAl-o3Q].f299.mp4.part",  # обломок
        "2024-04-11 - Ролик [oxd5IAl-o3Q].jpg",
        "2024-04-11 - Ролик [oxd5IAl-o3Q].nfo",
        "2024-04-11 - Ролик [oxd5IAl-o3Q]-thumb.jpg",
        "tvshow.nfo",
        "чужой файл.mkv",
    ],
)
def test_не_ролик_в_библиотеку_не_попадает(имя):
    """Показать обломок в библиотеке значило бы обещать то, что не откроется."""
    assert parse_name("К", имя) is None


def test_ролик_без_даты_в_имени_не_теряется():
    запись = parse_name("К", "Старое название [oxd5IAl-o3Q].mp4")
    assert запись is not None and запись.date == "" and запись.date_text == "—"


def test_скобки_в_названии_не_сбивают_разбор():
    запись = parse_name("К", "2024-01-01 - Обзор [часть 2] [oxd5IAl-o3Q].mkv")
    assert запись.title == "Обзор [часть 2]"


def test_свежие_сверху_а_без_даты_в_конце():
    записи = build([
        ("К", "2020-01-01 - Старый [aaaaaaaaaaa].mkv", 1),
        ("К", "Без даты [ccccccccccc].mkv", 1),
        ("К", "2026-01-01 - Новый [bbbbbbbbbbb].mkv", 1),
        ("К", "2026-01-01 - Новый [bbbbbbbbbbb].nfo", 1),
    ])
    assert [з.video_id for з in записи] == ["bbbbbbbbbbb", "aaaaaaaaaaa", "ccccccccccc"]


def test_пропавший_помечается():
    записи = build([("К", "2020-01-01 - А [aaaaaaaaaaa].mkv", 1)], frozenset({"aaaaaaaaaaa"}))
    assert записи[0].gone


def test_отбор():
    первый = Item("aaaaaaaaaaa", "Сборка двигателя", "MurkPOWER", "p", gone=True)
    второй = Item("bbbbbbbbbbb", "Обзор телефона", "SoyuzUS", "p")
    assert matches(первый) and matches(второй), "пустой отбор пропускает всё"
    assert matches(первый, query="ДВИГ") and not matches(второй, query="двиг")
    assert matches(второй, channel="SoyuzUS") and not matches(первый, channel="SoyuzUS")
    assert matches(первый, only_gone=True) and not matches(второй, only_gone=True)


def test_описание_из_меток_любого_контейнера():
    """Имя метки зависит от контейнера: в mkv — заглавными, в mp4 — строчными.
    Проверено на живых файлах архива."""
    assert description_from_tags({"DESCRIPTION": "Система: q9650", "COMMENT": "https://youtu.be/x"}) == "Система: q9650"
    assert description_from_tags({"description": "Двигатель стучит"}) == "Двигатель стучит"
    assert description_from_tags({"synopsis": "Запасное"}) == "Запасное"


def test_адрес_ролика_описанием_не_считается():
    """В метке `comment` лежит адрес ролика. Показать его как описание —
    выдать служебное за содержательное."""
    assert description_from_tags({"COMMENT": "https://www.youtube.com/watch?v=x"}) == ""
    assert description_from_tags({}) == ""


# --- пропавшие с YouTube -----------------------------------------------------

ДИСК = frozenset({"aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc", "ddddddddddd"})


def test_ролик_с_диска_которого_нет_в_переписи_пропал():
    приговор = judge(ДИСК, ДИСК - {"bbbbbbbbbbb"} | {"eeeeeeeeeee"})
    assert приговор == Verdict(gone=frozenset({"bbbbbbbbbbb"}), reliable=True)


def test_пустой_переписи_не_верим():
    """Так выглядит и обрыв связи, и истёкший вход. Объявить из-за этого
    пропавшим весь архив канала — худшая из ошибок."""
    assert judge(ДИСК, frozenset()) == Verdict()


def test_оборванной_переписи_не_верим():
    """Перепись оборвалась на четверти канала: «пропало» три ролика из
    четырёх. Столько разом не пропадает — это не про YouTube, а про сеть."""
    assert 3 / 4 > MAX_SHARE
    assert not judge(ДИСК, frozenset({"aaaaaaaaaaa"})).reliable


def test_ничего_не_пропало_это_надёжный_ответ():
    """Иначе ролик, вернувшийся на YouTube, навсегда остался бы в пропавших."""
    assert judge(ДИСК, ДИСК) == Verdict(gone=frozenset(), reliable=True)


def test_ненадёжный_приговор_отметок_не_трогает():
    было = {"К": frozenset({"aaaaaaaaaaa"})}
    стало, впервые = update(было, "К", Verdict())
    assert стало == было and not впервые


def test_надёжный_приговор_заменяет_отметки_и_называет_новое():
    было = {"К": frozenset({"aaaaaaaaaaa"}), "Другой": frozenset({"zzzzzzzzzzz"})}
    стало, впервые = update(было, "К", Verdict(frozenset({"bbbbbbbbbbb"}), True))
    assert стало == {"К": frozenset({"bbbbbbbbbbb"}), "Другой": frozenset({"zzzzzzzzzzz"})}
    assert впервые == {"bbbbbbbbbbb"}, "о том, что пропало впервые, говорят человеку"
    assert all_gone(стало) == {"bbbbbbbbbbb", "zzzzzzzzzzz"}


def test_отметки_переживают_запись():
    отметки = {"Уютный подвальчик": frozenset({"bbbbbbbbbbb", "aaaaaaaaaaa"}), "К": frozenset()}
    assert from_text(to_text(отметки)) == отметки


@pytest.mark.parametrize("текст", ["", "не json", "[1, 2]", '{"К": "строка"}'])
def test_испорченный_файл_отметок_это_их_отсутствие(текст):
    """Они восстановятся сами за один проход; ронять из-за них выкачку незачем."""
    assert from_text(текст) == {}


def test_отметки_пишутся_на_диск_и_о_новом_сообщается(tmp_path):
    канал = tmp_path / "К"
    канал.mkdir()
    for ролик in sorted(ДИСК):
        (канал / f"2024-01-01 - Ролик [{ролик}].mkv").write_text("x", encoding="utf-8")
    (канал / "2024-01-01 - Обломок [fffffffffff].f299.mp4.part").write_text("x", encoding="utf-8")
    assert ids_on_disk(канал) == ДИСК, "обломок роликом не считается"

    впервые = mark_gone(tmp_path, "К", ids_on_disk(канал), ДИСК - {"ccccccccccc"})
    assert впервые == {"ccccccccccc"}
    assert read_marks(tmp_path) == {"К": frozenset({"ccccccccccc"})}

    assert mark_gone(tmp_path, "К", ids_on_disk(канал), ДИСК - {"ccccccccccc"}) == frozenset(), (
        "о том же самом второй раз не говорим"
    )
    mark_gone(tmp_path, "К", ids_on_disk(канал), frozenset())
    assert read_marks(tmp_path) == {"К": frozenset({"ccccccccccc"})}, "сбой переписи отметок не стирает"


def test_проход_отмечает_пропавшее_и_говорит_об_этом(tmp_path, monkeypatch):
    архив = tmp_path / "downloaded.txt"
    архив.write_text("youtube aaaaaaaaaaa\nyoutube bbbbbbbbbbb\nyoutube ccccccccccc\n", encoding="utf-8")
    папка = tmp_path / "К"
    папка.mkdir()
    for ролик in ("aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"):
        (папка / f"2024-01-01 - Ролик [{ролик}].mkv").write_text("x", encoding="utf-8")

    def подделка(argv, policy, **kwargs):
        строки = ["aaaaaaaaaaa\t600\t20240101\tА", "ccccccccccc\t600\t20240101\tВ"]
        return RunOutcome(verdict=Приговор.OK, exit_code=0, lines=строки, stdout_lines=строки)

    monkeypatch.setattr(session, "run_watched", подделка)
    config = SessionConfig(
        base_dir=tmp_path, channels_file=tmp_path / "channels.txt",
        settings=DownloadSettings(archive_path=str(архив), output_template="x"),
    )
    сообщения = []
    download_channel(Channel("К", "https://youtube.com/@x/videos"), config, on_message=сообщения.append)

    assert read_marks(tmp_path) == {"К": frozenset({"bbbbbbbbbbb"})}
    assert any("больше нет" in строка and "1" in строка for строка in сообщения)


# --- описания для медиасервера ------------------------------------------------


def test_имя_файла_описания():
    assert nfo_name("К/2024-04-11 - Ролик [aaaaaaaaaaa].mkv") == "К/2024-04-11 - Ролик [aaaaaaaaaaa].nfo"


def test_два_ролика_одного_дня_не_получают_один_номер():
    """Сервер склеил бы их в одну серию."""
    записи = [
        Item("bbbbbbbbbbb", "Второй", "К", "p2", "20240411"),
        Item("aaaaaaaaaaa", "Первый", "К", "p1", "20240411"),
        Item("ccccccccccc", "Другой день", "К", "p3", "20241231"),
    ]
    номера = episode_numbers(записи)
    assert номера == {"aaaaaaaaaaa": 4110, "bbbbbbbbbbb": 4111, "ccccccccccc": 12310}
    assert номера == episode_numbers(list(reversed(записи))), "номер не зависит от порядка файлов"


def test_описание_серии_несёт_сезон_год_и_дату():
    текст = episode_nfo(Item("aaaaaaaaaaa", "BMW & E87 <тест>", "Murk", "p", "20240411"), 4110, "Описание")
    assert "<season>2024</season>" in текст and "<episode>4110</episode>" in текст
    assert "<aired>2024-04-11</aired>" in текст and "<plot>Описание</plot>" in текст
    assert "<title>BMW &amp; E87 &lt;тест&gt;</title>" in текст, "название — это текст, а не разметка"
    assert '<uniqueid type="youtube" default="true">aaaaaaaaaaa</uniqueid>' in текст


def test_описание_канала():
    assert "<tvshow>" in show_nfo("Уютный подвальчик") and "<title>Уютный подвальчик</title>" in show_nfo("Уютный подвальчик")


def test_описание_нужно_только_тем_у_кого_его_нет():
    записи = [Item("aaaaaaaaaaa", "А", "К", "К/А [aaaaaaaaaaa].mkv"), Item("bbbbbbbbbbb", "Б", "К", "К/Б [bbbbbbbbbbb].mkv")]
    assert missing_nfo(записи, frozenset({"К/А [aaaaaaaaaaa].nfo"})) == [записи[1]]


def test_описания_пишутся_а_существующие_не_трогаются(tmp_path, monkeypatch):
    """Описание могло быть поправлено человеком или самим медиасервером."""
    import runner.library

    monkeypatch.setattr(runner.library, "read_description", lambda путь: "Про что ролик")
    папка = tmp_path / "К"
    папка.mkdir()
    (папка / "2024-04-11 - Первый [aaaaaaaaaaa].mkv").write_text("x", encoding="utf-8")
    (папка / "2024-04-11 - Второй [bbbbbbbbbbb].mkv").write_text("x", encoding="utf-8")
    своё = папка / "2024-04-11 - Второй [bbbbbbbbbbb].nfo"
    своё.write_text("поправлено руками", encoding="utf-8")

    роликам, каналам = nfo_todo(tmp_path)
    assert [з.video_id for з in роликам] == ["aaaaaaaaaaa"] and каналам == ["К"]

    assert write_nfo(tmp_path) == (2, 0)
    assert своё.read_text(encoding="utf-8") == "поправлено руками"
    новое = (папка / "2024-04-11 - Первый [aaaaaaaaaaa].nfo").read_text(encoding="utf-8")
    assert "<plot>Про что ролик</plot>" in новое
    assert "<episode>4110</episode>" in новое, "номер считается по всем роликам канала, а не только по новым"
    assert (папка / "tvshow.nfo").exists()
    assert nfo_todo(tmp_path) == ([], []), "второй раз писать нечего"
    assert len([и for _к, и, _р in scan(tmp_path) if и.endswith(".mkv")]) == 2


# --- настройки и ключи yt-dlp -------------------------------------------------


def test_обложка_серии_ложится_рядом_с_хвостом_thumb():
    """Так обложку серии ищут Kodi и Jellyfin."""
    assert thumbnail_template("D:/a/К/%(title)s [%(id)s].%(ext)s") == "D:/a/К/%(title)s [%(id)s]-thumb.%(ext)s"
    доводы = build_args(DownloadSettings("a", "D:/a/%(id)s.%(ext)s", write_thumbnail=True), "u")
    assert "--write-thumbnail" in доводы
    assert "thumbnail:D:/a/%(id)s-thumb.%(ext)s" in доводы


def test_комментарии_и_обложки_по_умолчанию_выключены():
    доводы = build_args(DownloadSettings("a", "o"), "u")
    assert "--write-comments" not in доводы and "--write-thumbnail" not in доводы
    config = parse_config({"paths": {"base": "/a"}})
    assert config.write_comments is False and config.media_server is False


def test_комментарии_включаются_настройкой_и_переживают_запись():
    config = parse_config({"paths": {"base": "/a"}, "download": {"write_comments": True, "media_server": True}})
    assert parse_config(loads(dump_config(config))) == config
    assert "--write-comments" in build_args(DownloadSettings("a", "o", write_comments=True), "u")


# --- вкладка ------------------------------------------------------------------


@pytest.fixture
def вкладка(tmp_path):
    pytest.importorskip("PySide6", reason="окно проверяется только там, где есть Qt")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from gui.library import ВкладкаБиблиотека
    from gui.source import ArchiveSource

    _приложение = QApplication.instance() or QApplication([])
    (tmp_path / "_tools").mkdir()
    for канал, имя, размер in (
        ("MurkPOWER", "2024-04-11 - Сборка двигателя [aaaaaaaaaaa].mkv", 3000),
        ("MurkPOWER", "2020-01-01 - Старый ролик [bbbbbbbbbbb].mkv", 100),
        ("SoyuzUS", "2026-10-07 - Первый сервис [ccccccccccc].mkv", 2000),
        ("SoyuzUS", "2026-10-07 - Первый сервис [ccccccccccc].f299.mp4.part", 5),
    ):
        (tmp_path / канал).mkdir(exist_ok=True)
        (tmp_path / канал / имя).write_text("x" * размер, encoding="utf-8")
    (tmp_path / "_tools" / "gone.json").write_text(json.dumps({"MurkPOWER": ["bbbbbbbbbbb"]}), encoding="utf-8")
    источник = ArchiveSource(
        base=tmp_path, archive_path=tmp_path / "_tools" / "downloaded.txt", logs_dir=tmp_path / "_logs",
        lock_path=tmp_path / "_tools" / "ytarchive.lock", channels_path=tmp_path / "_tools" / "channels.txt",
        config_path=tmp_path / "ytarchive.toml", live_path=tmp_path / "_tools" / "live.json",
    )
    виджет = ВкладкаБиблиотека(источник, фоновые=False)
    виджет.перечитать()
    yield виджет
    виджет.дождаться_потоков()


def видимые(виджет) -> list[str]:
    from gui.library import СТОЛБЕЦ_НАЗВАНИЕ

    return [
        виджет.таблица.item(строка, СТОЛБЕЦ_НАЗВАНИЕ).text()
        for строка in range(виджет.таблица.rowCount())
        if not виджет.таблица.isRowHidden(строка)
    ]


@pytest.mark.slow
def test_библиотека_показывает_скачанное_свежее_сверху(вкладка):
    assert видимые(вкладка) == ["Первый сервис", "Сборка двигателя", "Старый ролик"]
    assert "показано 3 из 3" in вкладка.счётчик.text()


@pytest.mark.slow
def test_поиск_идёт_по_всем_каналам_сразу(вкладка):
    вкладка.поиск.setText("серв")
    assert видимые(вкладка) == ["Первый сервис"]
    вкладка.поиск.setText("")
    вкладка.канал.setCurrentIndex(вкладка.канал.findData("MurkPOWER"))
    assert видимые(вкладка) == ["Сборка двигателя", "Старый ролик"]


@pytest.mark.slow
def test_можно_показать_только_пропавшее_с_youtube(вкладка):
    """Ради этого архив и ведётся."""
    вкладка.только_пропавшие.setChecked(True)
    assert видимые(вкладка) == ["Старый ролик"]
    assert "нет на YouTube: 1" in вкладка.счётчик.text()


@pytest.mark.slow
def test_порядок_по_размеру_числовой_а_не_по_буквам(вкладка):
    """Иначе «9.5 ГБ» оказалось бы больше, чем «10.2 ГБ»."""
    from PySide6.QtCore import Qt

    from gui.library import СТОЛБЕЦ_РАЗМЕР

    вкладка.таблица.sortByColumn(СТОЛБЕЦ_РАЗМЕР, Qt.SortOrder.DescendingOrder)
    assert видимые(вкладка) == ["Сборка двигателя", "Первый сервис", "Старый ролик"]


@pytest.mark.slow
def test_после_смены_порядка_выбирается_тот_же_ролик(вкладка):
    """Номер строки после упорядочивания ничего не говорит о том, что в ней
    лежит: открыть «по номеру строки» значило бы открыть чужой ролик."""
    from PySide6.QtCore import Qt

    from gui.library import СТОЛБЕЦ_НАЗВАНИЕ

    вкладка.таблица.sortByColumn(СТОЛБЕЦ_НАЗВАНИЕ, Qt.SortOrder.AscendingOrder)
    вкладка.таблица.selectRow(0)
    выбранный = вкладка._текущая()
    assert выбранный.title == вкладка.таблица.item(0, СТОЛБЕЦ_НАЗВАНИЕ).text() == "Первый сервис"
    assert вкладка._путь(выбранный).name == "2026-10-07 - Первый сервис [ccccccccccc].mkv"
    assert вкладка.кнопка_смотреть.isEnabled()
