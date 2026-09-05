"""English.

Ключ — русская строка из кода. Полнота проверяется тестом: пропуск здесь
не падает, а тихо показывает человеку чужой язык посреди своего.
"""

СЛОВАРЬ = {
    # --- окно целиком ---
    "Архив YouTube": "YouTube Archive",
    "Архив YouTube — {}": "YouTube Archive — {}",
    "Обзор": "Overview",
    "Каналы": "Channels",
    "Настройки": "Settings",
    "читаю состояние…": "reading status…",
    # --- обзор ---
    "Запустить": "Start",
    "Остановить": "Stop",
    "Обновить": "Refresh",
    "Запустить выкачку": "Start downloading",
    "Остановить выкачку": "Stop downloading",
    "обход работает": "worker running",
    "обход не запущен": "worker not running",
    "в архиве {} роликов": "{} videos in the archive",
    "канал {}": "channel {}",
    "последний файл {:.0f} МБ, {:.1f} МБ/с": "last file {:.0f} MB, {:.1f} MB/s",
    "отказов в этом сеансе {} — заберутся следующим проходом":
        "{} failures this session — they will be retried on the next pass",
    " · канал {} из {}": " · channel {} of {}",
    "{}: ролик {} из {}": "{}: video {} of {}",
    "осталось {}": "{} left",
    # --- каналы ---
    "Сколько уже лежит в архиве по каждому каналу:":
        "How much is already archived per channel:",
    "Канал": "Channel",
    "Файлов": "Files",
    "Объём": "Size",
    "Название канала — например, alex m": "Channel name — for example, alex m",
    "Найти": "Search",
    "ищу…": "searching…",
    "введите название": "type a name",
    "Добавить выбранный канал": "Add the selected channel",
    "Убрать": "Remove",
    "Убрать канал": "Remove channel",
    "Выбрать ролики…": "Choose videos…",
    "Список роликов канала с галочками. По умолчанию отмечены все.":
        "The channel's videos with checkboxes. Everything is checked by default.",
    "↑ Выше": "↑ Up",
    "↓ Ниже": "↓ Down",
    "Список каналов. Порядок здесь — это порядок обхода: верхний забирается первым.":
        "The channel list. The order here is the order of traversal: "
        "the top one is fetched first.",
    "Убрать «{}» из списка?\n\nСкачанное останется на диске и в учёте — канал уходит "
    "из очереди, а не из архива. Вернёте обратно — заново качать не станет.":
        "Remove “{}” from the list?\n\nWhat is downloaded stays on disk and in the "
        "records — the channel leaves the queue, not the archive. Add it back and "
        "nothing will be downloaded again.",
    "«{}» уже в списке": "“{}” is already in the list",
    "{}: добавлен «{}»": "{}: added “{}”",
    "в списке есть непонятые строки — сначала поправьте их":
        "the list contains lines that could not be read — fix them first",
    "в файле есть непонятые строки — {}": "the file contains unreadable lines — {}",
    "строка {}: {}": "line {}: {}",
    "список каналов сохранён": "channel list saved",
    "логотип": "logo",
    "Влезет": "Fits",
    "Может не влезть": "May not fit",
    "НЕ ВЛЕЗЕТ": "WILL NOT FIT",
    "да": "yes",
    "По верхней оценке «{}» займёт больше, чем есть свободного места.\n\n{}\n\n"
    "Всё равно добавить?":
        "By the upper estimate “{}” needs more space than is free.\n\n{}\n\n"
        "Add it anyway?",
    # --- настройки ---
    "Рабочая папка:": "Working folder:",
    "Обзор…": "Browse…",
    "Куда складывать архив": "Where to keep the archive",
    "Эта папка не подойдёт": "This folder will not do",
    "Сменить рабочую папку?": "Change the working folder?",
    "{}\n\n{}\n\nСменить?": "{}\n\n{}\n\nChange it?",
    "папка сменится при сохранении": "the folder will change when you save",
    "Рабочая папка сменена": "Working folder changed",
    "папка сменена; окно покажет новую после перезапуска":
        "folder changed; the window will show the new one after a restart",
    "Выкачка перейдёт на новую папку со следующего прохода.\n\n"
    "Это окно показывает прежнюю папку, пока его не перезапустить.":
        "Downloading will move to the new folder on the next pass.\n\n"
        "This window keeps showing the previous folder until it is restarted.",
    "Рабочая папка — это и склад роликов, и учёт скачанного. Смена папки ничего "
    "не переносит: новая папка начинается с того, что в ней уже лежит. Выкачка "
    "перейдёт на неё со следующего прохода.":
        "The working folder holds both the videos and the record of what has been "
        "downloaded. Changing it moves nothing: the new folder starts from whatever "
        "is already in it. Downloading moves there on the next pass.",
    "Качество:": "Quality:",
    "до {}p": "up to {}p",
    "Предпочитать AV1 (тот же вид, файл меньше)":
        "Prefer AV1 (same picture, smaller file)",
    "Забирать субтитры": "Fetch subtitles",
    "Считать зависшим после:": "Consider stalled after:",
    "Пауза между роликами, от:": "Pause between videos, from:",
    "до:": "to:",
    " с": " s",
    "Паузы между роликами берегут доступ: на потоке в тысячи запросов YouTube "
    "начинает отвечать «подтвердите, что вы не бот». Предел молчания должен быть "
    "заметно больше самой длинной паузы, иначе живую выкачку будут убивать как зависшую.":
        "Pauses between videos protect your access: after thousands of requests "
        "YouTube starts answering “confirm you are not a bot”. The silence limit must "
        "be noticeably longer than the longest pause, or a healthy download will be "
        "killed as if it had stalled.",
    "Сохранить настройки": "Save settings",
    "Вернуть как было": "Revert",
    "Не сохранил": "Not saved",
    "не сохранено": "not saved",
    "не сохранилось: {}": "not saved: {}",
    "настройки не читаются: {}": "settings cannot be read: {}",
    "настройки сохранены — вступят в силу со следующего прохода":
        "settings saved — they take effect on the next pass",
    # --- трей ---
    "Показать окно": "Show window",
    "Выйти": "Quit",
    "Окно свёрнуто в трей. Выкачка идёт сама и от окна не зависит.":
        "The window is in the tray. Downloading runs on its own and does not "
        "depend on the window.",
    # --- пуск и остановка ---
    "запустил": "started",
    "уже работает": "already running",
    "никто не работает": "nothing is running",
    "не вышло запустить: {}": "could not start: {}",
    "не вышло остановить: {}": "could not stop: {}",
    "попросил остановиться — уйдёт, договорив текущий ролик":
        "asked it to stop — it will finish the current video and go",
    "журнал не читается: {}": "the log cannot be read: {}",
    # --- окно выбора роликов ---
    "Ролики канала «{}»": "Videos of “{}”",
    "Читаю список роликов канала «{}»…": "Reading the video list of “{}”…",
    "«{}»: роликов {}": "“{}”: {} videos",
    "«{}»: список получить не удалось — сеть или вход в аккаунт. Выбор не тронут.":
        "“{}”: could not get the list — network or sign-in. Your choice is untouched.",
    "Отмечено — будет скачано. Снятая галочка не удаляет уже скачанное: "
    "она про будущие проходы.":
        "Checked means it will be downloaded. Unchecking does not delete what is "
        "already downloaded: it is about future passes.",
    "Поиск по названию": "Search by title",
    "Отметить показанные": "Check shown",
    "Снять показанные": "Uncheck shown",
    "Название": "Title",
    "Длительность": "Duration",
    "Состояние": "Status",
    "скачан": "downloaded",
    "в очереди": "queued",
    "снят": "unchecked",
    "выберите ролик": "select a video",
    "миниатюра ещё не скачана": "thumbnail not downloaded yet",
    "миниатюра не читается": "thumbnail cannot be read",
    "Открыть на YouTube": "Open on YouTube",
    "Сохранить выбор": "Save selection",
    "Закрыть": "Close",
    "Выбор не сохранён": "Selection not saved",
    "выбор сохранён": "selection saved",
    "выбор сохранён; всего снято роликов по всем каналам: {}":
        "selection saved; videos unchecked across all channels: {}",
    " — вступит в силу со следующего прохода": " — takes effect on the next pass",
    "отмечено {} из {}{}": "{} of {} checked{}",
    ", показано {}": ", {} shown",
    "; снято {}": "; {} unchecked",
    # --- единицы ---
    "{:.0f} МБ": "{:.0f} MB",
    "{:.1f} МБ/с": "{:.1f} MB/s",
    "{:.1f} ГБ": "{:.1f} GB",
    "{:.2f} ГБ": "{:.2f} GB",
    'Язык:':
        'Language:',
    'Системный язык — {}':
        'System language — {}',
    'язык сменён':
        'language changed',
    'качает':
        'downloading',
    'пауза между роликами':
        'pause between videos',
    'не запущена':
        'not running',
    'остановлена, нужен человек':
        'stopped, needs you',
    'Архив YouTube — первый запуск':
        'YouTube Archive — first run',
    'Программа будет забирать новые ролики с выбранных каналов сама.':
        'The program will fetch new videos from the channels you choose, on its own.',
    'Ролики скачиваются целиком, и места им нужно много: час видео — от 0,6 до 1,6 ГБ, а канал целиком легко занимает сотни гигабайт. Выберите папку на диске, где есть запас.':
        'Videos are downloaded in full, and they need a lot of room: an hour of video is 0.6 to 1.6 GB, and a whole channel easily takes hundreds of gigabytes. Pick a folder on a drive with room to spare.',
    'Папка не выбрана':
        'No folder chosen',
    'Готово':
        'Done',
    'Отмена':
        'Cancel',
}
