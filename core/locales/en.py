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
    '    готово {:.1f} МБ{}':
        '    done {:.1f} MB{}',
    '    отказ: {}':
        '    failure: {}',
    '  {:.2f}–{:.2f} ГБ':
        '  {:.2f}–{:.2f} GB',
    '  {}: ОТКАЗ — {}':
        '  {}: REFUSED — {}',
    '  {}: доступ есть':
        '  {}: reachable',
    '  качаю {}':
        '  downloading {}',
    '  непонятных строк в архиве: {}':
        '  unreadable lines in the archive: {}',
    '  строка {} пропущена: {}':
        '  line {} skipped: {}',
    ', {:.2f} МБ/с':
        ', {:.2f} MB/s',
    ', предпочтение AV1':
        ', AV1 preferred',
    'yt-dlp вернул пустой список при успешном коде — похоже, он устарел':
        'yt-dlp returned an empty list with a success code — it looks outdated',
    'yt-dlp сомневается в правах на вкладку канала':
        'yt-dlp doubts the rights to the channel tab',
    '{} уже есть. Перезаписать: --force':
        '{} already exists. Overwrite: --force',
    '{}: не прошло за {} попыток':
        '{}: failed after {} attempts',
    '{}: не разбирается как TOML — {}':
        '{}: not valid TOML — {}',
    '{}: не удалось записать список — {}':
        '{}: could not write the queue — {}',
    '{}: непонятых строк в переписи {}':
        '{}: unreadable lines in the listing: {}',
    '{}: остановлено — {}':
        '{}: stopped — {}',
    '{}: проверка — {}{}':
        '{}: probe — {}{}',
    '{}: пропущено по вашему выбору {}':
        '{}: skipped by your choice: {}',
    '{}: скачано {}, упало {}':
        '{}: downloaded {}, failed {}',
    'Ничего не скачано и не изменено. Качать: ytarchive run':
        'Nothing downloaded and nothing changed. To download: ytarchive run',
    'Сколько займёт час материала при измеренных битрейтах:':
        'How much an hour of material takes at the measured bitrates:',
    'архив:      {}':
        'archive:     {}',
    'беда общая для всех каналов — остальные ({}) не проверяю, ждём следующего прохода':
        'the trouble is common to all channels — skipping the rest ({}), waiting for the next pass',
    'в списке исключений непонятых строк {}: {}':
        'unreadable lines in the exclusion list: {} — {}',
    'все каналы отвечают':
        'all channels respond',
    'доступ есть, форматы отдаются':
        'reachable, formats are served',
    'достучаться до каналов':
        'reach the channels',
    'каналов с бедой: {}':
        'channels in trouble: {}',
    'каналов:    {}':
        'channels:    {}',
    'качать непрерывно, без планировщика задач':
        'download continuously, without the task scheduler',
    'качать — один проход и выход':
        'download — one pass and exit',
    'качество:   до {}p':
        'quality:     up to {}p',
    'куки:       {}':
        'cookies:     {}',
    'настройки не записались: {}':
        'settings were not written: {}',
    'настройки не созданы — запустите ещё раз, когда решите, куда качать':
        'no settings created — run again once you decide where to download',
    'настройки:  {}':
        'settings:    {}',
    'настройки: {}':
        'settings: {}',
    'не найден движок JavaScript — нужен node':
        'no JavaScript engine found — node is required',
    'не решается задача YouTube — нужен решатель EJS':
        'the YouTube challenge is unsolved — the EJS solver is required',
    'не удалось прочитать список каналов':
        'could not read the channel list',
    'неопознанный отказ':
        'unrecognised failure',
    'нет движка JavaScript':
        'no JavaScript engine',
    'нет файла настроек {}. Создать образец: ytarchive init':
        'no settings file {}. Create a sample: ytarchive init',
    'нужен вход в аккаунт YouTube':
        'a YouTube sign-in is required',
    'нужен вход в аккаунт YouTube — куки истекли или их нет':
        'a YouTube sign-in is required — the cookies expired or are missing',
    'окно наблюдения':
        'the watching window',
    'окно требует PySide6, а его нет: {}':
        'the window needs PySide6, and it is missing: {}',
    'остановлено по просьбе':
        'stopped as asked',
    'остановлено по просьбе — остальные каналы ждут следующего прохода':
        'stopped as asked — the remaining channels wait for the next pass',
    'перезаписать существующий':
        'overwrite the existing one',
    'показать, но не создавать':
        'show, but do not create',
    'попросил остановиться — демон уйдёт, договорив текущий ролик':
        'asked it to stop — it will finish the current video and go',
    'попросить работающий экземпляр остановиться':
        'ask the running copy to stop',
    'поставить:  {}':
        'install:  {}',
    'построить окно и выйти — для сборки':
        'build the window and exit — for the pipeline',
    'проверка не дала ответа':
        'the probe gave no answer',
    'пустая выдача при успешном коде возврата':
        'empty output with a success exit code',
    'сделать столько проходов и выйти (по умолчанию — пока не остановят)':
        'make this many passes and exit (by default — until asked to stop)',
    'сетевой сбой':
        'network failure',
    'следующий проход через {:.0f} мин':
        'next pass in {:.0f} min',
    'снято галочками роликов: {}':
        'videos unchecked: {}',
    'создал бы {}:\n':
        'would create {}:\n',
    'создан {} — поправьте пути и запустите: ytarchive check':
        'created {} — fix the paths and run: ytarchive check',
    'создан {}: архив в {}':
        'created {}: archive in {}',
    'создать образец настроек':
        'create a sample settings file',
    'список исключений не прочитан ({}) — качаю всё':
        'the exclusion list was not read ({}) — downloading everything',
    'строка {} пропущена: {}':
        'line {} skipped: {}',
    'уже работает: {}':
        'already running: {}',
    'уже скачано: {} роликов':
        'already downloaded: {} videos',
    'файл настроек (по умолчанию {})':
        'settings file (default {})',
    'что будет скачано, без изменений':
        'what will be downloaded, changing nothing',
    'не заданы — YouTube откажет':
        'not set — YouTube will refuse',
    '{} роликов · {:.1f} ч · {:.0f}–{:.0f} ГБ':
        '{} videos · {:.1f} h · {:.0f}–{:.0f} GB',
    'замок брошен процессом {} — забираю':
        'lock abandoned by process {} — taking it',
    'замок протух: {} молчит слишком долго — забираю':
        'stale lock: {} has been silent too long — taking it',
    'замок свободен':
        'lock is free',
    'меряю…':
        'measuring…',
    'остановлено: {}':
        'stopped: {}',
    'скачано {}':
        'downloaded {}',
    'уже работает экземпляр {} — второй не нужен':
        'copy {} is already running — a second one is not needed',
    'упало {} (заберутся следующим проходом)':
        '{} failed (they will be fetched on the next pass)',
    'Новое название. Оно же станет именем папки — она переименуется вместе с каналом.':
        'New name. It also becomes the folder name — the folder is renamed together with the channel.',
    'Переименовать канал':
        'Rename channel',
    'Переименовать…':
        'Rename…',
    'Сменить название канала вместе с его папкой.':
        'Change the channel name together with its folder.',
    'в названии есть символы, недопустимые в имени папки':
        'the name contains characters that are not allowed in a folder name',
    'идёт проход выкачки — дождитесь его конца или остановите выкачку':
        'a download pass is running — wait for it to finish or stop downloading',
    'канал переименован: «{}» → «{}»':
        'channel renamed: “{}” → “{}”',
    'канал с таким названием уже есть':
        'a channel with this name already exists',
    'название не может быть пустым':
        'the name cannot be empty',
    'название то же самое':
        'the name is the same',
    'папка «{}» уже есть — сливать две папки молча нельзя':
        'the folder “{}” already exists — two folders are never merged silently',
    'папку переименовать не вышло: {}':
        'could not rename the folder: {}',
    'такого канала в списке нет':
        'there is no such channel in the list',
    # --- установщик ---
    '    на Debian и Ubuntu сначала нужно: sudo apt-get install python3-venv':
        '    on Debian and Ubuntu first run: sudo apt-get install python3-venv',
    'Python {} — подходит.':
        'Python {} — fine.',
    '[Д/н]':
        '[Y/n]',
    '[д/Н]':
        '[y/N]',
    '{} — не найден, и я не знаю, чем его поставить на этой системе':
        '{} — not found, and I do not know how to install it on this system',
    '{} — поставьте сами: {}':
        '{} — install it yourself: {}',
    'Архив YouTube — выкачка':
        'YouTube Archive — downloader',
    'Вхолостую: ничего не тронуто.':
        'Dry run: nothing was changed.',
    'Выкачка новых роликов в фоне':
        'Downloads new videos in the background',
    'Выполнить?':
        'Go ahead?',
    'Готово.':
        'Done.',
    'Запускать выкачку при входе в систему?':
        'Start downloading when you log in?',
    'Исправьте причину и запустите установку ещё раз — сделанное не пропадёт.':
        'Fix the cause and run the installer again — what is already done will be kept.',
    'Окно архива роликов':
        'The video archive window',
    'Осталось сделать руками:':
        'Left for you to do:',
    'Остановился на шаге {}: дальше без него нельзя.':
        'Stopped at step {}: cannot continue without it.',
    'Открыть окно сейчас?':
        'Open the window now?',
    'Открыть окно:  {} {} gui':
        'Open the window: {} {} gui',
    'Отменено, ничего не тронуто.':
        'Cancelled, nothing was changed.',
    'Положить ярлык, открывающий окно?':
        'Create a shortcut that opens the window?',
    'После установки node и ffmpeg откройте новый терминал: старый их не увидит.':
        'After installing node and ffmpeg open a new terminal: the old one will not see them.',
    'Создать настройки: {} {} init':
        'Create the settings: {} {} init',
    'Спросить некого: запустите в терминале или добавьте --yes.':
        'Nobody to ask: run this in a terminal or add --yes.',
    'Установка ytarchive в {}':
        'Installing ytarchive in {}',
    'Установка ytarchive.':
        'Install ytarchive.',
    'Что будет сделано:':
        'What will be done:',
    'Что дальше — куки YouTube и первый канал — написано в INSTALL.ru.md.':
        'What comes next — YouTube cookies and the first channel — is in INSTALL.md.',
    'без окна: только командная строка и выкачка':
        'no window: command line and downloader only',
    'запускать выкачку при входе в систему':
        'start downloading when you log in',
    'не запускать выкачку при входе в систему':
        'do not start downloading at login',
    'не класть ярлык окна':
        'do not create the window shortcut',
    'не получилось: {}':
        'failed: {}',
    'не спрашивать':
        'do not ask',
    'положить ярлык окна':
        'create the window shortcut',
    'поставить {}: {}':
        'install {}: {}',
    'поставить в окружение программы: {}':
        'install into the program’s environment: {}',
    'создать окружение Python в папке программы (.venv)':
        'create a Python environment in the program folder (.venv)',
    'только показать шаги, ничего не трогая':
        'only show the steps, changing nothing',
    # --- надзор за скоростью, правила, уход за архивом ---
    '  не убрался {}: {}':
        '  could not remove {}: {}',
    '  … и ещё {} (показать все: --limit 0)':
        '  … and {} more (show all: --limit 0)',
    ' КиБ/с':
        ' KiB/s',
    '23-7 или 23:00-07:30 — пусто: всегда':
        '23-7 or 23:00-07:30 — empty: always',
    'yt-dlp {} — {}':
        'yt-dlp {} — {}',
    'yt-dlp поставлен не этой программой — обновите его тем же способом, каким ставили.':
        'yt-dlp was not installed by this program — update it the same way you installed it.',
    '{}: медленно идёт всё подряд — похоже, дело в линии. До конца прохода не снимаю; порог задаётся в [limits] crawl_speed':
        '{}: everything is slow — it looks like the connection, not the videos. No more deferring until the end of this pass; the threshold is [limits] crawl_speed',
    '{}: пропущено по правилам канала {}':
        '{}: skipped by the channel rules: {}',
    '{}: ролик {} идёт медленнее {:.0f} КБ/с уже {:.0f} мин — откладываю до следующего прохода':
        '{}: video {} has been slower than {:.0f} KB/s for {:.0f} min — deferring it to the next pass',
    'Адрес плейлиста, ролика или вкладки videos канала:':
        'Address of a playlist, a video or a channel’s videos tab:',
    'Архив YouTube — нужен человек':
        'YouTube Archive — needs you',
    'В учёте есть, файла нет — такие ролики заново не скачаются: {}':
        'Recorded but the file is missing — these will never be downloaded again: {}',
    'Выполнить':
        'Run',
    'ГГГГ-ММ-ДД — пусто: любые':
        'YYYY-MM-DD — empty: any',
    'Добавить по адресу':
        'Add by address',
    'Добавить по адресу…':
        'Add by address…',
    'Куки YouTube:':
        'YouTube cookies:',
    'Название. Оно же станет именем папки в архиве:':
        'Name. It also becomes the folder name in the archive:',
    'Не длиннее:':
        'No longer than:',
    'Не короче, не длиннее, не старше — одной строкой вместо сотни галочек.':
        'No shorter, no longer, no older — one line instead of a hundred checkboxes.',
    'Не короче:':
        'No shorter than:',
    'Не старше:':
        'No older than:',
    'Ничего не тронуто. Убрать повторные строки: ytarchive verify --apply':
        'Nothing was changed. To remove the duplicate lines: ytarchive verify --apply',
    'Ничего не тронуто. Убрать: ytarchive clean --apply':
        'Nothing was changed. To remove: ytarchive clean --apply',
    'Обновить yt-dlp':
        'Update yt-dlp',
    'Обновление yt-dlp':
        'Updating yt-dlp',
    'Один ролик в нескольких файлах: {}':
        'One video in several files: {}',
    'Откладывать загрузку медленнее:':
        'Defer downloads slower than:',
    'Плейлист, отдельный ролик или канал, которого нет в поиске.':
        'A playlist, a single video, or a channel the search does not find.',
    'Повторных строк в учёте: {} (безвредно)':
        'Duplicate lines in the record: {} (harmless)',
    'Потолок скорости:':
        'Speed limit:',
    'Правила канала — {}':
        'Channel rules — {}',
    'Правила отбора: {}':
        'Selection rules: {}',
    'Правила…':
        'Rules…',
    'Правило вычёркивает ролики из очереди, но ничего не удаляет с диска: снимете правило — ролики вернутся в очередь. Ролик, у которого длительность или дата неизвестны, правилу не подчиняется.':
        'A rule takes videos out of the queue but deletes nothing from disk: remove the rule and they return to the queue. A video whose duration or date is unknown is not affected by the rule.',
    'Сверить учёт с диском':
        'Check the record against the disk',
    'Сверка учёта с диском':
        'Record against disk',
    'Старые журналы и обломки загрузок. Сначала покажет, что уберёт.':
        'Old logs and leftovers of downloads. It shows what it would remove first.',
    'Убирать нечего.':
        'Nothing to remove.',
    'Убрать повторные строки':
        'Remove duplicate lines',
    'Убрать показанное':
        'Remove what is shown',
    'Убрать старое…':
        'Remove old files…',
    'Учёт и диск сходятся.':
        'The record and the disk agree.',
    'Файл есть, в учёте нет — такие ролики скачаются второй раз: {}':
        'File present but not recorded — these will be downloaded a second time: {}',
    'Часы работы:':
        'Working hours:',
    'Чинить нечего: остальное — решение человека, а не программы.':
        'Nothing to fix: the rest is for you to decide, not the program.',
    'Что можно убрать':
        'What can be removed',
    'без потолка':
        'no limit',
    'в учёте строк: {}, роликов на диске: {}':
        'lines in the record: {}, videos on disk: {}',
    'вне часов работы — жду до {}':
        'outside working hours — waiting until {}',
    'готово':
        'done',
    'журналов старше {} суток: {} ({:.1f} МБ)':
        'logs older than {} days: {} ({:.1f} MB)',
    'закончено с замечаниями':
        'finished with remarks',
    'идёт выкачка — учёт сейчас править нельзя ({})':
        'a download is running — the record cannot be edited now ({})',
    'из браузера {}':
        'from the {} browser',
    'из файла cookies.txt':
        'from the cookies.txt file',
    'не добавлен: {}':
        'not added: {}',
    'не ограничено':
        'no limit',
    'не проверять':
        'do not check',
    'обломков загрузок, которые уже не пригодятся: {} ({:.1f} МБ)':
        'leftovers of downloads that are no longer needed: {} ({:.1f} MB)',
    'обновить yt-dlp':
        'update yt-dlp',
    'обновлён: {} → {}':
        'updated: {} → {}',
    'папка {} не прочитана: {}':
        'folder {} could not be read: {}',
    'работаю…':
        'working…',
    'сверить учёт с файлами на диске':
        'check the record against the files on disk',
    'сколько строк каждого перечня показать (0 — все)':
        'how many lines of each list to show (0 — all)',
    'старые журналы и обломки загрузок':
        'old logs and leftovers of downloads',
    'убрано журналов старше {} суток: {}':
        'removed logs older than {} days: {}',
    'убрано повторных строк: {}; прежний учёт сохранён как {}':
        'duplicate lines removed: {}; the previous record is kept as {}',
    'убрано файлов: {}':
        'files removed: {}',
    'убрать повторные строки учёта':
        'remove duplicate lines from the record',
    'убрать, а не только показать':
        'remove, not just show',
    'уже последняя версия: {}':
        'already the latest version: {}',
    'учёт не записан: {}':
        'the record was not written: {}',
    'учёт не прочитан: {}':
        'the record could not be read: {}',
    # --- новый вид окна ---
    'YouTube не отдаёт ролики без входа в аккаунт. Выберите в настройках браузер, в котором вы вошли в YouTube, или положите файл cookies.txt.':
        'YouTube does not serve videos unless you are signed in. In the settings, choose the browser where you are signed in to YouTube, or provide a cookies.txt file.',
    '{:.2f} ТБ':
        '{:.2f} TB',
    'Архив':
        'Archive',
    'В папке архива лежат ролики в папках, которых нет в списке: {}. Так выглядит канал, переименованный в файле руками.':
        'The archive folder holds videos in folders that are not in the list: {}. This is what a channel renamed by hand in the file looks like.',
    'Дата':
        'Date',
    'Дата примерная: YouTube в списке канала пишет «3 года назад». Точная появится, когда ролик будет скачан.':
        'The date is approximate: in a channel listing YouTube says “3 years ago”. The exact one appears once the video is downloaded.',
    'Добавить канал':
        'Add a channel',
    'Журнал':
        'Log',
    'Каналов пока нет. Добавьте первый — программа покажет, сколько в нём роликов и хватит ли места, ещё до того, как начнёт качать.':
        'No channels yet. Add the first one — the program shows how many videos it has and whether there is room for them before it downloads anything.',
    'Мои каналы':
        'My channels',
    'Осторожность':
        'Caution',
    'Открыть настройки':
        'Open settings',
    'Показать':
        'Show',
    'Сеть и расписание':
        'Network and schedule',
    'Скрыть':
        'Hide',
    'Уход за архивом':
        'Archive upkeep',
    'Что качать':
        'What to download',
    'ждёт следующего прохода':
        'waiting for the next pass',
    'каналов в списке':
        'channels in the list',
    'объём архива':
        'archive size',
    'роликов в архиве':
        'videos in the archive',
    'свободно на диске':
        'free on disk',
    'yt-dlp не получает ролики, только раскадровки — обновите yt-dlp кнопкой в настройках':
        'yt-dlp gets only storyboards, not the videos — update yt-dlp with the button in the settings',
    # --- библиотека, пропавшие с YouTube, медиасервер ---
    '{}: в списке канала на YouTube больше нет роликов из архива: {}':
        '{}: videos from the archive that are no longer in the channel’s list on YouTube: {}',
    'Библиотека':
        'Library',
    'Все каналы':
        'All channels',
    'Готовить для медиасервера (Jellyfin, Kodi, Plex)':
        'Prepare for a media server (Jellyfin, Kodi, Plex)',
    'Комментарии ложатся в файл .info.json рядом с роликом. Это сотни лишних запросов на ролик.':
        'Comments go into an .info.json file next to the video. That is hundreds of extra requests per video.',
    'Ничего не записано. Записать: ytarchive nfo --apply':
        'Nothing was written. To write: ytarchive nfo --apply',
    'Описания есть у всего.':
        'Everything already has a description file.',
    'Поиск по названию — по всем каналам':
        'Search by title — across all channels',
    'Показать в папке':
        'Show in folder',
    'Размер':
        'Size',
    'Ролики из архива, которых больше нет в списке канала: удалены, скрыты или лежат на другой вкладке канала (Shorts, трансляции).':
        'Videos from the archive that are no longer in the channel’s list: deleted, hidden, or sitting on another tab of the channel (Shorts, live streams).',
    'Рядом с роликом кладутся обложка и файл .nfo: сервер показывает канал сериалом. Для уже скачанного — команда ytarchive nfo --apply.':
        'A cover image and an .nfo file are placed next to each video: the server then shows the channel as a series. For what is already downloaded, use ytarchive nfo --apply.',
    'Смотреть':
        'Watch',
    'Сохранять комментарии (заметно дольше)':
        'Save comments (noticeably slower)',
    'Существующие описания не трогаются. На большом архиве это минуты: из каждого ролика читается его описание.':
        'Existing description files are left alone. On a large archive this takes minutes: the description is read out of every video.',
    'Только те, которых нет на YouTube':
        'Only those no longer on YouTube',
    'дописано описаний для медиасервера: {}':
        'description files added for the media server: {}',
    'записано описаний: {}':
        'description files written: {}',
    'записать, а не только посчитать':
        'write, not just count',
    'из них нет на YouTube: {}':
        'of them no longer on YouTube: {}',
    'не записалось: {}':
        'could not be written: {}',
    'нет в списке канала':
        'not in the channel’s list',
    'описание ролика':
        'video description',
    'описания для медиасервера':
        'description files for a media server',
    'показано {} из {}':
        'showing {} of {}',
    'роликов без описания: {}; каналов без описания: {}':
        'videos without a description file: {}; channels without one: {}',
}
