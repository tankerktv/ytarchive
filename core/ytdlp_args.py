"""Сборка аргументов yt-dlp.

Чистая функция: на входе настройки, на выходе список строк. Ни одного вызова
наружу — поэтому весь набор ключей, выстраданный за неделю выкачки, проверяется
тестами за миллисекунды, а не очередной ночью скачивания.

Каждый неочевидный ключ снабжён объяснением, ЗАЧЕМ он здесь. Без этого
следующий человек — или ты через месяц — аккуратно «почистит» набор
и вернёт себе неделю отладки.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Потолки разрешения, которые вообще имеет смысл предлагать.
ALLOWED_HEIGHTS = (720, 1080, 1440, 2160)


@dataclass(frozen=True)
class DownloadSettings:
    """Всё, что влияет на набор ключей."""

    archive_path: str
    output_template: str
    cookies_file: str | None = None
    cookies_browser: str | None = None
    height: int = 1080
    prefer_av1: bool = True
    write_subs: bool = True
    sub_langs: tuple[str, ...] = ("ru", "en")
    #: Паузы между роликами. Не украшение: на потоке в 1872 запроса YouTube
    #: начинает отвечать «подтвердите, что вы не бот». За неделю с этими
    #: паузами сбоило 964 ролика, и все забрались повторами.
    sleep_min: int = 15
    sleep_max: int = 45
    sleep_requests: int = 2
    #: Предел на сетевую операцию. Сам по себе зависание не лечит — мы ловили
    #: процессы, которых он не брал, — но без него их было бы больше.
    socket_timeout: int = 30
    retries: int = 10
    fragment_retries: int = 20
    #: Быстрый проход. Включать ТОЛЬКО когда `planner.is_incremental_safe`
    #: сказал «да»: на недособранном архиве он обрывается на первом же
    #: скачанном ролике и остальное не забирает никогда.
    break_on_existing: bool = False
    #: Потолок скорости, КиБ/с. Ноль — без потолка. Нужен тем, у кого выкачка
    #: делит линию с остальным домом: без него она забирает всё.
    rate_limit: int = 0
    #: Сохранять комментарии рядом с роликом, в `.info.json`.
    write_comments: bool = False
    #: Класть рядом с роликом обложку серии — для медиасерверов.
    write_thumbnail: bool = False
    extra: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.height not in ALLOWED_HEIGHTS:
            raise ValueError(f"потолок разрешения {self.height} не из {ALLOWED_HEIGHTS}")
        if self.cookies_file and self.cookies_browser:
            raise ValueError("куки берутся либо файлом, либо из браузера, но не оба сразу")
        if self.sleep_min > self.sleep_max:
            raise ValueError("нижняя граница паузы больше верхней")
        if self.sleep_min < 0 or self.sleep_requests < 0:
            raise ValueError("паузы не могут быть отрицательными")
        if self.socket_timeout <= 0:
            raise ValueError("предел сетевой операции должен быть положительным")
        if self.rate_limit < 0:
            raise ValueError("потолок скорости не может быть отрицательным")


def thumbnail_template(output_template: str) -> str:
    """Шаблон имени обложки: то же имя, что у ролика, с хвостом `-thumb`."""
    хвост = ".%(ext)s"
    if output_template.endswith(хвост):
        return output_template[: -len(хвост)] + "-thumb" + хвост
    return output_template + "-thumb"


def format_selector(height: int) -> str:
    """Что качать. Три запасных варианта на случай, если первый недоступен."""
    return f"bv*[height<={height}]+ba/b[height<={height}]/bv*+ba/b"


def format_sort(height: int, prefer_av1: bool) -> str:
    """Чем руководствоваться при выборе среди подходящих.

    AV1 при равном разрешении даёт заметно меньший файл — на нашем архиве это
    разница между нижней и верхней границей вилки, сотни гигабайт.
    """
    parts = [f"res:{height}"]
    if prefer_av1:
        parts.append("vcodec:av01")
    parts.append("acodec:opus")
    return ",".join(parts)


def build_args(settings: DownloadSettings, url: str) -> list[str]:
    """Собрать полный список аргументов для одного прохода по каналу."""
    args: list[str] = []

    if settings.cookies_file:
        args += ["--cookies", settings.cookies_file]
    elif settings.cookies_browser:
        args += ["--cookies-from-browser", settings.cookies_browser]

    args += [
        # Без движка JavaScript YouTube отдаёт только раскадровки: сам ролик
        # не достаётся вовсе. Решатель задач ставится пакетом yt-dlp-ejs.
        "--js-runtimes", "node",
        # Проверка прав на вкладку ложно срабатывает при сетевых сбоях —
        # ловили 29.08, когда падал DNS.
        "--extractor-args", "youtubetab:skip=authcheck",
        "--socket-timeout", str(settings.socket_timeout),
        "--download-archive", settings.archive_path,
        "-f", format_selector(settings.height),
        "-S", format_sort(settings.height, settings.prefer_av1),
        "--merge-output-format", "mkv",
        "-o", settings.output_template,
        "--embed-metadata",
        "--embed-thumbnail",
        "--embed-chapters",
        "--no-overwrites",
        "--continue",
        # Отказ на одном ролике не должен прекращать проход по каналу:
        # упавший просто не попадёт в архив и заберётся следующим разом.
        "--ignore-errors",
        "--no-abort-on-error",
        "--retries", str(settings.retries),
        "--fragment-retries", str(settings.fragment_retries),
        "--sleep-requests", str(settings.sleep_requests),
        "--min-sleep-interval", str(settings.sleep_min),
        "--max-sleep-interval", str(settings.sleep_max),
        # Построчный вывод: без него прогресс идёт возвратом каретки в одну
        # строку, и надзорщик не видит признаков жизни.
        "--newline",
    ]

    if settings.write_subs:
        args += ["--write-subs", "--sub-langs", ",".join(settings.sub_langs), "--embed-subs"]

    if settings.break_on_existing:
        args.append("--break-on-existing")

    if settings.rate_limit:
        args += ["--limit-rate", f"{settings.rate_limit}K"]

    if settings.write_comments:
        # Комментарии yt-dlp отдаёт только внутри описания ролика целиком,
        # отдельного файла для них нет.
        args += ["--write-comments", "--write-info-json"]

    if settings.write_thumbnail:
        # Имя с хвостом `-thumb` — так обложку серии ищут Kodi и Jellyfin.
        # Без `--write-thumbnail` картинка после вшивания в файл удаляется.
        args += [
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            "-o", "thumbnail:" + thumbnail_template(settings.output_template),
        ]

    args += list(settings.extra)
    args.append(url)
    return args


def build_batch_args(settings: DownloadSettings, batch_file: str) -> list[str]:
    """Аргументы для загрузки готового списка роликов.

    Отличается от `build_args` одним: вместо адреса канала подаётся файл
    со списком. Это единственный способ учесть исключения — отдав yt-dlp
    адрес канала, мы отдаём ему и решение, что качать.

    Список подаётся файлом, а не строкой аргументов: у канала бывает
    шестьсот роликов, и в командную строку они не влезут.
    """
    args = [a for a in build_args(settings, "") if a != ""]
    # Быстрый проход тут бессмыслен: список уже отфильтрован нами,
    # обрывать его на первом знакомом ролике нечего.
    if "--break-on-existing" in args:
        args.remove("--break-on-existing")
    return [*args, "--batch-file", batch_file]


#: Строка переписи. Название последним: в нём бывает что угодно, включая
#: табуляцию. Разбирает её `core.videos.parse_listing` — менять вместе.
LISTING_FORMAT = "%(id)s\t%(duration)s\t%(upload_date)s\t%(title)s"


def build_enumerate_args(settings: DownloadSettings, url: str) -> list[str]:
    """Аргументы для переписи канала: идентификаторы и названия.

    Названия нужны окну выбора роликов — по одному идентификатору человек
    не поймёт, что снимает.
    """
    args: list[str] = []
    if settings.cookies_file:
        args += ["--cookies", settings.cookies_file]
    elif settings.cookies_browser:
        args += ["--cookies-from-browser", settings.cookies_browser]

    args += [
        "--js-runtimes", "node",
        # approximate_date: без него перепись не отдаёт дату вовсе, и правило
        # «не старше» пришлось бы проверять загрузкой каждого ролика. Дата
        # примерная — YouTube пишет «3 года назад», — но запросов не стоит.
        "--extractor-args", "youtubetab:skip=authcheck;approximate_date",
        "--socket-timeout", str(settings.socket_timeout),
        "--flat-playlist",
        "--print", LISTING_FORMAT,
        "--no-warnings",
        url,
    ]
    return args


def build_probe_args(settings: DownloadSettings, url: str) -> list[str]:
    """Аргументы для проверки доступа: взять один свежий ролик канала.

    Именно канала из списка, а не постороннего: посторонние популярные ролики
    отдаются и без входа в аккаунт, из-за чего первая версия проверки врала.
    """
    args: list[str] = []
    if settings.cookies_file:
        args += ["--cookies", settings.cookies_file]
    elif settings.cookies_browser:
        args += ["--cookies-from-browser", settings.cookies_browser]

    args += [
        "--js-runtimes", "node",
        "--extractor-args", "youtubetab:skip=authcheck",
        "--socket-timeout", str(settings.socket_timeout),
        "--flat-playlist",
        "--playlist-items", "1",
        "--print", "%(id)s",
        "--no-warnings",
        url,
    ]
    return args


#: Имя файла внутри папки канала: дата, название, идентификатор.
FILE_TEMPLATE = "%(upload_date>%Y-%m-%d)s - %(title).150B [%(id)s].%(ext)s"


def output_template_for(base_dir: str, folder: str) -> str:
    """Шаблон пути для роликов одного канала.

    Папка берётся из имени канала В НАШЕМ СПИСКЕ, а не из названия, которое
    отдаёт YouTube. Раньше в шаблоне стояло `%(channel)s`, и это вскрылось
    через месяц работы: два канала из пяти переименовались, и всё новое стало
    ложиться в папки с новыми названиями. `SoyuzUS` застыл на 210 роликах,
    рядом вырос `Soyuz` — архив раскололся молча, а окно, считающее файлы
    по имени из списка, начало занижать.

    Название на YouTube меняет владелец канала, когда захочет. Имя в списке
    меняет только хозяин архива.

    Знак процента в имени удваивается: для yt-dlp он начинает подстановку,
    и канал «100% игры» иначе дал бы ошибку шаблона на каждом ролике.
    """
    from pathlib import PurePath

    безопасное = folder.replace("%", "%%")
    return str(PurePath(base_dir) / безопасное / FILE_TEMPLATE)
