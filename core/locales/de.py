"""Deutsch.

Ключ — русская строка из кода. Полнота проверяется тестом: пропуск здесь
не падает, а тихо показывает человеку чужой язык посреди своего.

Переведено без носителя языка: если что-то звучит неловко, правьте смело.
"""

СЛОВАРЬ = {
    'Архив YouTube':
        'YouTube-Archiv',
    'Архив YouTube — {}':
        'YouTube-Archiv — {}',
    'Обзор':
        'Übersicht',
    'Каналы':
        'Kanäle',
    'Настройки':
        'Einstellungen',
    'читаю состояние…':
        'lese Status…',
    'Запустить':
        'Starten',
    'Остановить':
        'Anhalten',
    'Обновить':
        'Aktualisieren',
    'Запустить выкачку':
        'Herunterladen starten',
    'Остановить выкачку':
        'Herunterladen anhalten',
    'обход работает':
        'Durchlauf läuft',
    'обход не запущен':
        'Durchlauf nicht gestartet',
    'в архиве {} роликов':
        '{} Videos im Archiv',
    'канал {}':
        'Kanal {}',
    'последний файл {:.0f} МБ, {:.1f} МБ/с':
        'letzte Datei {:.0f} MB, {:.1f} MB/s',
    'отказов в этом сеансе {} — заберутся следующим проходом':
        '{} Fehlschläge in dieser Sitzung — sie werden beim nächsten Durchlauf geholt',
    ' · канал {} из {}':
        ' · Kanal {} von {}',
    '{}: ролик {} из {}':
        '{}: Video {} von {}',
    'осталось {}':
        '{} übrig',
    'Сколько уже лежит в архиве по каждому каналу:':
        'Wie viel je Kanal bereits im Archiv liegt:',
    'Канал':
        'Kanal',
    'Файлов':
        'Dateien',
    'Объём':
        'Größe',
    'Название канала — например, alex m':
        'Kanalname — zum Beispiel alex m',
    'Найти':
        'Suchen',
    'ищу…':
        'suche…',
    'введите название':
        'Namen eingeben',
    'Добавить выбранный канал':
        'Ausgewählten Kanal hinzufügen',
    'Убрать':
        'Entfernen',
    'Убрать канал':
        'Kanal entfernen',
    'Выбрать ролики…':
        'Videos auswählen…',
    'Список роликов канала с галочками. По умолчанию отмечены все.':
        'Die Videos des Kanals mit Häkchen. Standardmäßig ist alles angehakt.',
    '↑ Выше':
        '↑ Höher',
    '↓ Ниже':
        '↓ Tiefer',
    'Список каналов. Порядок здесь — это порядок обхода: верхний забирается первым.':
        'Die Kanalliste. Die Reihenfolge hier ist die Abarbeitungsreihenfolge: der oberste wird zuerst geholt.',
    'Убрать «{}» из списка?\n\nСкачанное останется на диске и в учёте — канал уходит из очереди, а не из архива. Вернёте обратно — заново качать не станет.':
        '„{}“ aus der Liste entfernen?\n\nBereits Heruntergeladenes bleibt auf der Festplatte und in der Erfassung — der Kanal verlässt die Warteschlange, nicht das Archiv. Fügen Sie ihn wieder hinzu, wird nichts erneut geladen.',
    '«{}» уже в списке':
        '„{}“ steht schon in der Liste',
    '{}: добавлен «{}»':
        '{}: „{}“ hinzugefügt',
    'в списке есть непонятые строки — сначала поправьте их':
        'die Liste enthält unlesbare Zeilen — bringen Sie diese zuerst in Ordnung',
    'в файле есть непонятые строки — {}':
        'die Datei enthält unlesbare Zeilen — {}',
    'строка {}: {}':
        'Zeile {}: {}',
    'список каналов сохранён':
        'Kanalliste gespeichert',
    'логотип':
        'Logo',
    'Влезет':
        'Passt',
    'Может не влезть':
        'Passt womöglich nicht',
    'НЕ ВЛЕЗЕТ':
        'PASST NICHT',
    'да':
        'ja',
    'По верхней оценке «{}» займёт больше, чем есть свободного места.\n\n{}\n\nВсё равно добавить?':
        'Nach der oberen Schätzung braucht „{}“ mehr Platz als frei ist.\n\n{}\n\nTrotzdem hinzufügen?',
    'Рабочая папка:':
        'Arbeitsordner:',
    'Обзор…':
        'Durchsuchen…',
    'Куда складывать архив':
        'Wohin das Archiv gehört',
    'Эта папка не подойдёт':
        'Dieser Ordner taugt nicht',
    'Сменить рабочую папку?':
        'Arbeitsordner wechseln?',
    '{}\n\n{}\n\nСменить?':
        '{}\n\n{}\n\nWechseln?',
    'папка сменится при сохранении':
        'der Ordner wechselt beim Speichern',
    'Рабочая папка сменена':
        'Arbeitsordner gewechselt',
    'папка сменена; окно покажет новую после перезапуска':
        'Ordner gewechselt; das Fenster zeigt den neuen nach einem Neustart',
    'Выкачка перейдёт на новую папку со следующего прохода.\n\nЭто окно показывает прежнюю папку, пока его не перезапустить.':
        'Das Herunterladen wechselt beim nächsten Durchlauf in den neuen Ordner.\n\nDieses Fenster zeigt weiter den bisherigen Ordner, bis es neu gestartet wird.',
    'Рабочая папка — это и склад роликов, и учёт скачанного. Смена папки ничего не переносит: новая папка начинается с того, что в ней уже лежит. Выкачка перейдёт на неё со следующего прохода.':
        'Der Arbeitsordner enthält sowohl die Videos als auch die Erfassung des bereits Geladenen. Ein Wechsel verschiebt nichts: der neue Ordner beginnt mit dem, was schon darin liegt. Das Herunterladen wechselt beim nächsten Durchlauf dorthin.',
    'Качество:':
        'Qualität:',
    'до {}p':
        'bis {}p',
    'Предпочитать AV1 (тот же вид, файл меньше)':
        'AV1 bevorzugen (gleiches Bild, kleinere Datei)',
    'Забирать субтитры':
        'Untertitel holen',
    'Считать зависшим после:':
        'Als hängend gelten nach:',
    'Пауза между роликами, от:':
        'Pause zwischen Videos, von:',
    'до:':
        'bis:',
    ' с':
        ' s',
    'Паузы между роликами берегут доступ: на потоке в тысячи запросов YouTube начинает отвечать «подтвердите, что вы не бот». Предел молчания должен быть заметно больше самой длинной паузы, иначе живую выкачку будут убивать как зависшую.':
        'Pausen zwischen den Videos schützen den Zugang: nach Tausenden Anfragen antwortet YouTube mit „Bestätigen Sie, dass Sie kein Bot sind“. Die Schweigegrenze muss deutlich über der längsten Pause liegen, sonst wird ein gesunder Download als hängend abgebrochen.',
    'Сохранить настройки':
        'Einstellungen speichern',
    'Вернуть как было':
        'Zurücksetzen',
    'Не сохранил':
        'Nicht gespeichert',
    'не сохранено':
        'nicht gespeichert',
    'не сохранилось: {}':
        'nicht gespeichert: {}',
    'настройки не читаются: {}':
        'Einstellungen nicht lesbar: {}',
    'настройки сохранены — вступят в силу со следующего прохода':
        'Einstellungen gespeichert — sie gelten ab dem nächsten Durchlauf',
    'Показать окно':
        'Fenster zeigen',
    'Выйти':
        'Beenden',
    'Окно свёрнуто в трей. Выкачка идёт сама и от окна не зависит.':
        'Das Fenster liegt im Infobereich. Das Herunterladen läuft von selbst und hängt nicht am Fenster.',
    'запустил':
        'gestartet',
    'уже работает':
        'läuft bereits',
    'никто не работает':
        'es läuft nichts',
    'не вышло запустить: {}':
        'Start fehlgeschlagen: {}',
    'не вышло остановить: {}':
        'Anhalten fehlgeschlagen: {}',
    'попросил остановиться — уйдёт, договорив текущий ролик':
        'angehalten — das laufende Video wird noch zu Ende geladen',
    'журнал не читается: {}':
        'das Protokoll ist nicht lesbar: {}',
    'Ролики канала «{}»':
        'Videos von „{}“',
    'Читаю список роликов канала «{}»…':
        'Lese die Videoliste von „{}“…',
    '«{}»: роликов {}':
        '„{}“: {} Videos',
    '«{}»: список получить не удалось — сеть или вход в аккаунт. Выбор не тронут.':
        '„{}“: Liste nicht erhalten — Netzwerk oder Anmeldung. Ihre Auswahl bleibt unberührt.',
    'Отмечено — будет скачано. Снятая галочка не удаляет уже скачанное: она про будущие проходы.':
        'Angehakt heißt: wird geladen. Ein entferntes Häkchen löscht nichts bereits Geladenes — es betrifft künftige Durchläufe.',
    'Поиск по названию':
        'Nach Titel suchen',
    'Отметить показанные':
        'Angezeigte anhaken',
    'Снять показанные':
        'Häkchen der Angezeigten entfernen',
    'Название':
        'Titel',
    'Длительность':
        'Dauer',
    'Состояние':
        'Zustand',
    'скачан':
        'geladen',
    'в очереди':
        'in der Warteschlange',
    'снят':
        'abgewählt',
    'выберите ролик':
        'Video auswählen',
    'миниатюра ещё не скачана':
        'Vorschaubild noch nicht geladen',
    'миниатюра не читается':
        'Vorschaubild nicht lesbar',
    'Открыть на YouTube':
        'Auf YouTube öffnen',
    'Сохранить выбор':
        'Auswahl speichern',
    'Закрыть':
        'Schließen',
    'Выбор не сохранён':
        'Auswahl nicht gespeichert',
    'выбор сохранён':
        'Auswahl gespeichert',
    'выбор сохранён; всего снято роликов по всем каналам: {}':
        'Auswahl gespeichert; über alle Kanäle abgewählte Videos: {}',
    ' — вступит в силу со следующего прохода':
        ' — gilt ab dem nächsten Durchlauf',
    'отмечено {} из {}{}':
        '{} von {} angehakt{}',
    ', показано {}':
        ', {} angezeigt',
    '; снято {}':
        '; {} abgewählt',
    '{:.0f} МБ':
        '{:.0f} MB',
    '{:.1f} МБ/с':
        '{:.1f} MB/s',
    '{:.1f} ГБ':
        '{:.1f} GB',
    '{:.2f} ГБ':
        '{:.2f} GB',
    'Язык:':
        'Sprache:',
    'Системный язык — {}':
        'Systemsprache — {}',
    'язык окна сменится после перезапуска':
        'die Sprache des Fensters wechselt nach einem Neustart',
}
