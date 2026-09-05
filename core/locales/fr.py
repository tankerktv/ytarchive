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
}
