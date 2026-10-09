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
    'Новое название. Оно же станет именем папки — она переименуется вместе с каналом.':
        'Neuer Name. Er wird auch der Ordnername — der Ordner wird zusammen mit dem Kanal umbenannt.',
    'Переименовать канал':
        'Kanal umbenennen',
    'Переименовать…':
        'Umbenennen…',
    'Сменить название канала вместе с его папкой.':
        'Den Kanalnamen samt Ordner ändern.',
    'в названии есть символы, недопустимые в имени папки':
        'der Name enthält Zeichen, die in Ordnernamen nicht erlaubt sind',
    'идёт проход выкачки — дождитесь его конца или остановите выкачку':
        'ein Durchlauf läuft gerade — warten Sie ab oder halten Sie das Herunterladen an',
    'канал переименован: «{}» → «{}»':
        'Kanal umbenannt: „{}“ → „{}“',
    'канал с таким названием уже есть':
        'ein Kanal mit diesem Namen existiert bereits',
    'название не может быть пустым':
        'der Name darf nicht leer sein',
    'название то же самое':
        'der Name ist derselbe',
    'папка «{}» уже есть — сливать две папки молча нельзя':
        'der Ordner „{}“ existiert bereits — zwei Ordner werden nie stillschweigend zusammengelegt',
    'папку переименовать не вышло: {}':
        'Ordner konnte nicht umbenannt werden: {}',
    'такого канала в списке нет':
        'diesen Kanal gibt es in der Liste nicht',
    # --- установщик ---
    '    на Debian и Ubuntu сначала нужно: sudo apt-get install python3-venv':
        '    unter Debian und Ubuntu zuerst: sudo apt-get install python3-venv',
    'Python {} — подходит.':
        'Python {} — passt.',
    '[Д/н]':
        '[J/n]',
    '[д/Н]':
        '[j/N]',
    '{} — не найден, и я не знаю, чем его поставить на этой системе':
        '{} — nicht gefunden, und ich weiß nicht, womit man es auf diesem System installiert',
    '{} — поставьте сами: {}':
        '{} — bitte selbst installieren: {}',
    'Архив YouTube — выкачка':
        'YouTube-Archiv — Download',
    'Вхолостую: ничего не тронуто.':
        'Probelauf: nichts wurde verändert.',
    'Выкачка новых роликов в фоне':
        'Lädt neue Videos im Hintergrund',
    'Выполнить?':
        'Ausführen?',
    'Готово.':
        'Fertig.',
    'Запускать выкачку при входе в систему?':
        'Download bei der Anmeldung starten?',
    'Исправьте причину и запустите установку ещё раз — сделанное не пропадёт.':
        'Beheben Sie die Ursache und starten Sie die Installation erneut — das Erledigte bleibt erhalten.',
    'Окно архива роликов':
        'Fenster des Videoarchivs',
    'Осталось сделать руками:':
        'Von Hand zu erledigen:',
    'Остановился на шаге {}: дальше без него нельзя.':
        'Bei Schritt {} angehalten: ohne ihn geht es nicht weiter.',
    'Открыть окно сейчас?':
        'Fenster jetzt öffnen?',
    'Открыть окно:  {} {} gui':
        'Fenster öffnen:  {} {} gui',
    'Отменено, ничего не тронуто.':
        'Abgebrochen, nichts wurde verändert.',
    'Положить ярлык, открывающий окно?':
        'Verknüpfung anlegen, die das Fenster öffnet?',
    'После установки node и ffmpeg откройте новый терминал: старый их не увидит.':
        'Öffnen Sie nach der Installation von node und ffmpeg ein neues Terminal: das alte sieht sie nicht.',
    'Создать настройки: {} {} init':
        'Einstellungen anlegen: {} {} init',
    'Спросить некого: запустите в терминале или добавьте --yes.':
        'Niemand zum Fragen: im Terminal starten oder --yes angeben.',
    'Установка ytarchive в {}':
        'ytarchive wird installiert in {}',
    'Установка ytarchive.':
        'ytarchive installieren.',
    'Что будет сделано:':
        'Was getan wird:',
    'Что дальше — куки YouTube и первый канал — написано в INSTALL.ru.md.':
        'Wie es weitergeht — YouTube-Cookies und der erste Kanal — steht in INSTALL.md.',
    'без окна: только командная строка и выкачка':
        'ohne Fenster: nur Kommandozeile und Download',
    'запускать выкачку при входе в систему':
        'Download bei der Anmeldung starten',
    'не запускать выкачку при входе в систему':
        'Download bei der Anmeldung nicht starten',
    'не класть ярлык окна':
        'keine Verknüpfung für das Fenster anlegen',
    'не получилось: {}':
        'fehlgeschlagen: {}',
    'не спрашивать':
        'nicht nachfragen',
    'положить ярлык окна':
        'Verknüpfung für das Fenster anlegen',
    'поставить {}: {}':
        '{} installieren: {}',
    'поставить в окружение программы: {}':
        'in die Programmumgebung installieren: {}',
    'создать окружение Python в папке программы (.venv)':
        'Python-Umgebung im Programmordner anlegen (.venv)',
    'только показать шаги, ничего не трогая':
        'nur die Schritte zeigen, nichts verändern',
    # --- надзор за скоростью, правила, уход за архивом ---
    '  не убрался {}: {}':
        '  nicht entfernt {}: {}',
    '  … и ещё {} (показать все: --limit 0)':
        '  … und {} weitere (alle zeigen: --limit 0)',
    ' КиБ/с':
        ' KiB/s',
    '23-7 или 23:00-07:30 — пусто: всегда':
        '23-7 oder 23:00-07:30 — leer: immer',
    'yt-dlp {} — {}':
        'yt-dlp {} — {}',
    'yt-dlp поставлен не этой программой — обновите его тем же способом, каким ставили.':
        'yt-dlp wurde nicht von diesem Programm installiert — aktualisieren Sie es auf demselben Weg, auf dem Sie es installiert haben.',
    '{}: медленно идёт всё подряд — похоже, дело в линии. До конца прохода не снимаю; порог задаётся в [limits] crawl_speed':
        '{}: alles läuft langsam — offenbar liegt es an der Leitung. Bis zum Ende des Durchlaufs wird nichts mehr zurückgestellt; die Schwelle steht in [limits] crawl_speed',
    '{}: пропущено по правилам канала {}':
        '{}: nach Kanalregeln übersprungen: {}',
    '{}: ролик {} идёт медленнее {:.0f} КБ/с уже {:.0f} мин — откладываю до следующего прохода':
        '{}: Video {} läuft langsamer als {:.0f} KB/s, und das seit {:.0f} Min. — auf den nächsten Durchlauf verschoben',
    'Адрес плейлиста, ролика или вкладки videos канала:':
        'Adresse einer Playlist, eines Videos oder des Videos-Tabs eines Kanals:',
    'Архив YouTube — нужен человек':
        'YouTube-Archiv — Sie werden gebraucht',
    'В учёте есть, файла нет — такие ролики заново не скачаются: {}':
        'Verzeichnet, aber Datei fehlt — diese werden nie wieder geladen: {}',
    'Выполнить':
        'Ausführen',
    'ГГГГ-ММ-ДД — пусто: любые':
        'JJJJ-MM-TT — leer: beliebig',
    'Добавить по адресу':
        'Per Adresse hinzufügen',
    'Добавить по адресу…':
        'Per Adresse hinzufügen…',
    'Куки YouTube:':
        'YouTube-Cookies:',
    'Название. Оно же станет именем папки в архиве:':
        'Name. Er wird auch der Ordnername im Archiv:',
    'Не длиннее:':
        'Nicht länger als:',
    'Не короче, не длиннее, не старше — одной строкой вместо сотни галочек.':
        'Nicht kürzer, nicht länger, nicht älter — eine Zeile statt hundert Häkchen.',
    'Не короче:':
        'Nicht kürzer als:',
    'Не старше:':
        'Nicht älter als:',
    'Ничего не тронуто. Убрать повторные строки: ytarchive verify --apply':
        'Nichts wurde verändert. Doppelte Zeilen entfernen: ytarchive verify --apply',
    'Ничего не тронуто. Убрать: ytarchive clean --apply':
        'Nichts wurde verändert. Entfernen: ytarchive clean --apply',
    'Обновить yt-dlp':
        'yt-dlp aktualisieren',
    'Обновление yt-dlp':
        'yt-dlp wird aktualisiert',
    'Один ролик в нескольких файлах: {}':
        'Ein Video in mehreren Dateien: {}',
    'Откладывать загрузку медленнее:':
        'Downloads zurückstellen, langsamer als:',
    'Плейлист, отдельный ролик или канал, которого нет в поиске.':
        'Eine Playlist, ein einzelnes Video oder ein Kanal, den die Suche nicht findet.',
    'Повторных строк в учёте: {} (безвредно)':
        'Doppelte Zeilen im Verzeichnis: {} (harmlos)',
    'Потолок скорости:':
        'Geschwindigkeitsgrenze:',
    'Правила канала — {}':
        'Kanalregeln — {}',
    'Правила отбора: {}':
        'Auswahlregeln: {}',
    'Правила…':
        'Regeln…',
    'Правило вычёркивает ролики из очереди, но ничего не удаляет с диска: снимете правило — ролики вернутся в очередь. Ролик, у которого длительность или дата неизвестны, правилу не подчиняется.':
        'Eine Regel nimmt Videos aus der Warteschlange, löscht aber nichts von der Platte: Ohne die Regel kehren sie zurück. Ein Video mit unbekannter Dauer oder unbekanntem Datum fällt nicht unter die Regel.',
    'Сверить учёт с диском':
        'Verzeichnis mit der Platte abgleichen',
    'Сверка учёта с диском':
        'Abgleich von Verzeichnis und Platte',
    'Старые журналы и обломки загрузок. Сначала покажет, что уберёт.':
        'Alte Protokolle und Download-Reste. Zeigt zuerst, was entfernt würde.',
    'Убирать нечего.':
        'Nichts zu entfernen.',
    'Убрать повторные строки':
        'Doppelte Zeilen entfernen',
    'Убрать показанное':
        'Angezeigtes entfernen',
    'Убрать старое…':
        'Altes entfernen…',
    'Учёт и диск сходятся.':
        'Verzeichnis und Platte stimmen überein.',
    'Файл есть, в учёте нет — такие ролики скачаются второй раз: {}':
        'Datei vorhanden, aber nicht verzeichnet — diese werden ein zweites Mal geladen: {}',
    'Часы работы:':
        'Betriebszeiten:',
    'Чинить нечего: остальное — решение человека, а не программы.':
        'Nichts zu reparieren: Der Rest ist Ihre Entscheidung, nicht die des Programms.',
    'Что можно убрать':
        'Was entfernt werden kann',
    'без потолка':
        'ohne Grenze',
    'в учёте строк: {}, роликов на диске: {}':
        'Zeilen im Verzeichnis: {}, Videos auf der Platte: {}',
    'вне часов работы — жду до {}':
        'außerhalb der Betriebszeiten — warte bis {}',
    'готово':
        'fertig',
    'журналов старше {} суток: {} ({:.1f} МБ)':
        'Protokolle älter als {} Tage: {} ({:.1f} MB)',
    'закончено с замечаниями':
        'mit Anmerkungen beendet',
    'идёт выкачка — учёт сейчас править нельзя ({})':
        'ein Download läuft — das Verzeichnis kann jetzt nicht geändert werden ({})',
    'из браузера {}':
        'aus dem Browser {}',
    'из файла cookies.txt':
        'aus der Datei cookies.txt',
    'не добавлен: {}':
        'nicht hinzugefügt: {}',
    'не ограничено':
        'unbegrenzt',
    'не проверять':
        'nicht prüfen',
    'обломков загрузок, которые уже не пригодятся: {} ({:.1f} МБ)':
        'Download-Reste, die nicht mehr gebraucht werden: {} ({:.1f} MB)',
    'обновить yt-dlp':
        'yt-dlp aktualisieren',
    'обновлён: {} → {}':
        'aktualisiert: {} → {}',
    'папка {} не прочитана: {}':
        'Ordner {} nicht lesbar: {}',
    'работаю…':
        'arbeite…',
    'сверить учёт с файлами на диске':
        'Verzeichnis mit den Dateien auf der Platte abgleichen',
    'сколько строк каждого перечня показать (0 — все)':
        'wie viele Zeilen jeder Liste gezeigt werden (0 — alle)',
    'старые журналы и обломки загрузок':
        'alte Protokolle und Download-Reste',
    'убрано журналов старше {} суток: {}':
        'Protokolle älter als {} Tage entfernt: {}',
    'убрано повторных строк: {}; прежний учёт сохранён как {}':
        'doppelte Zeilen entfernt: {}; das bisherige Verzeichnis liegt als {} vor',
    'убрано файлов: {}':
        'Dateien entfernt: {}',
    'убрать повторные строки учёта':
        'doppelte Zeilen aus dem Verzeichnis entfernen',
    'убрать, а не только показать':
        'entfernen, nicht nur zeigen',
    'уже последняя версия: {}':
        'bereits die neueste Version: {}',
    'учёт не записан: {}':
        'Verzeichnis nicht geschrieben: {}',
    'учёт не прочитан: {}':
        'Verzeichnis nicht lesbar: {}',
    # --- новый вид окна ---
    'YouTube не отдаёт ролики без входа в аккаунт. Выберите в настройках браузер, в котором вы вошли в YouTube, или положите файл cookies.txt.':
        'YouTube liefert Videos nur an angemeldete Nutzer. Wählen Sie in den Einstellungen den Browser, in dem Sie bei YouTube angemeldet sind, oder legen Sie eine Datei cookies.txt ab.',
    '{:.2f} ТБ':
        '{:.2f} TB',
    'Архив':
        'Archiv',
    'В папке архива лежат ролики в папках, которых нет в списке: {}. Так выглядит канал, переименованный в файле руками.':
        'Im Archivordner liegen Videos in Ordnern, die nicht in der Liste stehen: {}. So sieht ein Kanal aus, der von Hand in der Datei umbenannt wurde.',
    'Дата':
        'Datum',
    'Дата примерная: YouTube в списке канала пишет «3 года назад». Точная появится, когда ролик будет скачан.':
        'Das Datum ist ungefähr: In der Kanalliste schreibt YouTube „vor 3 Jahren“. Das genaue erscheint, sobald das Video geladen ist.',
    'Добавить канал':
        'Kanal hinzufügen',
    'Журнал':
        'Protokoll',
    'Каналов пока нет. Добавьте первый — программа покажет, сколько в нём роликов и хватит ли места, ещё до того, как начнёт качать.':
        'Noch keine Kanäle. Fügen Sie den ersten hinzu — das Programm zeigt, wie viele Videos er hat und ob der Platz reicht, bevor es etwas lädt.',
    'Мои каналы':
        'Meine Kanäle',
    'Осторожность':
        'Vorsicht',
    'Открыть настройки':
        'Einstellungen öffnen',
    'Показать':
        'Zeigen',
    'Сеть и расписание':
        'Netz und Zeitplan',
    'Скрыть':
        'Ausblenden',
    'Уход за архивом':
        'Pflege des Archivs',
    'Что качать':
        'Was geladen wird',
    'ждёт следующего прохода':
        'wartet auf den nächsten Durchlauf',
    'каналов в списке':
        'Kanäle in der Liste',
    'объём архива':
        'Größe des Archivs',
    'роликов в архиве':
        'Videos im Archiv',
    'свободно на диске':
        'frei auf der Platte',
    'yt-dlp не получает ролики, только раскадровки — обновите yt-dlp кнопкой в настройках':
        'yt-dlp bekommt nur Vorschaubilder, keine Videos — aktualisieren Sie yt-dlp über die Schaltfläche in den Einstellungen',
    # --- библиотека, пропавшие с YouTube, медиасервер ---
    '{}: в списке канала на YouTube больше нет роликов из архива: {}':
        '{}: Videos aus dem Archiv, die nicht mehr in der Kanalliste auf YouTube stehen: {}',
    'Библиотека':
        'Bibliothek',
    'Все каналы':
        'Alle Kanäle',
    'Готовить для медиасервера (Jellyfin, Kodi, Plex)':
        'Für einen Medienserver vorbereiten (Jellyfin, Kodi, Plex)',
    'Комментарии ложатся в файл .info.json рядом с роликом. Это сотни лишних запросов на ролик.':
        'Kommentare landen in einer .info.json-Datei neben dem Video. Das sind Hunderte zusätzlicher Anfragen pro Video.',
    'Ничего не записано. Записать: ytarchive nfo --apply':
        'Nichts wurde geschrieben. Schreiben: ytarchive nfo --apply',
    'Описания есть у всего.':
        'Alles hat bereits eine Beschreibungsdatei.',
    'Поиск по названию — по всем каналам':
        'Suche nach Titel — über alle Kanäle',
    'Показать в папке':
        'Im Ordner zeigen',
    'Размер':
        'Größe',
    'Ролики из архива, которых больше нет в списке канала: удалены, скрыты или лежат на другой вкладке канала (Shorts, трансляции).':
        'Videos aus dem Archiv, die nicht mehr in der Kanalliste stehen: gelöscht, verborgen oder auf einem anderen Tab des Kanals (Shorts, Livestreams).',
    'Рядом с роликом кладутся обложка и файл .nfo: сервер показывает канал сериалом. Для уже скачанного — команда ytarchive nfo --apply.':
        'Neben jedes Video kommen ein Titelbild und eine .nfo-Datei: Der Server zeigt den Kanal dann als Serie. Für bereits Geladenes: ytarchive nfo --apply.',
    'Смотреть':
        'Ansehen',
    'Сохранять комментарии (заметно дольше)':
        'Kommentare speichern (deutlich langsamer)',
    'Существующие описания не трогаются. На большом архиве это минуты: из каждого ролика читается его описание.':
        'Vorhandene Beschreibungsdateien bleiben unberührt. Bei einem großen Archiv dauert das Minuten: Aus jedem Video wird die Beschreibung gelesen.',
    'Только те, которых нет на YouTube':
        'Nur die, die nicht mehr auf YouTube sind',
    'дописано описаний для медиасервера: {}':
        'Beschreibungsdateien für den Medienserver ergänzt: {}',
    'записано описаний: {}':
        'Beschreibungsdateien geschrieben: {}',
    'записать, а не только посчитать':
        'schreiben, nicht nur zählen',
    'из них нет на YouTube: {}':
        'davon nicht mehr auf YouTube: {}',
    'не записалось: {}':
        'nicht geschrieben: {}',
    'нет в списке канала':
        'nicht in der Kanalliste',
    'описание ролика':
        'Videobeschreibung',
    'описания для медиасервера':
        'Beschreibungsdateien für einen Medienserver',
    'показано {} из {}':
        '{} von {} angezeigt',
    'роликов без описания: {}; каналов без описания: {}':
        'Videos ohne Beschreibungsdatei: {}; Kanäle ohne: {}',
    'считаю объём…':
        'Umfang wird ermittelt…',
    '{} · объём не удалось узнать: {}':
        '{} · Umfang unbekannt für: {}',
    'пустой запрос':
        'leere Anfrage',
    'поиск не удался: {}':
        'Suche fehlgeschlagen: {}',
    'ничего не нашлось':
        'nichts gefunden',
    'нашлось каналов: {}':
        'Kanäle gefunden: {}',
    'перепись не удалась: {}':
        'Kanal konnte nicht aufgelistet werden: {}',
    'измерено':
        'ermittelt',
    'без объяснения':
        'ohne Erklärung',
}
