"""Проверки переименования канала.

Имя канала задаёт папку. Переименовать одно без другого значит расколоть
архив: новое пойдёт в новую папку, старое останется в прежней. Это уже
случалось — когда имя папки брали у YouTube и канал переименовал его владелец.

Половина проверок здесь — на отказ. Сработавшее неверно переименование
перемешивает два архива так, что потом не разобрать; несработавшее просто
оставляет всё как было.
"""

import pytest

from core.channels import (
    Channel,
    FolderMove,
    RenameVerdict,
    check_rename,
    judge_folder_rename,
    parse_channels,
    rename_channel,
)

КАНАЛЫ = (
    Channel("SoyuzUS", "https://www.youtube.com/@SoyuzUS/videos"),
    Channel("MurkPOWER", "https://www.youtube.com/@MurkPOWER/videos"),
)


# --- можно ли такое имя ------------------------------------------------------


def test_обычное_переименование_разрешено():
    assert check_rename(КАНАЛЫ, 0, "Союз") is RenameVerdict.OK


def test_пустое_имя_не_годится():
    assert check_rename(КАНАЛЫ, 0, "   ") is RenameVerdict.EMPTY


@pytest.mark.parametrize("имя", ["a:b", "a/b", "a\\b", "что?", "a|b", 'кавычки"', "<тег>"])
def test_имя_с_запретными_для_папки_знаками_не_годится(имя):
    """Имя уезжает в путь. Узнать о плохом имени лучше здесь, чем на середине
    скачивания."""
    assert check_rename(КАНАЛЫ, 0, имя) is RenameVerdict.FORBIDDEN


def test_то_же_самое_имя_это_не_переименование():
    assert check_rename(КАНАЛЫ, 0, "SoyuzUS") is RenameVerdict.SAME


def test_имя_другого_канала_занято():
    """Два канала в одну папку — перемешанный архив, разобрать который
    потом нельзя.
    """
    assert check_rename(КАНАЛЫ, 0, "MurkPOWER") is RenameVerdict.DUPLICATE


def test_имя_другого_канала_занято_и_в_другом_регистре():
    # На Windows «murkpower» и «MurkPOWER» — одна и та же папка.
    assert check_rename(КАНАЛЫ, 0, "murkpower") is RenameVerdict.DUPLICATE


def test_сменить_регистр_собственного_имени_можно():
    assert check_rename(КАНАЛЫ, 0, "soyuzus") is RenameVerdict.OK


def test_несуществующий_канал():
    assert check_rename(КАНАЛЫ, 5, "Союз") is RenameVerdict.NO_SUCH
    assert check_rename(КАНАЛЫ, -1, "Союз") is RenameVerdict.NO_SUCH


def test_переименование_не_трогает_адрес_и_порядок():
    итог = rename_channel(КАНАЛЫ, 0, "  Союз  ")
    assert [c.name for c in итог] == ["Союз", "MurkPOWER"]
    assert итог[0].url == КАНАЛЫ[0].url


def test_недопустимое_переименование_не_делается_молча():
    with pytest.raises(ValueError):
        rename_channel(КАНАЛЫ, 0, "MurkPOWER")


# --- что делать с папкой -----------------------------------------------------


def test_папка_едет_вместе_с_именем():
    assert judge_folder_rename(old_exists=True, new_exists=False, same_folder=False) is FolderMove.MOVE


def test_если_папки_ещё_нет_двигать_нечего():
    # Канал добавили, но ни одного ролика ещё не скачали.
    assert judge_folder_rename(old_exists=False, new_exists=False, same_folder=False) is FolderMove.NOTHING


def test_чужую_готовую_папку_молча_не_занимаем():
    """Там могут лежать ролики другого канала. Слить — значит перемешать."""
    assert judge_folder_rename(old_exists=True, new_exists=True, same_folder=False) is FolderMove.CONFLICT


def test_смена_одного_регистра_это_та_же_папка():
    assert judge_folder_rename(old_exists=True, new_exists=True, same_folder=True) is FolderMove.MOVE


# --- на настоящих папках -----------------------------------------------------


@pytest.fixture
def источник(tmp_path):
    from gui.source import ArchiveSource

    (tmp_path / "_tools").mkdir()
    (tmp_path / "_tools" / "channels.txt").write_text(
        "SoyuzUS|https://www.youtube.com/@SoyuzUS/videos\n"
        "MurkPOWER|https://www.youtube.com/@MurkPOWER/videos\n",
        encoding="utf-8",
    )
    (tmp_path / "SoyuzUS").mkdir()
    (tmp_path / "SoyuzUS" / "ролик [aaaaaaaaaaa].mp4").write_bytes(b"x")
    return ArchiveSource(
        base=tmp_path,
        archive_path=tmp_path / "_tools" / "downloaded.txt",
        logs_dir=tmp_path / "_logs",
        lock_path=tmp_path / "_tools" / "ytarchive.lock",
        channels_path=tmp_path / "_tools" / "channels.txt",
        config_path=tmp_path / "ytarchive.toml",
        live_path=tmp_path / "_tools" / "live.json",
    )


def имена(источник) -> list[str]:
    return [c.name for c in parse_channels(источник.channels_text()).channels]


def test_папка_и_список_меняются_вместе(источник):
    ответ = источник.rename_channel(0, "Союз")

    assert ответ.ok, ответ.text
    assert имена(источник) == ["Союз", "MurkPOWER"]
    assert not (источник.base / "SoyuzUS").exists()
    assert (источник.base / "Союз" / "ролик [aaaaaaaaaaa].mp4").exists()


def test_занятая_папка_останавливает_всё(источник):
    """Ни список, ни папки не должны измениться: половина переименования
    хуже, чем никакого.
    """
    (источник.base / "Союз").mkdir()
    (источник.base / "Союз" / "чужой.mp4").write_bytes(b"y")

    ответ = источник.rename_channel(0, "Союз")

    assert not ответ.ok
    assert имена(источник) == ["SoyuzUS", "MurkPOWER"]
    assert (источник.base / "SoyuzUS" / "ролик [aaaaaaaaaaa].mp4").exists()
    assert (источник.base / "Союз" / "чужой.mp4").exists()


def test_отказ_по_имени_ничего_не_трогает(источник):
    ответ = источник.rename_channel(0, "MurkPOWER")

    assert not ответ.ok
    assert имена(источник) == ["SoyuzUS", "MurkPOWER"]
    assert (источник.base / "SoyuzUS").is_dir()


def test_канал_без_папки_переименовывается_только_в_списке(источник):
    ответ = источник.rename_channel(1, "Мурк")

    assert ответ.ok, ответ.text
    assert имена(источник) == ["SoyuzUS", "Мурк"]
    assert not (источник.base / "Мурк").exists()


def test_во_время_прохода_переименовывать_нельзя(источник, monkeypatch):
    """Идущий проход держит прежнее имя в памяти: он завёл бы старую папку
    заново и доложил остаток канала туда — тот же раскол, только своими руками.
    """
    monkeypatch.setattr(type(источник), "download_running", lambda self: True)

    ответ = источник.rename_channel(0, "Союз")

    assert not ответ.ok
    assert имена(источник) == ["SoyuzUS", "MurkPOWER"]
    assert (источник.base / "SoyuzUS").is_dir()


def test_несохранённый_список_возвращает_папку_на_место(источник, monkeypatch):
    """Список не записался, а папка уже переименована — имя и папка разошлись
    бы, и следующий проход начал бы складывать ролики в пустую папку.
    """
    from gui.source import Записано

    monkeypatch.setattr(
        type(источник), "write_channels", lambda self, text: Записано(False, "не сохранилось")
    )

    ответ = источник.rename_channel(0, "Союз")

    assert not ответ.ok
    assert (источник.base / "SoyuzUS" / "ролик [aaaaaaaaaaa].mp4").exists()
    assert not (источник.base / "Союз").exists()
