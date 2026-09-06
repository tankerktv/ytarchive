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
    'язык сменён':
        'Sprache gewechselt',
    'качает':
        'lädt herunter',
    'пауза между роликами':
        'Pause zwischen Videos',
    'не запущена':
        'nicht gestartet',
    'остановлена, нужен человек':
        'angehalten, Eingriff nötig',
    'Архив YouTube — первый запуск':
        'YouTube-Archiv — erster Start',
    'Программа будет забирать новые ролики с выбранных каналов сама.':
        'Das Programm holt neue Videos der gewählten Kanäle von selbst.',
    'Ролики скачиваются целиком, и места им нужно много: час видео — от 0,6 до 1,6 ГБ, а канал целиком легко занимает сотни гигабайт. Выберите папку на диске, где есть запас.':
        'Videos werden vollständig geladen und brauchen viel Platz: eine Stunde Video sind 0,6 bis 1,6 GB, ein ganzer Kanal leicht mehrere hundert Gigabyte. Wählen Sie einen Ordner auf einer Platte mit Reserve.',
    'Папка не выбрана':
        'Kein Ordner gewählt',
    'Готово':
        'Fertig',
    'Отмена':
        'Abbrechen',
    '    готово {:.1f} МБ{}':
        '    fertig {:.1f} MB{}',
    '    отказ: {}':
        '    Fehler: {}',
    '  {:.2f}–{:.2f} ГБ':
        '  {:.2f}–{:.2f} GB',
    '  {}: ОТКАЗ — {}':
        '  {}: ABGELEHNT — {}',
    '  {}: доступ есть':
        '  {}: erreichbar',
    '  качаю {}':
        '  lade {}',
    '  непонятных строк в архиве: {}':
        '  unlesbare Zeilen im Archiv: {}',
    '  строка {} пропущена: {}':
        '  Zeile {} übersprungen: {}',
    ', {:.2f} МБ/с':
        ', {:.2f} MB/s',
    ', предпочтение AV1':
        ', AV1 bevorzugt',
    'yt-dlp вернул пустой список при успешном коде — похоже, он устарел':
        'yt-dlp lieferte eine leere Liste bei Erfolgscode — es wirkt veraltet',
    'yt-dlp сомневается в правах на вкладку канала':
        'yt-dlp zweifelt an den Rechten für den Kanalreiter',
    '{} уже есть. Перезаписать: --force':
        '{} gibt es schon. Überschreiben: --force',
    '{}: не прошло за {} попыток':
        '{}: nach {} Versuchen nicht geschafft',
    '{}: не разбирается как TOML — {}':
        '{}: kein gültiges TOML — {}',
    '{}: не удалось записать список — {}':
        '{}: Warteschlange nicht schreibbar — {}',
    '{}: непонятых строк в переписи {}':
        '{}: unlesbare Zeilen in der Liste: {}',
    '{}: остановлено — {}':
        '{}: angehalten — {}',
    '{}: проверка — {}{}':
        '{}: Prüfung — {}{}',
    '{}: пропущено по вашему выбору {}':
        '{}: nach Ihrer Wahl übersprungen: {}',
    '{}: скачано {}, упало {}':
        '{}: geladen {}, fehlgeschlagen {}',
    'Ничего не скачано и не изменено. Качать: ytarchive run':
        'Nichts geladen, nichts geändert. Zum Laden: ytarchive run',
    'Сколько займёт час материала при измеренных битрейтах:':
        'Wie viel eine Stunde Material bei den gemessenen Bitraten braucht:',
    'архив:      {}':
        'Archiv:      {}',
    'беда общая для всех каналов — остальные ({}) не проверяю, ждём следующего прохода':
        'die Störung betrifft alle Kanäle — die übrigen ({}) werden übersprungen, wir warten auf den nächsten Durchlauf',
    'в списке исключений непонятых строк {}: {}':
        'unlesbare Zeilen in der Ausschlussliste: {} — {}',
    'все каналы отвечают':
        'alle Kanäle antworten',
    'доступ есть, форматы отдаются':
        'erreichbar, Formate werden geliefert',
    'достучаться до каналов':
        'die Kanäle erreichen',
    'каналов с бедой: {}':
        'Kanäle mit Problemen: {}',
    'каналов:    {}':
        'Kanäle:      {}',
    'качать непрерывно, без планировщика задач':
        'durchgehend laden, ohne Aufgabenplanung',
    'качать — один проход и выход':
        'laden — ein Durchlauf und Ende',
    'качество:   до {}p':
        'Qualität:    bis {}p',
    'куки:       {}':
        'Cookies:     {}',
    'настройки не записались: {}':
        'Einstellungen nicht geschrieben: {}',
    'настройки не созданы — запустите ещё раз, когда решите, куда качать':
        'keine Einstellungen angelegt — starten Sie erneut, wenn Sie wissen, wohin',
    'настройки:  {}':
        'Einstellungen: {}',
    'настройки: {}':
        'Einstellungen: {}',
    'не найден движок JavaScript — нужен node':
        'keine JavaScript-Engine gefunden — node wird gebraucht',
    'не решается задача YouTube — нужен решатель EJS':
        'die YouTube-Aufgabe wird nicht gelöst — der EJS-Löser wird gebraucht',
    'не удалось прочитать список каналов':
        'die Kanalliste war nicht lesbar',
    'неопознанный отказ':
        'unbekannter Fehler',
    'нет движка JavaScript':
        'keine JavaScript-Engine',
    'нет файла настроек {}. Создать образец: ytarchive init':
        'keine Einstellungsdatei {}. Muster anlegen: ytarchive init',
    'нужен вход в аккаунт YouTube':
        'eine Anmeldung bei YouTube ist nötig',
    'нужен вход в аккаунт YouTube — куки истекли или их нет':
        'eine Anmeldung bei YouTube ist nötig — die Cookies sind abgelaufen oder fehlen',
    'окно наблюдения':
        'das Beobachtungsfenster',
    'окно требует PySide6, а его нет: {}':
        'das Fenster braucht PySide6, und es fehlt: {}',
    'остановлено по просьбе':
        'auf Wunsch angehalten',
    'остановлено по просьбе — остальные каналы ждут следующего прохода':
        'auf Wunsch angehalten — die übrigen Kanäle warten auf den nächsten Durchlauf',
    'перезаписать существующий':
        'die vorhandene überschreiben',
    'показать, но не создавать':
        'zeigen, aber nicht anlegen',
    'попросил остановиться — демон уйдёт, договорив текущий ролик':
        'angehalten — das laufende Video wird noch zu Ende geladen',
    'попросить работающий экземпляр остановиться':
        'die laufende Kopie zum Anhalten auffordern',
    'поставить:  {}':
        'installieren:  {}',
    'построить окно и выйти — для сборки':
        'das Fenster bauen und beenden — für die Sammlung',
    'проверка не дала ответа':
        'die Prüfung gab keine Antwort',
    'пустая выдача при успешном коде возврата':
        'leere Ausgabe bei Erfolgscode',
    'сделать столько проходов и выйти (по умолчанию — пока не остановят)':
        'so viele Durchläufe machen und beenden (voreingestellt: bis man anhält)',
    'сетевой сбой':
        'Netzwerkstörung',
    'следующий проход через {:.0f} мин':
        'nächster Durchlauf in {:.0f} min',
    'снято галочками роликов: {}':
        'abgewählte Videos: {}',
    'создал бы {}:\n':
        'würde anlegen {}:\n',
    'создан {} — поправьте пути и запустите: ytarchive check':
        '{} angelegt — Pfade anpassen und starten: ytarchive check',
    'создан {}: архив в {}':
        '{} angelegt: Archiv in {}',
    'создать образец настроек':
        'eine Muster-Einstellungsdatei anlegen',
    'список исключений не прочитан ({}) — качаю всё':
        'die Ausschlussliste war nicht lesbar ({}) — es wird alles geladen',
    'строка {} пропущена: {}':
        'Zeile {} übersprungen: {}',
    'уже работает: {}':
        'läuft bereits: {}',
    'уже скачано: {} роликов':
        'bereits geladen: {} Videos',
    'файл настроек (по умолчанию {})':
        'Einstellungsdatei (voreingestellt {})',
    'что будет скачано, без изменений':
        'was geladen würde, ohne etwas zu ändern',
    'не заданы — YouTube откажет':
        'nicht gesetzt — YouTube wird ablehnen',
    '{} роликов · {:.1f} ч · {:.0f}–{:.0f} ГБ':
        '{} Videos · {:.1f} h · {:.0f}–{:.0f} GB',
    'замок брошен процессом {} — забираю':
        'Sperre von Prozess {} verlassen — ich übernehme sie',
    'замок протух: {} молчит слишком долго — забираю':
        'Sperre veraltet: {} schweigt zu lange — ich übernehme sie',
    'замок свободен':
        'Sperre ist frei',
    'меряю…':
        'messe…',
    'остановлено: {}':
        'angehalten: {}',
    'скачано {}':
        'geladen {}',
    'уже работает экземпляр {} — второй не нужен':
        'Kopie {} läuft bereits — eine zweite ist nicht nötig',
    'упало {} (заберутся следующим проходом)':
        '{} fehlgeschlagen (werden beim nächsten Durchlauf geholt)',
}
