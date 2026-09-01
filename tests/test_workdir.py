"""Проверки смены рабочей папки.

Настройка выглядит как «куда складывать», а на деле решает судьбу учёта
скачанного: он лежит внутри этой папки. Указать пустую — начать архив
с нуля и забрать 1,27 ТБ заново.

Отсюда главное свойство, которое здесь сторожится: согласие никогда не
бывает молчаливым. Даже когда папка годится, человеку возвращается текст
о том, что именно случится.
"""

from core.workdir import judge_folder

ГОДНАЯ = dict(exists=True, is_dir=True, writable=True, has_archive=False)


def test_несуществующая_папка_не_годится():
    итог = judge_folder(exists=False, is_dir=False, writable=False, has_archive=False)
    assert not итог.ok
    assert "папки нет" in итог.reason


def test_файл_вместо_папки_не_годится():
    итог = judge_folder(exists=True, is_dir=False, writable=True, has_archive=False)
    assert not итог.ok
    assert "файл" in итог.reason


def test_папка_без_записи_не_годится():
    """Иначе беда всплывёт ночью, посреди выкачки, и в журнале."""
    итог = judge_folder(exists=True, is_dir=True, writable=False, has_archive=False)
    assert not итог.ok
    assert "нельзя писать" in итог.reason


def test_нынешняя_папка_не_считается_сменой():
    # Молча «сохранить» то же самое — сбить с толку: человек решит, что
    # смена произошла.
    итог = judge_folder(**ГОДНАЯ, same_as_now=True)
    assert not итог.ok
    assert "нынешняя" in итог.reason


def test_папка_с_архивом_годится_и_объясняет_что_будет():
    итог = judge_folder(
        exists=True, is_dir=True, writable=True, has_archive=True, archive_count=1935
    )
    assert итог.ok
    assert "1935" in итог.warning
    assert "продолжит" in итог.warning


def test_пустая_папка_годится_но_предупреждает_о_перекачке():
    """Самая опасная из годных: всё скачается заново, и узнать об этом
    после согласия — поздно.
    """
    итог = judge_folder(**ГОДНАЯ, files_inside=0)
    assert итог.ok
    assert "заново" in итог.warning


def test_папка_с_файлами_но_без_учёта_предупреждает_отдельно():
    # Не то же самое, что пустая: человек видит свои ролики и решит,
    # что программа их узнает. Не узнает — учёт ведётся файлом, а не диском.
    итог = judge_folder(**ГОДНАЯ, files_inside=400)
    assert итог.ok
    assert "не сможет понять" in итог.warning


def test_годная_папка_всегда_что_то_говорит():
    """Пустое предупреждение при ok означало бы молчаливое согласие."""
    для_проверки = [
        judge_folder(**ГОДНАЯ, files_inside=0),
        judge_folder(**ГОДНАЯ, files_inside=10),
        judge_folder(exists=True, is_dir=True, writable=True, has_archive=True),
    ]
    for итог in для_проверки:
        assert итог.ok
        assert итог.warning.strip()


def test_про_перенос_файлов_сказано_прямо():
    """Ожидание «программа перенесёт архив» стоит терабайта недоразумений."""
    for итог in (
        judge_folder(**ГОДНАЯ),
        judge_folder(exists=True, is_dir=True, writable=True, has_archive=True),
    ):
        assert "не переносит" in итог.warning


# --- сбор фактов о настоящей папке ------------------------------------------


def источник(tmp_path):
    from gui.source import ArchiveSource

    база = tmp_path / "нынешняя"
    (база / "_tools").mkdir(parents=True)
    return ArchiveSource(
        base=база,
        archive_path=база / "_tools" / "downloaded.txt",
        logs_dir=база / "_logs",
        lock_path=база / "_tools" / "ytarchive.lock",
        channels_path=база / "_tools" / "channels.txt",
        config_path=tmp_path / "ytarchive.toml",
        live_path=база / "_tools" / "live.json",
    )


def test_учёт_ищется_на_том_же_месте_внутри_новой_папки(tmp_path):
    """Иначе смена папки не увидела бы там готового архива и молча
    предложила бы скачать всё заново.
    """
    src = источник(tmp_path)
    assert src.archive_relative == "_tools/downloaded.txt"


def test_папка_с_готовым_учётом_опознаётся(tmp_path):
    src = источник(tmp_path)
    новая = tmp_path / "новая"
    (новая / "_tools").mkdir(parents=True)
    (новая / "_tools" / "downloaded.txt").write_text(
        "youtube aaaaaaaaaaa\nyoutube bbbbbbbbbbb\n", encoding="utf-8"
    )

    итог = src.check_folder(новая)
    assert итог.ok
    assert "2 роликов" in итог.warning


def test_пустая_папка_предупреждает_о_перекачке(tmp_path):
    src = источник(tmp_path)
    новая = tmp_path / "пустая"
    новая.mkdir()

    итог = src.check_folder(новая)
    assert итог.ok
    assert "заново" in итог.warning


def test_несуществующую_папку_не_принимаем(tmp_path):
    src = источник(tmp_path)
    итог = src.check_folder(tmp_path / "нет-такой")
    assert not итог.ok


def test_нынешняя_папка_отвергается(tmp_path):
    src = источник(tmp_path)
    итог = src.check_folder(src.base)
    assert not итог.ok
    assert "нынешняя" in итог.reason


def test_проба_записи_за_собой_убирает(tmp_path):
    """Проверка записью не должна оставлять мусор в чужой папке."""
    src = источник(tmp_path)
    новая = tmp_path / "чистая"
    новая.mkdir()

    src.check_folder(новая)
    assert list(новая.iterdir()) == []
