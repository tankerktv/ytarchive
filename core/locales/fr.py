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
    # --- установщик ---
    '    на Debian и Ubuntu сначала нужно: sudo apt-get install python3-venv':
        '    sous Debian et Ubuntu, d’abord : sudo apt-get install python3-venv',
    'Python {} — подходит.':
        'Python {} — convient.',
    '[Д/н]':
        '[O/n]',
    '[д/Н]':
        '[o/N]',
    '{} — не найден, и я не знаю, чем его поставить на этой системе':
        '{} — introuvable, et je ne sais pas comment l’installer sur ce système',
    '{} — поставьте сами: {}':
        '{} — à installer vous-même : {}',
    'Архив YouTube — выкачка':
        'Archive YouTube — téléchargement',
    'Вхолостую: ничего не тронуто.':
        'Simulation : rien n’a été modifié.',
    'Выкачка новых роликов в фоне':
        'Télécharge les nouvelles vidéos en arrière-plan',
    'Выполнить?':
        'Exécuter ?',
    'Готово.':
        'Terminé.',
    'Запускать выкачку при входе в систему?':
        'Lancer le téléchargement à l’ouverture de session ?',
    'Исправьте причину и запустите установку ещё раз — сделанное не пропадёт.':
        'Corrigez la cause et relancez l’installation — ce qui est fait est conservé.',
    'Окно архива роликов':
        'Fenêtre de l’archive vidéo',
    'Осталось сделать руками:':
        'Reste à faire à la main :',
    'Остановился на шаге {}: дальше без него нельзя.':
        'Arrêt à l’étape {} : impossible de continuer sans elle.',
    'Открыть окно сейчас?':
        'Ouvrir la fenêtre maintenant ?',
    'Открыть окно:  {} {} gui':
        'Ouvrir la fenêtre : {} {} gui',
    'Отменено, ничего не тронуто.':
        'Annulé, rien n’a été modifié.',
    'Положить ярлык, открывающий окно?':
        'Créer un raccourci qui ouvre la fenêtre ?',
    'После установки node и ffmpeg откройте новый терминал: старый их не увидит.':
        'Après avoir installé node et ffmpeg, ouvrez un nouveau terminal : l’ancien ne les verra pas.',
    'Создать настройки: {} {} init':
        'Créer les réglages : {} {} init',
    'Спросить некого: запустите в терминале или добавьте --yes.':
        'Personne à qui demander : lancez-le dans un terminal ou ajoutez --yes.',
    'Установка ytarchive в {}':
        'Installation de ytarchive dans {}',
    'Установка ytarchive.':
        'Installer ytarchive.',
    'Что будет сделано:':
        'Ce qui sera fait :',
    'Что дальше — куки YouTube и первый канал — написано в INSTALL.ru.md.':
        'La suite — cookies YouTube et premier canal — est décrite dans INSTALL.md.',
    'без окна: только командная строка и выкачка':
        'sans fenêtre : ligne de commande et téléchargement seulement',
    'запускать выкачку при входе в систему':
        'lancer le téléchargement à l’ouverture de session',
    'не запускать выкачку при входе в систему':
        'ne pas lancer le téléchargement à l’ouverture de session',
    'не класть ярлык окна':
        'ne pas créer le raccourci de la fenêtre',
    'не получилось: {}':
        'échec : {}',
    'не спрашивать':
        'ne rien demander',
    'положить ярлык окна':
        'créer le raccourci de la fenêtre',
    'поставить {}: {}':
        'installer {} : {}',
    'поставить в окружение программы: {}':
        'installer dans l’environnement du programme : {}',
    'создать окружение Python в папке программы (.venv)':
        'créer un environnement Python dans le dossier du programme (.venv)',
    'только показать шаги, ничего не трогая':
        'seulement montrer les étapes, sans rien modifier',
    # --- надзор за скоростью, правила, уход за архивом ---
    '  не убрался {}: {}':
        '  non supprimé {} : {}',
    '  … и ещё {} (показать все: --limit 0)':
        '  … et {} de plus (tout afficher : --limit 0)',
    ' КиБ/с':
        ' Kio/s',
    '23-7 или 23:00-07:30 — пусто: всегда':
        '23-7 ou 23:00-07:30 — vide : toujours',
    'yt-dlp {} — {}':
        'yt-dlp {} — {}',
    'yt-dlp поставлен не этой программой — обновите его тем же способом, каким ставили.':
        'yt-dlp n’a pas été installé par ce programme — mettez-le à jour de la même façon que vous l’avez installé.',
    '{}: медленно идёт всё подряд — похоже, дело в линии. До конца прохода не снимаю; порог задаётся в [limits] crawl_speed':
        '{}: tout est lent — c’est sans doute la connexion. Plus de report jusqu’à la fin du passage ; le seuil se règle dans [limits] crawl_speed',
    '{}: пропущено по правилам канала {}':
        '{}: ignorées selon les règles de la chaîne : {}',
    '{}: ролик {} идёт медленнее {:.0f} КБ/с уже {:.0f} мин — откладываю до следующего прохода':
        '{}: la vidéo {} est plus lente que {:.0f} Ko/s depuis {:.0f} min — reportée au prochain passage',
    'Адрес плейлиста, ролика или вкладки videos канала:':
        'Adresse d’une playlist, d’une vidéo ou de l’onglet vidéos d’une chaîne :',
    'Архив YouTube — нужен человек':
        'Archive YouTube — on a besoin de vous',
    'В учёте есть, файла нет — такие ролики заново не скачаются: {}':
        'Enregistrées mais fichier absent — elles ne seront jamais retéléchargées : {}',
    'Выполнить':
        'Exécuter',
    'ГГГГ-ММ-ДД — пусто: любые':
        'AAAA-MM-JJ — vide : toutes',
    'Добавить по адресу':
        'Ajouter par adresse',
    'Добавить по адресу…':
        'Ajouter par adresse…',
    'Куки YouTube:':
        'Cookies YouTube :',
    'Название. Оно же станет именем папки в архиве:':
        'Nom. Ce sera aussi le nom du dossier dans l’archive :',
    'Не длиннее:':
        'Pas plus long que :',
    'Не короче, не длиннее, не старше — одной строкой вместо сотни галочек.':
        'Ni plus court, ni plus long, ni plus ancien — une ligne au lieu de cent cases.',
    'Не короче:':
        'Pas plus court que :',
    'Не старше:':
        'Pas plus ancien que :',
    'Ничего не тронуто. Убрать повторные строки: ytarchive verify --apply':
        'Rien n’a été modifié. Pour retirer les lignes en double : ytarchive verify --apply',
    'Ничего не тронуто. Убрать: ytarchive clean --apply':
        'Rien n’a été modifié. Pour supprimer : ytarchive clean --apply',
    'Обновить yt-dlp':
        'Mettre à jour yt-dlp',
    'Обновление yt-dlp':
        'Mise à jour de yt-dlp',
    'Один ролик в нескольких файлах: {}':
        'Une vidéo dans plusieurs fichiers : {}',
    'Откладывать загрузку медленнее:':
        'Reporter les téléchargements plus lents que :',
    'Плейлист, отдельный ролик или канал, которого нет в поиске.':
        'Une playlist, une vidéo seule ou une chaîne que la recherche ne trouve pas.',
    'Повторных строк в учёте: {} (безвредно)':
        'Lignes en double dans le registre : {} (sans gravité)',
    'Потолок скорости:':
        'Limite de débit :',
    'Правила канала — {}':
        'Règles de la chaîne — {}',
    'Правила отбора: {}':
        'Règles de sélection : {}',
    'Правила…':
        'Règles…',
    'Правило вычёркивает ролики из очереди, но ничего не удаляет с диска: снимете правило — ролики вернутся в очередь. Ролик, у которого длительность или дата неизвестны, правилу не подчиняется.':
        'Une règle retire des vidéos de la file mais ne supprime rien du disque : retirez la règle et elles reviennent. Une vidéo dont la durée ou la date est inconnue n’est pas concernée.',
    'Сверить учёт с диском':
        'Comparer le registre au disque',
    'Сверка учёта с диском':
        'Registre et disque',
    'Старые журналы и обломки загрузок. Сначала покажет, что уберёт.':
        'Anciens journaux et restes de téléchargements. Montre d’abord ce qui serait supprimé.',
    'Убирать нечего.':
        'Rien à supprimer.',
    'Убрать повторные строки':
        'Retirer les lignes en double',
    'Убрать показанное':
        'Supprimer ce qui est affiché',
    'Убрать старое…':
        'Supprimer l’ancien…',
    'Учёт и диск сходятся.':
        'Le registre et le disque concordent.',
    'Файл есть, в учёте нет — такие ролики скачаются второй раз: {}':
        'Fichier présent mais non enregistré — elles seront téléchargées une seconde fois : {}',
    'Часы работы:':
        'Heures de fonctionnement :',
    'Чинить нечего: остальное — решение человека, а не программы.':
        'Rien à réparer : le reste relève de votre décision, pas du programme.',
    'Что можно убрать':
        'Ce qui peut être supprimé',
    'без потолка':
        'sans limite',
    'в учёте строк: {}, роликов на диске: {}':
        'lignes dans le registre : {}, vidéos sur le disque : {}',
    'вне часов работы — жду до {}':
        'hors des heures de fonctionnement — attente jusqu’à {}',
    'готово':
        'terminé',
    'журналов старше {} суток: {} ({:.1f} МБ)':
        'journaux de plus de {} jours : {} ({:.1f} Mo)',
    'закончено с замечаниями':
        'terminé avec des remarques',
    'идёт выкачка — учёт сейчас править нельзя ({})':
        'un téléchargement est en cours — le registre ne peut pas être modifié maintenant ({})',
    'из браузера {}':
        'depuis le navigateur {}',
    'из файла cookies.txt':
        'depuis le fichier cookies.txt',
    'не добавлен: {}':
        'non ajouté : {}',
    'не ограничено':
        'sans limite',
    'не проверять':
        'ne pas vérifier',
    'обломков загрузок, которые уже не пригодятся: {} ({:.1f} МБ)':
        'restes de téléchargements devenus inutiles : {} ({:.1f} Mo)',
    'обновить yt-dlp':
        'mettre à jour yt-dlp',
    'обновлён: {} → {}':
        'mis à jour : {} → {}',
    'папка {} не прочитана: {}':
        'dossier {} illisible : {}',
    'работаю…':
        'en cours…',
    'сверить учёт с файлами на диске':
        'comparer le registre aux fichiers du disque',
    'сколько строк каждого перечня показать (0 — все)':
        'combien de lignes de chaque liste afficher (0 — toutes)',
    'старые журналы и обломки загрузок':
        'anciens journaux et restes de téléchargements',
    'убрано журналов старше {} суток: {}':
        'journaux de plus de {} jours supprimés : {}',
    'убрано повторных строк: {}; прежний учёт сохранён как {}':
        'lignes en double retirées : {} ; l’ancien registre est conservé sous {}',
    'убрано файлов: {}':
        'fichiers supprimés : {}',
    'убрать повторные строки учёта':
        'retirer les lignes en double du registre',
    'убрать, а не только показать':
        'supprimer, pas seulement afficher',
    'уже последняя версия: {}':
        'déjà la dernière version : {}',
    'учёт не записан: {}':
        'registre non écrit : {}',
    'учёт не прочитан: {}':
        'registre illisible : {}',
    # --- новый вид окна ---
    'YouTube не отдаёт ролики без входа в аккаунт. Выберите в настройках браузер, в котором вы вошли в YouTube, или положите файл cookies.txt.':
        'YouTube ne fournit pas les vidéos sans connexion. Choisissez dans les réglages le navigateur où vous êtes connecté à YouTube, ou déposez un fichier cookies.txt.',
    '{:.2f} ТБ':
        '{:.2f} To',
    'Архив':
        'Archive',
    'В папке архива лежат ролики в папках, которых нет в списке: {}. Так выглядит канал, переименованный в файле руками.':
        'Le dossier d’archive contient des vidéos dans des dossiers absents de la liste : {}. C’est l’aspect d’une chaîne renommée à la main dans le fichier.',
    'Дата':
        'Date',
    'Дата примерная: YouTube в списке канала пишет «3 года назад». Точная появится, когда ролик будет скачан.':
        'La date est approximative : dans la liste d’une chaîne, YouTube indique « il y a 3 ans ». La date exacte apparaît une fois la vidéo téléchargée.',
    'Добавить канал':
        'Ajouter une chaîne',
    'Журнал':
        'Journal',
    'Каналов пока нет. Добавьте первый — программа покажет, сколько в нём роликов и хватит ли места, ещё до того, как начнёт качать.':
        'Aucune chaîne pour l’instant. Ajoutez la première — le programme indique combien de vidéos elle contient et s’il y a la place, avant de télécharger quoi que ce soit.',
    'Мои каналы':
        'Mes chaînes',
    'Осторожность':
        'Prudence',
    'Открыть настройки':
        'Ouvrir les réglages',
    'Показать':
        'Afficher',
    'Сеть и расписание':
        'Réseau et horaires',
    'Скрыть':
        'Masquer',
    'Уход за архивом':
        'Entretien de l’archive',
    'Что качать':
        'Quoi télécharger',
    'ждёт следующего прохода':
        'en attente du prochain passage',
    'каналов в списке':
        'chaînes dans la liste',
    'объём архива':
        'taille de l’archive',
    'роликов в архиве':
        'vidéos dans l’archive',
    'свободно на диске':
        'libre sur le disque',
    'yt-dlp не получает ролики, только раскадровки — обновите yt-dlp кнопкой в настройках':
        'yt-dlp n’obtient que des storyboards, pas les vidéos — mettez yt-dlp à jour avec le bouton des réglages',
}
