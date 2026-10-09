"""Español.

Ключ — русская строка из кода. Полнота проверяется тестом: пропуск здесь
не падает, а тихо показывает человеку чужой язык посреди своего.

Переведено без носителя языка: если что-то звучит неловко, правьте смело.
"""

СЛОВАРЬ = {
    'Архив YouTube':
        'Archivo de YouTube',
    'Архив YouTube — {}':
        'Archivo de YouTube — {}',
    'Обзор':
        'Resumen',
    'Каналы':
        'Canales',
    'Настройки':
        'Ajustes',
    'читаю состояние…':
        'leyendo el estado…',
    'Запустить':
        'Iniciar',
    'Остановить':
        'Detener',
    'Запустить выкачку':
        'Iniciar la descarga',
    'Остановить выкачку':
        'Detener la descarga',
    'обход работает':
        'el recorrido está activo',
    'обход не запущен':
        'el recorrido no está activo',
    'в архиве {} роликов':
        '{} vídeos en el archivo',
    'канал {}':
        'canal {}',
    'последний файл {:.0f} МБ, {:.1f} МБ/с':
        'último archivo {:.0f} MB, {:.1f} MB/s',
    'отказов в этом сеансе {} — заберутся следующим проходом':
        '{} fallos en esta sesión: se recogerán en la siguiente pasada',
    ' · канал {} из {}':
        ' · canal {} de {}',
    '{}: ролик {} из {}':
        '{}: vídeo {} de {}',
    'осталось {}':
        'quedan {}',
    'Канал':
        'Canal',
    'Файлов':
        'Archivos',
    'Объём':
        'Tamaño',
    'Название канала — например, alex m':
        'Nombre del canal, por ejemplo alex m',
    'Найти':
        'Buscar',
    'ищу…':
        'buscando…',
    'введите название':
        'escriba un nombre',
    'Добавить выбранный канал':
        'Añadir el canal seleccionado',
    'Убрать':
        'Quitar',
    'Убрать канал':
        'Quitar canal',
    'Выбрать ролики…':
        'Elegir vídeos…',
    'Список роликов канала с галочками. По умолчанию отмечены все.':
        'Los vídeos del canal con casillas. Todo está marcado por omisión.',
    '↑ Выше':
        '↑ Subir',
    '↓ Ниже':
        '↓ Bajar',
    'Список каналов. Порядок здесь — это порядок обхода: верхний забирается первым.':
        'La lista de canales. El orden es el de recorrido: el primero se descarga antes.',
    'Убрать «{}» из списка?\n\nСкачанное останется на диске и в учёте — канал уходит из очереди, а не из архива. Вернёте обратно — заново качать не станет.':
        '¿Quitar «{}» de la lista?\n\nLo descargado permanece en el disco y en el registro: el canal sale de la cola, no del archivo. Si lo vuelve a añadir, no se descargará de nuevo.',
    '«{}» уже в списке':
        '«{}» ya está en la lista',
    '{}: добавлен «{}»':
        '{}: se añadió «{}»',
    'в списке есть непонятые строки — сначала поправьте их':
        'la lista tiene líneas ilegibles: corríjalas primero',
    'в файле есть непонятые строки — {}':
        'el archivo tiene líneas ilegibles: {}',
    'строка {}: {}':
        'línea {}: {}',
    'список каналов сохранён':
        'lista de canales guardada',
    'Влезет':
        'Cabe',
    'Может не влезть':
        'Puede no caber',
    'НЕ ВЛЕЗЕТ':
        'NO CABE',
    'да':
        'sí',
    'По верхней оценке «{}» займёт больше, чем есть свободного места.\n\n{}\n\nВсё равно добавить?':
        'Según la estimación superior, «{}» ocupa más de lo que hay libre.\n\n{}\n\n¿Añadirlo de todos modos?',
    'Рабочая папка:':
        'Carpeta de trabajo:',
    'Обзор…':
        'Examinar…',
    'Куда складывать архив':
        'Dónde guardar el archivo',
    'Эта папка не подойдёт':
        'Esta carpeta no sirve',
    'Сменить рабочую папку?':
        '¿Cambiar la carpeta de trabajo?',
    '{}\n\n{}\n\nСменить?':
        '{}\n\n{}\n\n¿Cambiarla?',
    'папка сменится при сохранении':
        'la carpeta cambiará al guardar',
    'Рабочая папка сменена':
        'Carpeta de trabajo cambiada',
    'папка сменена; окно покажет новую после перезапуска':
        'carpeta cambiada; la ventana mostrará la nueva tras reiniciarla',
    'Выкачка перейдёт на новую папку со следующего прохода.\n\nЭто окно показывает прежнюю папку, пока его не перезапустить.':
        'La descarga pasará a la carpeta nueva en la siguiente pasada.\n\nEsta ventana sigue mostrando la anterior hasta que se reinicie.',
    'Рабочая папка — это и склад роликов, и учёт скачанного. Смена папки ничего не переносит: новая папка начинается с того, что в ней уже лежит. Выкачка перейдёт на неё со следующего прохода.':
        'La carpeta de trabajo guarda tanto los vídeos como el registro de lo descargado. Cambiarla no mueve nada: la carpeta nueva empieza con lo que ya tenga dentro. La descarga pasa allí en la siguiente pasada.',
    'Качество:':
        'Calidad:',
    'до {}p':
        'hasta {}p',
    'Предпочитать AV1 (тот же вид, файл меньше)':
        'Preferir AV1 (misma imagen, archivo menor)',
    'Забирать субтитры':
        'Descargar subtítulos',
    'Считать зависшим после:':
        'Considerar colgado tras:',
    'Пауза между роликами, от:':
        'Pausa entre vídeos, desde:',
    'до:':
        'hasta:',
    ' с':
        ' s',
    'Паузы между роликами берегут доступ: на потоке в тысячи запросов YouTube начинает отвечать «подтвердите, что вы не бот». Предел молчания должен быть заметно больше самой длинной паузы, иначе живую выкачку будут убивать как зависшую.':
        'Las pausas entre vídeos protegen el acceso: tras miles de peticiones YouTube empieza a responder «confirme que no es un robot». El límite de silencio debe superar con holgura la pausa más larga, o se matará una descarga sana como si estuviera colgada.',
    'Сохранить настройки':
        'Guardar ajustes',
    'Вернуть как было':
        'Deshacer',
    'Не сохранил':
        'No se guardó',
    'не сохранено':
        'no guardado',
    'не сохранилось: {}':
        'no se guardó: {}',
    'настройки не читаются: {}':
        'no se pueden leer los ajustes: {}',
    'настройки сохранены — вступят в силу со следующего прохода':
        'ajustes guardados: se aplican en la siguiente pasada',
    'Показать окно':
        'Mostrar la ventana',
    'Выйти':
        'Salir',
    'Окно свёрнуто в трей. Выкачка идёт сама и от окна не зависит.':
        'La ventana está en la bandeja. La descarga sigue sola y no depende de la ventana.',
    'запустил':
        'iniciado',
    'уже работает':
        'ya está funcionando',
    'никто не работает':
        'no hay nada funcionando',
    'не вышло запустить: {}':
        'no se pudo iniciar: {}',
    'не вышло остановить: {}':
        'no se pudo detener: {}',
    'попросил остановиться — уйдёт, договорив текущий ролик':
        'se pidió detener: terminará el vídeo actual y saldrá',
    'журнал не читается: {}':
        'no se puede leer el registro: {}',
    'Ролики канала «{}»':
        'Vídeos de «{}»',
    'Читаю список роликов канала «{}»…':
        'Leyendo la lista de vídeos de «{}»…',
    '«{}»: роликов {}':
        '«{}»: {} vídeos',
    '«{}»: список получить не удалось — сеть или вход в аккаунт. Выбор не тронут.':
        '«{}»: no se pudo obtener la lista (red o inicio de sesión). Su selección queda intacta.',
    'Отмечено — будет скачано. Снятая галочка не удаляет уже скачанное: она про будущие проходы.':
        'Marcado significa que se descargará. Desmarcar no borra lo ya descargado: afecta a las pasadas futuras.',
    'Поиск по названию':
        'Buscar por título',
    'Отметить показанные':
        'Marcar los mostrados',
    'Снять показанные':
        'Desmarcar los mostrados',
    'Название':
        'Título',
    'Длительность':
        'Duración',
    'Состояние':
        'Estado',
    'скачан':
        'descargado',
    'в очереди':
        'en cola',
    'снят':
        'desmarcado',
    'выберите ролик':
        'elija un vídeo',
    'миниатюра ещё не скачана':
        'miniatura aún no descargada',
    'миниатюра не читается':
        'no se puede leer la miniatura',
    'Открыть на YouTube':
        'Abrir en YouTube',
    'Сохранить выбор':
        'Guardar la selección',
    'Закрыть':
        'Cerrar',
    'Выбор не сохранён':
        'Selección no guardada',
    'выбор сохранён':
        'selección guardada',
    'выбор сохранён; всего снято роликов по всем каналам: {}':
        'selección guardada; vídeos desmarcados en todos los canales: {}',
    ' — вступит в силу со следующего прохода':
        ' — se aplica en la siguiente pasada',
    'отмечено {} из {}{}':
        '{} de {} marcados{}',
    ', показано {}':
        ', {} mostrados',
    '; снято {}':
        '; {} desmarcados',
    '{:.0f} МБ':
        '{:.0f} MB',
    '{:.1f} МБ/с':
        '{:.1f} MB/s',
    '{:.1f} ГБ':
        '{:.1f} GB',
    'Язык:':
        'Idioma:',
    'Системный язык — {}':
        'Idioma del sistema — {}',
    'язык сменён':
        'idioma cambiado',
    'качает':
        'descargando',
    'пауза между роликами':
        'pausa entre vídeos',
    'не запущена':
        'no está en marcha',
    'остановлена, нужен человек':
        'detenida, hace falta usted',
    'Архив YouTube — первый запуск':
        'Archivo de YouTube — primer arranque',
    'Программа будет забирать новые ролики с выбранных каналов сама.':
        'El programa recogerá por su cuenta los vídeos nuevos de los canales que elija.',
    'Ролики скачиваются целиком, и места им нужно много: час видео — от 0,6 до 1,6 ГБ, а канал целиком легко занимает сотни гигабайт. Выберите папку на диске, где есть запас.':
        'Los vídeos se descargan enteros y ocupan mucho: una hora de vídeo son de 0,6 a 1,6 GB, y un canal entero llega con facilidad a cientos de gigabytes. Elija una carpeta en un disco con holgura.',
    'Папка не выбрана':
        'Ninguna carpeta elegida',
    'Готово':
        'Listo',
    'Отмена':
        'Cancelar',
    '    готово {:.1f} МБ{}':
        '    listo {:.1f} MB{}',
    '    отказ: {}':
        '    fallo: {}',
    '  {:.2f}–{:.2f} ГБ':
        '  {:.2f}–{:.2f} GB',
    '  {}: ОТКАЗ — {}':
        '  {}: RECHAZADO — {}',
    '  {}: доступ есть':
        '  {}: accesible',
    '  качаю {}':
        '  descargando {}',
    '  непонятных строк в архиве: {}':
        '  líneas ilegibles en el archivo: {}',
    '  строка {} пропущена: {}':
        '  línea {} omitida: {}',
    ', {:.2f} МБ/с':
        ', {:.2f} MB/s',
    ', предпочтение AV1':
        ', con preferencia por AV1',
    'yt-dlp вернул пустой список при успешном коде — похоже, он устарел':
        'yt-dlp devolvió una lista vacía con código de éxito: parece anticuado',
    'yt-dlp сомневается в правах на вкладку канала':
        'yt-dlp duda de los permisos sobre la pestaña del canal',
    '{} уже есть. Перезаписать: --force':
        '{} ya existe. Sobrescribir: --force',
    '{}: не прошло за {} попыток':
        '{}: no salió en {} intentos',
    '{}: не разбирается как TOML — {}':
        '{}: no es TOML válido — {}',
    '{}: не удалось записать список — {}':
        '{}: no se pudo escribir la cola — {}',
    '{}: непонятых строк в переписи {}':
        '{}: líneas ilegibles en el listado: {}',
    '{}: остановлено — {}':
        '{}: detenido — {}',
    '{}: проверка — {}{}':
        '{}: comprobación — {}{}',
    '{}: пропущено по вашему выбору {}':
        '{}: omitidos por su elección: {}',
    '{}: скачано {}, упало {}':
        '{}: descargados {}, fallidos {}',
    'Ничего не скачано и не изменено. Качать: ytarchive run':
        'No se descargó ni cambió nada. Para descargar: ytarchive run',
    'Сколько займёт час материала при измеренных битрейтах:':
        'Cuánto ocupa una hora de material con los bitrates medidos:',
    'архив:      {}':
        'archivo:     {}',
    'беда общая для всех каналов — остальные ({}) не проверяю, ждём следующего прохода':
        'el problema afecta a todos los canales: omito los demás ({}) y espero a la siguiente pasada',
    'в списке исключений непонятых строк {}: {}':
        'líneas ilegibles en la lista de exclusiones: {} — {}',
    'все каналы отвечают':
        'todos los canales responden',
    'доступ есть, форматы отдаются':
        'accesible, entrega formatos',
    'достучаться до каналов':
        'llegar a los canales',
    'каналов с бедой: {}':
        'canales con problemas: {}',
    'каналов:    {}':
        'canales:     {}',
    'качать непрерывно, без планировщика задач':
        'descargar sin parar, sin el programador de tareas',
    'качать — один проход и выход':
        'descargar: una pasada y salir',
    'качество:   до {}p':
        'calidad:     hasta {}p',
    'куки:       {}':
        'cookies:     {}',
    'настройки не записались: {}':
        'no se escribieron los ajustes: {}',
    'настройки не созданы — запустите ещё раз, когда решите, куда качать':
        'no se crearon ajustes: vuelva a ejecutarlo cuando decida dónde descargar',
    'настройки:  {}':
        'ajustes:     {}',
    'настройки: {}':
        'ajustes: {}',
    'не найден движок JavaScript — нужен node':
        'no se encontró motor de JavaScript: hace falta node',
    'не решается задача YouTube — нужен решатель EJS':
        'no se resuelve el reto de YouTube: hace falta el resolvedor EJS',
    'не удалось прочитать список каналов':
        'no se pudo leer la lista de canales',
    'неопознанный отказ':
        'fallo no identificado',
    'нет движка JavaScript':
        'sin motor de JavaScript',
    'нет файла настроек {}. Создать образец: ytarchive init':
        'no hay archivo de ajustes {}. Cree uno de muestra: ytarchive init',
    'нужен вход в аккаунт YouTube':
        'hace falta iniciar sesión en YouTube',
    'нужен вход в аккаунт YouTube — куки истекли или их нет':
        'hace falta iniciar sesión en YouTube: las cookies caducaron o no están',
    'окно наблюдения':
        'la ventana de seguimiento',
    'окно требует PySide6, а его нет: {}':
        'la ventana necesita PySide6 y no está: {}',
    'остановлено по просьбе':
        'detenido a petición',
    'остановлено по просьбе — остальные каналы ждут следующего прохода':
        'detenido a petición: los demás canales esperan a la siguiente pasada',
    'перезаписать существующий':
        'sobrescribir el existente',
    'показать, но не создавать':
        'mostrar, sin crear nada',
    'попросил остановиться — демон уйдёт, договорив текущий ролик':
        'se pidió detener: terminará el vídeo actual y saldrá',
    'попросить работающий экземпляр остановиться':
        'pedir a la copia en marcha que se detenga',
    'поставить:  {}':
        'instalar:  {}',
    'построить окно и выйти — для сборки':
        'construir la ventana y salir: para la integración',
    'проверка не дала ответа':
        'la comprobación no dio respuesta',
    'пустая выдача при успешном коде возврата':
        'salida vacía con código de éxito',
    'сделать столько проходов и выйти (по умолчанию — пока не остановят)':
        'hacer tantas pasadas y salir (por omisión: hasta que se le pida parar)',
    'сетевой сбой':
        'fallo de red',
    'следующий проход через {:.0f} мин':
        'siguiente pasada en {:.0f} min',
    'снято галочками роликов: {}':
        'vídeos desmarcados: {}',
    'создал бы {}:\n':
        'crearía {}:\n',
    'создан {} — поправьте пути и запустите: ytarchive check':
        'creado {}: corrija las rutas y ejecute: ytarchive check',
    'создан {}: архив в {}':
        'creado {}: archivo en {}',
    'создать образец настроек':
        'crear un archivo de ajustes de muestra',
    'список исключений не прочитан ({}) — качаю всё':
        'no se leyó la lista de exclusiones ({}): se descarga todo',
    'строка {} пропущена: {}':
        'línea {} omitida: {}',
    'уже работает: {}':
        'ya está en marcha: {}',
    'уже скачано: {} роликов':
        'ya descargados: {} vídeos',
    'файл настроек (по умолчанию {})':
        'archivo de ajustes (por omisión {})',
    'что будет скачано, без изменений':
        'qué se descargaría, sin cambiar nada',
    'не заданы — YouTube откажет':
        'sin definir: YouTube lo rechazará',
    '{} роликов · {:.1f} ч · {:.0f}–{:.0f} ГБ':
        '{} vídeos · {:.1f} h · {:.0f}–{:.0f} GB',
    'замок брошен процессом {} — забираю':
        'cerrojo abandonado por el proceso {}: lo tomo',
    'замок протух: {} молчит слишком долго — забираю':
        'cerrojo caducado: {} lleva demasiado callado, lo tomo',
    'замок свободен':
        'el cerrojo está libre',
    'меряю…':
        'midiendo…',
    'остановлено: {}':
        'detenido: {}',
    'скачано {}':
        'descargados {}',
    'уже работает экземпляр {} — второй не нужен':
        'la copia {} ya está en marcha: no hace falta otra',
    'упало {} (заберутся следующим проходом)':
        '{} fallidos (se recogerán en la siguiente pasada)',
    'Новое название. Оно же станет именем папки — она переименуется вместе с каналом.':
        'Nombre nuevo. Será también el nombre de la carpeta: se renombra junto con el canal.',
    'Переименовать канал':
        'Renombrar canal',
    'Переименовать…':
        'Renombrar…',
    'Сменить название канала вместе с его папкой.':
        'Cambiar el nombre del canal junto con su carpeta.',
    'в названии есть символы, недопустимые в имени папки':
        'el nombre contiene caracteres no permitidos en nombres de carpeta',
    'идёт проход выкачки — дождитесь его конца или остановите выкачку':
        'hay una pasada en curso: espere a que termine o detenga la descarga',
    'канал переименован: «{}» → «{}»':
        'canal renombrado: «{}» → «{}»',
    'канал с таким названием уже есть':
        'ya existe un canal con ese nombre',
    'название не может быть пустым':
        'el nombre no puede estar vacío',
    'название то же самое':
        'el nombre es el mismo',
    'папка «{}» уже есть — сливать две папки молча нельзя':
        'la carpeta «{}» ya existe: dos carpetas nunca se fusionan en silencio',
    'папку переименовать не вышло: {}':
        'no se pudo renombrar la carpeta: {}',
    'такого канала в списке нет':
        'ese canal no está en la lista',
    # --- установщик ---
    '    на Debian и Ubuntu сначала нужно: sudo apt-get install python3-venv':
        '    en Debian y Ubuntu primero: sudo apt-get install python3-venv',
    'Python {} — подходит.':
        'Python {} — sirve.',
    '[Д/н]':
        '[S/n]',
    '[д/Н]':
        '[s/N]',
    '{} — не найден, и я не знаю, чем его поставить на этой системе':
        '{} — no se encontró, y no sé con qué instalarlo en este sistema',
    '{} — поставьте сами: {}':
        '{} — instálelo usted: {}',
    'Архив YouTube — выкачка':
        'Archivo de YouTube — descarga',
    'Вхолостую: ничего не тронуто.':
        'Simulación: no se ha tocado nada.',
    'Выкачка новых роликов в фоне':
        'Descarga los vídeos nuevos en segundo plano',
    'Выполнить?':
        '¿Ejecutar?',
    'Готово.':
        'Listo.',
    'Запускать выкачку при входе в систему?':
        '¿Iniciar la descarga al iniciar sesión?',
    'Исправьте причину и запустите установку ещё раз — сделанное не пропадёт.':
        'Corrija la causa y vuelva a ejecutar la instalación: lo ya hecho no se pierde.',
    'Окно архива роликов':
        'Ventana del archivo de vídeos',
    'Осталось сделать руками:':
        'Queda por hacer a mano:',
    'Остановился на шаге {}: дальше без него нельзя.':
        'Detenido en el paso {}: sin él no se puede continuar.',
    'Открыть окно сейчас?':
        '¿Abrir la ventana ahora?',
    'Открыть окно:  {} {} gui':
        'Abrir la ventana: {} {} gui',
    'Отменено, ничего не тронуто.':
        'Cancelado, no se ha tocado nada.',
    'Положить ярлык, открывающий окно?':
        '¿Crear un acceso directo que abra la ventana?',
    'После установки node и ffmpeg откройте новый терминал: старый их не увидит.':
        'Tras instalar node y ffmpeg abra una terminal nueva: la antigua no los verá.',
    'Создать настройки: {} {} init':
        'Crear los ajustes: {} {} init',
    'Спросить некого: запустите в терминале или добавьте --yes.':
        'No hay a quién preguntar: ejecútelo en una terminal o añada --yes.',
    'Установка ytarchive в {}':
        'Instalando ytarchive en {}',
    'Установка ytarchive.':
        'Instalar ytarchive.',
    'Что будет сделано:':
        'Qué se va a hacer:',
    'Что дальше — куки YouTube и первый канал — написано в INSTALL.ru.md.':
        'Lo que sigue — las cookies de YouTube y el primer canal — está en INSTALL.md.',
    'без окна: только командная строка и выкачка':
        'sin ventana: solo línea de órdenes y descarga',
    'запускать выкачку при входе в систему':
        'iniciar la descarga al iniciar sesión',
    'не запускать выкачку при входе в систему':
        'no iniciar la descarga al iniciar sesión',
    'не класть ярлык окна':
        'no crear el acceso directo de la ventana',
    'не получилось: {}':
        'no se pudo: {}',
    'не спрашивать':
        'no preguntar',
    'положить ярлык окна':
        'crear el acceso directo de la ventana',
    'поставить {}: {}':
        'instalar {}: {}',
    'поставить в окружение программы: {}':
        'instalar en el entorno del programa: {}',
    'создать окружение Python в папке программы (.venv)':
        'crear un entorno de Python en la carpeta del programa (.venv)',
    'только показать шаги, ничего не трогая':
        'solo mostrar los pasos, sin tocar nada',
    # --- надзор за скоростью, правила, уход за архивом ---
    '  не убрался {}: {}':
        '  no se pudo quitar {}: {}',
    '  … и ещё {} (показать все: --limit 0)':
        '  … y {} más (mostrar todo: --limit 0)',
    ' КиБ/с':
        ' KiB/s',
    '23-7 или 23:00-07:30 — пусто: всегда':
        '23-7 o 23:00-07:30 — vacío: siempre',
    'yt-dlp {} — {}':
        'yt-dlp {} — {}',
    'yt-dlp поставлен не этой программой — обновите его тем же способом, каким ставили.':
        'yt-dlp no fue instalado por este programa: actualícelo del mismo modo en que lo instaló.',
    '{}: медленно идёт всё подряд — похоже, дело в линии. До конца прохода не снимаю; порог задаётся в [limits] crawl_speed':
        '{}: todo va lento; parece cosa de la conexión. No aplazo más hasta el final de la pasada; el umbral está en [limits] crawl_speed',
    '{}: пропущено по правилам канала {}':
        '{}: omitidos por las reglas del canal: {}',
    '{}: ролик {} идёт медленнее {:.0f} КБ/с уже {:.0f} мин — откладываю до следующего прохода':
        '{}: el vídeo {} lleva más lento que {:.0f} KB/s {:.0f} min: lo aplazo a la siguiente pasada',
    'Адрес плейлиста, ролика или вкладки videos канала:':
        'Dirección de una lista, un vídeo o la pestaña de vídeos de un canal:',
    'Архив YouTube — нужен человек':
        'Archivo de YouTube — le necesita',
    'В учёте есть, файла нет — такие ролики заново не скачаются: {}':
        'Registrados pero sin archivo: estos no volverán a descargarse: {}',
    'Выполнить':
        'Ejecutar',
    'ГГГГ-ММ-ДД — пусто: любые':
        'AAAA-MM-DD — vacío: cualquiera',
    'Добавить по адресу':
        'Añadir por dirección',
    'Добавить по адресу…':
        'Añadir por dirección…',
    'Куки YouTube:':
        'Cookies de YouTube:',
    'Название. Оно же станет именем папки в архиве:':
        'Nombre. Será también el nombre de la carpeta en el archivo:',
    'Не длиннее:':
        'No más largo que:',
    'Не короче, не длиннее, не старше — одной строкой вместо сотни галочек.':
        'Ni más corto, ni más largo, ni más antiguo: una línea en vez de cien casillas.',
    'Не короче:':
        'No más corto que:',
    'Не старше:':
        'No anterior a:',
    'Ничего не тронуто. Убрать повторные строки: ytarchive verify --apply':
        'No se ha tocado nada. Para quitar las líneas repetidas: ytarchive verify --apply',
    'Ничего не тронуто. Убрать: ytarchive clean --apply':
        'No se ha tocado nada. Para quitar: ytarchive clean --apply',
    'Обновить yt-dlp':
        'Actualizar yt-dlp',
    'Обновление yt-dlp':
        'Actualización de yt-dlp',
    'Один ролик в нескольких файлах: {}':
        'Un vídeo en varios archivos: {}',
    'Откладывать загрузку медленнее:':
        'Aplazar descargas más lentas que:',
    'Плейлист, отдельный ролик или канал, которого нет в поиске.':
        'Una lista, un vídeo suelto o un canal que la búsqueda no encuentra.',
    'Повторных строк в учёте: {} (безвредно)':
        'Líneas repetidas en el registro: {} (inofensivo)',
    'Потолок скорости:':
        'Límite de velocidad:',
    'Правила канала — {}':
        'Reglas del canal — {}',
    'Правила отбора: {}':
        'Reglas de selección: {}',
    'Правила…':
        'Reglas…',
    'Правило вычёркивает ролики из очереди, но ничего не удаляет с диска: снимете правило — ролики вернутся в очередь. Ролик, у которого длительность или дата неизвестны, правилу не подчиняется.':
        'Una regla saca vídeos de la cola pero no borra nada del disco: quite la regla y volverán a la cola. Un vídeo cuya duración o fecha se desconoce no queda sujeto a la regla.',
    'Сверить учёт с диском':
        'Comparar el registro con el disco',
    'Сверка учёта с диском':
        'Registro frente al disco',
    'Старые журналы и обломки загрузок. Сначала покажет, что уберёт.':
        'Registros antiguos y restos de descargas. Primero muestra lo que quitaría.',
    'Убирать нечего.':
        'No hay nada que quitar.',
    'Убрать повторные строки':
        'Quitar líneas repetidas',
    'Убрать показанное':
        'Quitar lo mostrado',
    'Убрать старое…':
        'Quitar lo antiguo…',
    'Учёт и диск сходятся.':
        'El registro y el disco coinciden.',
    'Файл есть, в учёте нет — такие ролики скачаются второй раз: {}':
        'Archivo presente pero sin registrar: estos se descargarán por segunda vez: {}',
    'Часы работы:':
        'Horario de trabajo:',
    'Чинить нечего: остальное — решение человека, а не программы.':
        'Nada que arreglar: lo demás lo decide usted, no el programa.',
    'Что можно убрать':
        'Qué se puede quitar',
    'без потолка':
        'sin límite',
    'в учёте строк: {}, роликов на диске: {}':
        'líneas en el registro: {}, vídeos en el disco: {}',
    'вне часов работы — жду до {}':
        'fuera del horario de trabajo: espero hasta las {}',
    'готово':
        'listo',
    'журналов старше {} суток: {} ({:.1f} МБ)':
        'registros de más de {} días: {} ({:.1f} MB)',
    'закончено с замечаниями':
        'terminado con observaciones',
    'идёт выкачка — учёт сейчас править нельзя ({})':
        'hay una descarga en curso: el registro no puede editarse ahora ({})',
    'из браузера {}':
        'del navegador {}',
    'из файла cookies.txt':
        'del archivo cookies.txt',
    'не добавлен: {}':
        'no añadido: {}',
    'не ограничено':
        'sin límite',
    'не проверять':
        'no comprobar',
    'обломков загрузок, которые уже не пригодятся: {} ({:.1f} МБ)':
        'restos de descargas que ya no hacen falta: {} ({:.1f} MB)',
    'обновить yt-dlp':
        'actualizar yt-dlp',
    'обновлён: {} → {}':
        'actualizado: {} → {}',
    'папка {} не прочитана: {}':
        'no se pudo leer la carpeta {}: {}',
    'работаю…':
        'trabajando…',
    'сверить учёт с файлами на диске':
        'comparar el registro con los archivos del disco',
    'сколько строк каждого перечня показать (0 — все)':
        'cuántas líneas de cada lista mostrar (0 — todas)',
    'старые журналы и обломки загрузок':
        'registros antiguos y restos de descargas',
    'убрано журналов старше {} суток: {}':
        'registros de más de {} días quitados: {}',
    'убрано повторных строк: {}; прежний учёт сохранён как {}':
        'líneas repetidas quitadas: {}; el registro anterior se guardó como {}',
    'убрано файлов: {}':
        'archivos quitados: {}',
    'убрать повторные строки учёта':
        'quitar las líneas repetidas del registro',
    'убрать, а не только показать':
        'quitar, no solo mostrar',
    'уже последняя версия: {}':
        'ya es la última versión: {}',
    'учёт не записан: {}':
        'no se escribió el registro: {}',
    'учёт не прочитан: {}':
        'no se pudo leer el registro: {}',
    # --- новый вид окна ---
    'YouTube не отдаёт ролики без входа в аккаунт. Выберите в настройках браузер, в котором вы вошли в YouTube, или положите файл cookies.txt.':
        'YouTube no entrega vídeos sin iniciar sesión. Elija en los ajustes el navegador en el que tiene la sesión de YouTube abierta, o coloque un archivo cookies.txt.',
    '{:.2f} ТБ':
        '{:.2f} TB',
    'Архив':
        'Archivo',
    'В папке архива лежат ролики в папках, которых нет в списке: {}. Так выглядит канал, переименованный в файле руками.':
        'En la carpeta del archivo hay vídeos en carpetas que no están en la lista: {}. Así se ve un canal renombrado a mano en el archivo.',
    'Дата':
        'Fecha',
    'Дата примерная: YouTube в списке канала пишет «3 года назад». Точная появится, когда ролик будет скачан.':
        'La fecha es aproximada: en la lista del canal YouTube dice «hace 3 años». La exacta aparece cuando el vídeo se descarga.',
    'Добавить канал':
        'Añadir un canal',
    'Журнал':
        'Registro',
    'Каналов пока нет. Добавьте первый — программа покажет, сколько в нём роликов и хватит ли места, ещё до того, как начнёт качать.':
        'Aún no hay canales. Añada el primero: el programa muestra cuántos vídeos tiene y si caben antes de descargar nada.',
    'Мои каналы':
        'Mis canales',
    'Осторожность':
        'Precaución',
    'Открыть настройки':
        'Abrir ajustes',
    'Показать':
        'Mostrar',
    'Сеть и расписание':
        'Red y horario',
    'Скрыть':
        'Ocultar',
    'Уход за архивом':
        'Mantenimiento del archivo',
    'Что качать':
        'Qué descargar',
    'ждёт следующего прохода':
        'esperando la siguiente pasada',
    'каналов в списке':
        'canales en la lista',
    'объём архива':
        'tamaño del archivo',
    'роликов в архиве':
        'vídeos en el archivo',
    'свободно на диске':
        'libre en el disco',
    'yt-dlp не получает ролики, только раскадровки — обновите yt-dlp кнопкой в настройках':
        'yt-dlp solo obtiene guiones gráficos, no los vídeos: actualice yt-dlp con el botón de los ajustes',
    # --- библиотека, пропавшие с YouTube, медиасервер ---
    '{}: в списке канала на YouTube больше нет роликов из архива: {}':
        '{}: vídeos del archivo que ya no están en la lista del canal en YouTube: {}',
    'Библиотека':
        'Biblioteca',
    'Все каналы':
        'Todos los canales',
    'Готовить для медиасервера (Jellyfin, Kodi, Plex)':
        'Preparar para un servidor multimedia (Jellyfin, Kodi, Plex)',
    'Комментарии ложатся в файл .info.json рядом с роликом. Это сотни лишних запросов на ролик.':
        'Los comentarios van a un archivo .info.json junto al vídeo. Son cientos de peticiones más por vídeo.',
    'Ничего не записано. Записать: ytarchive nfo --apply':
        'No se ha escrito nada. Para escribir: ytarchive nfo --apply',
    'Описания есть у всего.':
        'Todo tiene ya su archivo de descripción.',
    'Поиск по названию — по всем каналам':
        'Buscar por título — en todos los canales',
    'Показать в папке':
        'Mostrar en la carpeta',
    'Размер':
        'Tamaño',
    'Ролики из архива, которых больше нет в списке канала: удалены, скрыты или лежат на другой вкладке канала (Shorts, трансляции).':
        'Vídeos del archivo que ya no están en la lista del canal: eliminados, ocultos o en otra pestaña del canal (Shorts, directos).',
    'Рядом с роликом кладутся обложка и файл .nfo: сервер показывает канал сериалом. Для уже скачанного — команда ytarchive nfo --apply.':
        'Junto a cada vídeo se colocan una carátula y un archivo .nfo: el servidor muestra el canal como una serie. Para lo ya descargado: ytarchive nfo --apply.',
    'Смотреть':
        'Ver',
    'Сохранять комментарии (заметно дольше)':
        'Guardar comentarios (bastante más lento)',
    'Существующие описания не трогаются. На большом архиве это минуты: из каждого ролика читается его описание.':
        'Los archivos de descripción existentes no se tocan. En un archivo grande esto lleva minutos: se lee la descripción de cada vídeo.',
    'Только те, которых нет на YouTube':
        'Solo los que ya no están en YouTube',
    'дописано описаний для медиасервера: {}':
        'archivos de descripción añadidos para el servidor multimedia: {}',
    'записано описаний: {}':
        'archivos de descripción escritos: {}',
    'записать, а не только посчитать':
        'escribir, no solo contar',
    'из них нет на YouTube: {}':
        'de ellos ya no están en YouTube: {}',
    'не записалось: {}':
        'no se pudieron escribir: {}',
    'нет в списке канала':
        'no está en la lista del canal',
    'описание ролика':
        'descripción del vídeo',
    'описания для медиасервера':
        'archivos de descripción para un servidor multimedia',
    'показано {} из {}':
        'se muestran {} de {}',
    'роликов без описания: {}; каналов без описания: {}':
        'vídeos sin archivo de descripción: {}; canales sin él: {}',
    'считаю объём…':
        'calculando el tamaño…',
    '{} · объём не удалось узнать: {}':
        '{} · tamaño desconocido de: {}',
}
