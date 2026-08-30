"""Проверки сборки аргументов yt-dlp.

Набор ключей выстрадан за неделю выкачки, и каждый здесь не просто так.
Тесты сторожат именно это: чтобы «наведение порядка» не выкинуло ключ,
без которого всё встанет через сутки.
"""

import pytest

from core.ytdlp_args import (
    DownloadSettings,
    build_args,
    build_probe_args,
    format_selector,
    format_sort,
)

НАСТРОЙКИ = DownloadSettings(
    archive_path="F:/архив/downloaded.txt",
    output_template="F:/архив/%(channel)s/%(title)s.%(ext)s",
    cookies_file="F:/архив/cookies.txt",
)


def пары(args, ключ):
    """Значения, идущие сразу за ключом."""
    return [args[i + 1] for i, a in enumerate(args) if a == ключ and i + 1 < len(args)]


# --- ключи, без которых не работает -----------------------------------------


def test_движок_javascript_обязателен():
    # Без него YouTube отдаёт только раскадровки — сам ролик не достаётся.
    assert пары(build_args(НАСТРОЙКИ, "URL"), "--js-runtimes") == ["node"]


def test_обход_ложной_проверки_прав_на_вкладку():
    значения = пары(build_args(НАСТРОЙКИ, "URL"), "--extractor-args")
    assert "youtubetab:skip=authcheck" in значения


def test_построчный_вывод_обязателен():
    # Без него прогресс идёт возвратом каретки в одну строку,
    # и надзорщик не видит признаков жизни — снимет живую загрузку.
    assert "--newline" in build_args(НАСТРОЙКИ, "URL")


def test_отказ_на_ролике_не_прекращает_проход():
    args = build_args(НАСТРОЙКИ, "URL")
    assert "--ignore-errors" in args
    assert "--no-abort-on-error" in args


def test_архив_и_продолжение():
    args = build_args(НАСТРОЙКИ, "URL")
    assert пары(args, "--download-archive") == ["F:/архив/downloaded.txt"]
    assert "--continue" in args
    assert "--no-overwrites" in args


def test_паузы_передаются():
    args = build_args(НАСТРОЙКИ, "URL")
    assert пары(args, "--min-sleep-interval") == ["15"]
    assert пары(args, "--max-sleep-interval") == ["45"]
    assert пары(args, "--sleep-requests") == ["2"]


def test_адрес_идёт_последним():
    assert build_args(НАСТРОЙКИ, "https://youtube.com/@X/videos")[-1] == (
        "https://youtube.com/@X/videos"
    )


# --- выбор формата ----------------------------------------------------------


def test_потолок_разрешения_попадает_в_отбор():
    assert "height<=720" in format_selector(720)


def test_av1_предпочитается_когда_просят():
    assert "vcodec:av01" in format_sort(1080, prefer_av1=True)


def test_без_предпочтения_av1_его_нет():
    assert "vcodec:av01" not in format_sort(1080, prefer_av1=False)


def test_настоящий_случай_2026_08_16_av1_даёт_нижнюю_границу_вилки():
    """Предпочтение AV1 при равном разрешении — разница между 1,1 и 1,9 ТБ
    на нашем архиве. Проверка на живом ролике дала `av01.0.09M.08`.
    """
    args = build_args(НАСТРОЙКИ, "URL")
    сортировка = пары(args, "-S")[0]
    assert "vcodec:av01" in сортировка
    assert "res:1080" in сортировка


# --- быстрый проход ---------------------------------------------------------


def test_быстрый_проход_по_умолчанию_выключен():
    # Включённый не вовремя, он обрывает выкачку на первом же скачанном ролике.
    assert "--break-on-existing" not in build_args(НАСТРОЙКИ, "URL")


def test_быстрый_проход_добавляется_когда_разрешён():
    настройки = DownloadSettings(
        archive_path="a", output_template="o", break_on_existing=True
    )
    assert "--break-on-existing" in build_args(настройки, "URL")


# --- отказы на бессмысленных настройках -------------------------------------


def test_отказ_на_неизвестном_разрешении():
    with pytest.raises(ValueError):
        DownloadSettings(archive_path="a", output_template="o", height=999)


def test_отказ_на_двух_источниках_куки():
    # Либо файл, либо браузер: иначе непонятно, что победит.
    with pytest.raises(ValueError):
        DownloadSettings(
            archive_path="a", output_template="o",
            cookies_file="c.txt", cookies_browser="firefox",
        )


def test_отказ_когда_нижняя_пауза_больше_верхней():
    with pytest.raises(ValueError):
        DownloadSettings(archive_path="a", output_template="o", sleep_min=60, sleep_max=10)


def test_куки_из_браузера_когда_файла_нет():
    настройки = DownloadSettings(
        archive_path="a", output_template="o", cookies_browser="firefox"
    )
    args = build_args(настройки, "URL")
    assert пары(args, "--cookies-from-browser") == ["firefox"]
    assert "--cookies" not in args


# --- проверка доступа -------------------------------------------------------


def test_проверка_берёт_один_ролик_канала():
    """Проверять надо ролик ИЗ СПИСКА КАНАЛОВ: посторонние популярные ролики
    отдаются и без входа, из-за чего первая версия проверки врала сутки.
    """
    args = build_probe_args(НАСТРОЙКИ, "https://youtube.com/@SoyuzUS/videos")
    assert "--flat-playlist" in args
    assert пары(args, "--playlist-items") == ["1"]
    assert args[-1] == "https://youtube.com/@SoyuzUS/videos"


def test_проверка_не_качает():
    args = build_probe_args(НАСТРОЙКИ, "URL")
    assert "--download-archive" not in args
    assert пары(args, "--print") == ["%(id)s"]
