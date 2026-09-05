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
    'Обновить':
        'Actualizar',
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
    'Сколько уже лежит в архиве по каждому каналу:':
        'Cuánto hay ya archivado en cada canal:',
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
    'логотип':
        'logotipo',
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
    '{:.2f} ГБ':
        '{:.2f} GB',
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
}
