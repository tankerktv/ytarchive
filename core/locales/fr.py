"""Français.

Ключ — русская строка из кода. Полнота проверяется тестом: пропуск здесь
не падает, а тихо показывает человеку чужой язык посреди своего.

Переведено без носителя языка: если что-то звучит неловко, правьте смело.
"""

СЛОВАРЬ = {
    'Архив YouTube':
        'Archive YouTube',
    'Архив YouTube — {}':
        'Archive YouTube — {}',
    'Обзор':
        'Aperçu',
    'Каналы':
        'Chaînes',
    'Настройки':
        'Réglages',
    'читаю состояние…':
        'lecture de l’état…',
    'Запустить':
        'Démarrer',
    'Остановить':
        'Arrêter',
    'Обновить':
        'Rafraîchir',
    'Запустить выкачку':
        'Démarrer le téléchargement',
    'Остановить выкачку':
        'Arrêter le téléchargement',
    'обход работает':
        'le parcours tourne',
    'обход не запущен':
        'le parcours est arrêté',
    'в архиве {} роликов':
        '{} vidéos dans l’archive',
    'канал {}':
        'chaîne {}',
    'последний файл {:.0f} МБ, {:.1f} МБ/с':
        'dernier fichier {:.0f} Mo, {:.1f} Mo/s',
    'отказов в этом сеансе {} — заберутся следующим проходом':
        '{} échecs cette session — ils seront repris au passage suivant',
    ' · канал {} из {}':
        ' · chaîne {} sur {}',
    '{}: ролик {} из {}':
        '{} : vidéo {} sur {}',
    'осталось {}':
        '{} restantes',
    'Сколько уже лежит в архиве по каждому каналу:':
        'Ce qui est déjà archivé, par chaîne :',
    'Канал':
        'Chaîne',
    'Файлов':
        'Fichiers',
    'Объём':
        'Taille',
    'Название канала — например, alex m':
        'Nom de la chaîne — par exemple alex m',
    'Найти':
        'Chercher',
    'ищу…':
        'recherche…',
    'введите название':
        'saisissez un nom',
    'Добавить выбранный канал':
        'Ajouter la chaîne choisie',
    'Убрать':
        'Retirer',
    'Убрать канал':
        'Retirer la chaîne',
    'Выбрать ролики…':
        'Choisir les vidéos…',
    'Список роликов канала с галочками. По умолчанию отмечены все.':
        'Les vidéos de la chaîne avec des cases. Tout est coché par défaut.',
    '↑ Выше':
        '↑ Monter',
    '↓ Ниже':
        '↓ Descendre',
    'Список каналов. Порядок здесь — это порядок обхода: верхний забирается первым.':
        'La liste des chaînes. L’ordre est celui du parcours : la première est téléchargée d’abord.',
    'Убрать «{}» из списка?\n\nСкачанное останется на диске и в учёте — канал уходит из очереди, а не из архива. Вернёте обратно — заново качать не станет.':
        'Retirer « {} » de la liste ?\n\nCe qui est téléchargé reste sur le disque et dans le relevé : la chaîne quitte la file, pas l’archive. Si vous la remettez, rien ne sera retéléchargé.',
    '«{}» уже в списке':
        '« {} » est déjà dans la liste',
    '{}: добавлен «{}»':
        '{} : « {} » ajoutée',
    'в списке есть непонятые строки — сначала поправьте их':
        'la liste contient des lignes illisibles — corrigez-les d’abord',
    'в файле есть непонятые строки — {}':
        'le fichier contient des lignes illisibles — {}',
    'строка {}: {}':
        'ligne {} : {}',
    'список каналов сохранён':
        'liste des chaînes enregistrée',
    'логотип':
        'logo',
    'Влезет':
        'Tient',
    'Может не влезть':
        'Pourrait ne pas tenir',
    'НЕ ВЛЕЗЕТ':
        'NE TIENDRA PAS',
    'да':
        'oui',
    'По верхней оценке «{}» займёт больше, чем есть свободного места.\n\n{}\n\nВсё равно добавить?':
        'D’après l’estimation haute, « {} » demande plus de place qu’il n’y en a de libre.\n\n{}\n\nL’ajouter quand même ?',
    'Рабочая папка:':
        'Dossier de travail :',
    'Обзор…':
        'Parcourir…',
    'Куда складывать архив':
        'Où ranger l’archive',
    'Эта папка не подойдёт':
        'Ce dossier ne convient pas',
    'Сменить рабочую папку?':
        'Changer de dossier de travail ?',
    '{}\n\n{}\n\nСменить?':
        '{}\n\n{}\n\nChanger ?',
    'папка сменится при сохранении':
        'le dossier changera à l’enregistrement',
    'Рабочая папка сменена':
        'Dossier de travail changé',
    'папка сменена; окно покажет новую после перезапуска':
        'dossier changé ; la fenêtre montrera le nouveau après un redémarrage',
    'Выкачка перейдёт на новую папку со следующего прохода.\n\nЭто окно показывает прежнюю папку, пока его не перезапустить.':
        'Le téléchargement passera au nouveau dossier au passage suivant.\n\nCette fenêtre continue d’afficher l’ancien tant qu’elle n’est pas relancée.',
    'Рабочая папка — это и склад роликов, и учёт скачанного. Смена папки ничего не переносит: новая папка начинается с того, что в ней уже лежит. Выкачка перейдёт на неё со следующего прохода.':
        'Le dossier de travail contient à la fois les vidéos et le relevé de ce qui a été téléchargé. En changer ne déplace rien : le nouveau dossier part de ce qu’il contient déjà. Le téléchargement y passe au passage suivant.',
    'Качество:':
        'Qualité :',
    'до {}p':
        'jusqu’à {}p',
    'Предпочитать AV1 (тот же вид, файл меньше)':
        'Préférer AV1 (même image, fichier plus petit)',
    'Забирать субтитры':
        'Récupérer les sous-titres',
    'Считать зависшим после:':
        'Considérer bloqué après :',
    'Пауза между роликами, от:':
        'Pause entre vidéos, de :',
    'до:':
        'à :',
    ' с':
        ' s',
    'Паузы между роликами берегут доступ: на потоке в тысячи запросов YouTube начинает отвечать «подтвердите, что вы не бот». Предел молчания должен быть заметно больше самой длинной паузы, иначе живую выкачку будут убивать как зависшую.':
        'Les pauses entre vidéos protègent l’accès : après des milliers de requêtes, YouTube se met à répondre « confirmez que vous n’êtes pas un robot ». La limite de silence doit dépasser nettement la plus longue pause, sinon un téléchargement sain sera tué comme s’il était bloqué.',
    'Сохранить настройки':
        'Enregistrer les réglages',
    'Вернуть как было':
        'Rétablir',
    'Не сохранил':
        'Non enregistré',
    'не сохранено':
        'non enregistré',
    'не сохранилось: {}':
        'non enregistré : {}',
    'настройки не читаются: {}':
        'réglages illisibles : {}',
    'настройки сохранены — вступят в силу со следующего прохода':
        'réglages enregistrés — ils prennent effet au passage suivant',
    'Показать окно':
        'Afficher la fenêtre',
    'Выйти':
        'Quitter',
    'Окно свёрнуто в трей. Выкачка идёт сама и от окна не зависит.':
        'La fenêtre est dans la zone de notification. Le téléchargement continue seul et ne dépend pas d’elle.',
    'запустил':
        'démarré',
    'уже работает':
        'tourne déjà',
    'никто не работает':
        'rien ne tourne',
    'не вышло запустить: {}':
        'démarrage impossible : {}',
    'не вышло остановить: {}':
        'arrêt impossible : {}',
    'попросил остановиться — уйдёт, договорив текущий ролик':
        'arrêt demandé — la vidéo en cours sera terminée',
    'журнал не читается: {}':
        'journal illisible : {}',
    'Ролики канала «{}»':
        'Vidéos de « {} »',
    'Читаю список роликов канала «{}»…':
        'Lecture de la liste des vidéos de « {} »…',
    '«{}»: роликов {}':
        '« {} » : {} vidéos',
    '«{}»: список получить не удалось — сеть или вход в аккаунт. Выбор не тронут.':
        '« {} » : liste indisponible — réseau ou connexion au compte. Votre choix est intact.',
    'Отмечено — будет скачано. Снятая галочка не удаляет уже скачанное: она про будущие проходы.':
        'Coché veut dire : sera téléchargée. Décocher n’efface rien de déjà téléchargé : cela concerne les passages à venir.',
    'Поиск по названию':
        'Chercher par titre',
    'Отметить показанные':
        'Cocher les affichées',
    'Снять показанные':
        'Décocher les affichées',
    'Название':
        'Titre',
    'Длительность':
        'Durée',
    'Состояние':
        'État',
    'скачан':
        'téléchargée',
    'в очереди':
        'en file',
    'снят':
        'décochée',
    'выберите ролик':
        'choisissez une vidéo',
    'миниатюра ещё не скачана':
        'vignette pas encore téléchargée',
    'миниатюра не читается':
        'vignette illisible',
    'Открыть на YouTube':
        'Ouvrir sur YouTube',
    'Сохранить выбор':
        'Enregistrer le choix',
    'Закрыть':
        'Fermer',
    'Выбор не сохранён':
        'Choix non enregistré',
    'выбор сохранён':
        'choix enregistré',
    'выбор сохранён; всего снято роликов по всем каналам: {}':
        'choix enregistré ; vidéos décochées sur toutes les chaînes : {}',
    ' — вступит в силу со следующего прохода':
        ' — prend effet au passage suivant',
    'отмечено {} из {}{}':
        '{} sur {} cochées{}',
    ', показано {}':
        ', {} affichées',
    '; снято {}':
        ' ; {} décochées',
    '{:.0f} МБ':
        '{:.0f} Mo',
    '{:.1f} МБ/с':
        '{:.1f} Mo/s',
    '{:.1f} ГБ':
        '{:.1f} Go',
    '{:.2f} ГБ':
        '{:.2f} Go',
    'Язык:':
        'Langue :',
    'Системный язык — {}':
        'Langue du système — {}',
    'язык сменён':
        'langue changée',
    'качает':
        'téléchargement',
    'пауза между роликами':
        'pause entre vidéos',
    'не запущена':
        'arrêtée',
    'остановлена, нужен человек':
        'arrêtée, votre intervention est requise',
    'Архив YouTube — первый запуск':
        'Archive YouTube — premier démarrage',
    'Программа будет забирать новые ролики с выбранных каналов сама.':
        'Le programme récupérera tout seul les nouvelles vidéos des chaînes choisies.',
    'Ролики скачиваются целиком, и места им нужно много: час видео — от 0,6 до 1,6 ГБ, а канал целиком легко занимает сотни гигабайт. Выберите папку на диске, где есть запас.':
        'Les vidéos sont téléchargées en entier et prennent beaucoup de place : une heure de vidéo fait de 0,6 à 1,6 Go, et une chaîne entière atteint vite des centaines de Go. Choisissez un dossier sur un disque au large.',
    'Папка не выбрана':
        'Aucun dossier choisi',
    'Готово':
        'Terminé',
    'Отмена':
        'Annuler',
    '    готово {:.1f} МБ{}':
        '    terminé {:.1f} Mo{}',
    '    отказ: {}':
        '    échec : {}',
    '  {:.2f}–{:.2f} ГБ':
        '  {:.2f}–{:.2f} Go',
    '  {}: ОТКАЗ — {}':
        '  {} : REFUSÉ — {}',
    '  {}: доступ есть':
        '  {} : joignable',
    '  качаю {}':
        '  téléchargement de {}',
    '  непонятных строк в архиве: {}':
        '  lignes illisibles dans l’archive : {}',
    '  строка {} пропущена: {}':
        '  ligne {} ignorée : {}',
    ', {:.2f} МБ/с':
        ', {:.2f} Mo/s',
    ', предпочтение AV1':
        ', AV1 préféré',
    'yt-dlp вернул пустой список при успешном коде — похоже, он устарел':
        'yt-dlp a renvoyé une liste vide avec un code de succès — il semble périmé',
    'yt-dlp сомневается в правах на вкладку канала':
        'yt-dlp doute des droits sur l’onglet de la chaîne',
    '{} уже есть. Перезаписать: --force':
        '{} existe déjà. Écraser : --force',
    '{}: не прошло за {} попыток':
        '{} : échec après {} tentatives',
    '{}: не разбирается как TOML — {}':
        '{} : TOML invalide — {}',
    '{}: не удалось записать список — {}':
        '{} : file d’attente non écrite — {}',
    '{}: непонятых строк в переписи {}':
        '{} : lignes illisibles dans la liste : {}',
    '{}: остановлено — {}':
        '{} : arrêté — {}',
    '{}: проверка — {}{}':
        '{} : vérification — {}{}',
    '{}: пропущено по вашему выбору {}':
        '{} : ignorées selon votre choix : {}',
    '{}: скачано {}, упало {}':
        '{} : téléchargées {}, échouées {}',
    'Ничего не скачано и не изменено. Качать: ytarchive run':
        'Rien de téléchargé, rien de modifié. Pour télécharger : ytarchive run',
    'Сколько займёт час материала при измеренных битрейтах:':
        'Ce que prend une heure de vidéo aux débits mesurés :',
    'архив:      {}':
        'archive :    {}',
    'беда общая для всех каналов — остальные ({}) не проверяю, ждём следующего прохода':
        'le problème touche toutes les chaînes — les autres ({}) sont ignorées, on attend le passage suivant',
    'в списке исключений непонятых строк {}: {}':
        'lignes illisibles dans la liste d’exclusion : {} — {}',
    'все каналы отвечают':
        'toutes les chaînes répondent',
    'доступ есть, форматы отдаются':
        'joignable, les formats sont fournis',
    'достучаться до каналов':
        'joindre les chaînes',
    'каналов с бедой: {}':
        'chaînes en difficulté : {}',
    'каналов:    {}':
        'chaînes :    {}',
    'качать непрерывно, без планировщика задач':
        'télécharger en continu, sans le planificateur de tâches',
    'качать — один проход и выход':
        'télécharger — un passage puis sortir',
    'качество:   до {}p':
        'qualité :    jusqu’à {}p',
    'куки:       {}':
        'cookies :    {}',
    'настройки не записались: {}':
        'réglages non écrits : {}',
    'настройки не созданы — запустите ещё раз, когда решите, куда качать':
        'aucun réglage créé — relancez quand vous saurez où télécharger',
    'настройки:  {}':
        'réglages :   {}',
    'настройки: {}':
        'réglages : {}',
    'не найден движок JavaScript — нужен node':
        'aucun moteur JavaScript trouvé — node est nécessaire',
    'не решается задача YouTube — нужен решатель EJS':
        'l’épreuve YouTube n’est pas résolue — le solveur EJS est nécessaire',
    'не удалось прочитать список каналов':
        'la liste des chaînes n’a pas pu être lue',
    'неопознанный отказ':
        'échec non identifié',
    'нет движка JavaScript':
        'pas de moteur JavaScript',
    'нет файла настроек {}. Создать образец: ytarchive init':
        'pas de fichier de réglages {}. Créer un modèle : ytarchive init',
    'нужен вход в аккаунт YouTube':
        'une connexion au compte YouTube est requise',
    'нужен вход в аккаунт YouTube — куки истекли или их нет':
        'une connexion YouTube est requise — les cookies ont expiré ou manquent',
    'окно наблюдения':
        'la fenêtre de suivi',
    'окно требует PySide6, а его нет: {}':
        'la fenêtre demande PySide6, et il manque : {}',
    'остановлено по просьбе':
        'arrêté à la demande',
    'остановлено по просьбе — остальные каналы ждут следующего прохода':
        'arrêté à la demande — les autres chaînes attendent le passage suivant',
    'перезаписать существующий':
        'écraser l’existant',
    'показать, но не создавать':
        'montrer, sans rien créer',
    'попросил остановиться — демон уйдёт, договорив текущий ролик':
        'arrêt demandé — la vidéo en cours sera terminée',
    'попросить работающий экземпляр остановиться':
        'demander l’arrêt à la copie en cours',
    'поставить:  {}':
        'installer :  {}',
    'построить окно и выйти — для сборки':
        'construire la fenêtre et sortir — pour l’intégration',
    'проверка не дала ответа':
        'la vérification n’a rien répondu',
    'пустая выдача при успешном коде возврата':
        'sortie vide avec un code de succès',
    'сделать столько проходов и выйти (по умолчанию — пока не остановят)':
        'faire ce nombre de passages puis sortir (par défaut : jusqu’à l’arrêt demandé)',
    'сетевой сбой':
        'panne réseau',
    'следующий проход через {:.0f} мин':
        'prochain passage dans {:.0f} min',
    'снято галочками роликов: {}':
        'vidéos décochées : {}',
    'создал бы {}:\n':
        'créerait {} :\n',
    'создан {} — поправьте пути и запустите: ytarchive check':
        '{} créé — corrigez les chemins et lancez : ytarchive check',
    'создан {}: архив в {}':
        '{} créé : archive dans {}',
    'создать образец настроек':
        'créer un fichier de réglages modèle',
    'список исключений не прочитан ({}) — качаю всё':
        'la liste d’exclusion n’a pas été lue ({}) — tout est téléchargé',
    'строка {} пропущена: {}':
        'ligne {} ignorée : {}',
    'уже работает: {}':
        'tourne déjà : {}',
    'уже скачано: {} роликов':
        'déjà téléchargées : {} vidéos',
    'файл настроек (по умолчанию {})':
        'fichier de réglages (par défaut {})',
    'что будет скачано, без изменений':
        'ce qui serait téléchargé, sans rien changer',
    'не заданы — YouTube откажет':
        'non définis — YouTube refusera',
    '{} роликов · {:.1f} ч · {:.0f}–{:.0f} ГБ':
        '{} vidéos · {:.1f} h · {:.0f}–{:.0f} Go',
    'замок брошен процессом {} — забираю':
        'verrou abandonné par le processus {} — je le prends',
    'замок протух: {} молчит слишком долго — забираю':
        'verrou périmé : {} se tait depuis trop longtemps — je le prends',
    'замок свободен':
        'le verrou est libre',
    'меряю…':
        'mesure…',
    'остановлено: {}':
        'arrêté : {}',
    'скачано {}':
        'téléchargées {}',
    'уже работает экземпляр {} — второй не нужен':
        'la copie {} tourne déjà — une seconde est inutile',
    'упало {} (заберутся следующим проходом)':
        '{} en échec (reprises au passage suivant)',
    'Новое название. Оно же станет именем папки — она переименуется вместе с каналом.':
        'Nouveau nom. Il devient aussi le nom du dossier : celui-ci est renommé avec la chaîne.',
    'Переименовать канал':
        'Renommer la chaîne',
    'Переименовать…':
        'Renommer…',
    'Сменить название канала вместе с его папкой.':
        'Changer le nom de la chaîne et de son dossier.',
    'в названии есть символы, недопустимые в имени папки':
        'le nom contient des caractères interdits dans un nom de dossier',
    'идёт проход выкачки — дождитесь его конца или остановите выкачку':
        'un passage est en cours — attendez sa fin ou arrêtez le téléchargement',
    'канал переименован: «{}» → «{}»':
        'chaîne renommée : « {} » → « {} »',
    'канал с таким названием уже есть':
        'une chaîne porte déjà ce nom',
    'название не может быть пустым':
        'le nom ne peut pas être vide',
    'название то же самое':
        'le nom est le même',
    'папка «{}» уже есть — сливать две папки молча нельзя':
        'le dossier « {} » existe déjà — deux dossiers ne sont jamais fusionnés en silence',
    'папку переименовать не вышло: {}':
        'impossible de renommer le dossier : {}',
    'такого канала в списке нет':
        'cette chaîne n’est pas dans la liste',
}
