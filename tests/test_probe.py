"""Проверки разбора ответа yt-dlp.

Это разбор чужого формата — категория, где тесты окупаются лучше всего:
вывод меняется от версии к версии, и заметить это без проверок нельзя.

Половина случаев взята дословно из журналов выкачки за 16–29.08.2026.
"""

from core.probe import Diagnosis, diagnose


def test_успех_когда_отдан_идентификатор():
    итог = diagnose("rbYUHA9ZOg8\n", 0)
    assert итог.diagnosis is Diagnosis.OK
    assert итог.video_ids == ("rbYUHA9ZOg8",)
    assert итог.is_ok


def test_несколько_идентификаторов():
    итог = diagnose("rbYUHA9ZOg8\naRbfazQ_Cns\n", 0)
    assert итог.video_ids == ("rbYUHA9ZOg8", "aRbfazQ_Cns")


def test_шум_вокруг_идентификатора_не_мешает():
    вывод = "[youtube:tab] Extracting URL\nrbYUHA9ZOg8\n[download] Finished\n"
    assert diagnose(вывод, 0).video_ids == ("rbYUHA9ZOg8",)


def test_нужен_вход_в_аккаунт():
    вывод = "ERROR: [youtube] rbYUHA9ZOg8: Sign in to confirm you're not a bot."
    assert diagnose(вывод, 1).diagnosis is Diagnosis.LOGIN_REQUIRED


def test_нет_движка_javascript():
    вывод = "WARNING: [youtube] No supported JavaScript runtime could be found."
    assert diagnose(вывод, 1).diagnosis is Diagnosis.NO_JS_RUNTIME


def test_не_решается_задача():
    вывод = "WARNING: [youtube] n challenge solving failed: Some formats may be missing."
    assert diagnose(вывод, 1).diagnosis is Diagnosis.CHALLENGE_FAILED


def test_сетевой_сбой():
    вывод = "ERROR: Unable to download API page: [Errno 11001] getaddrinfo failed"
    assert diagnose(вывод, 1).diagnosis is Diagnosis.NETWORK


def test_сеть_проверяется_раньше_входа():
    """При обрыве связи YouTube тоже отвечает «подтвердите, что вы не бот».

    Если спутать эти два случая, человека погонят заново входить в аккаунт,
    хотя чинить надо сеть — и наоборот, сетевой сбой будут пережидать,
    когда на самом деле слетела сессия.
    """
    вывод = (
        "ERROR: getaddrinfo failed\n"
        "ERROR: Sign in to confirm you're not a bot.\n"
    )
    assert diagnose(вывод, 1).diagnosis is Diagnosis.NETWORK


def test_частичная_выдача_вперемешку_с_отказом_это_отказ():
    вывод = "rbYUHA9ZOg8\nERROR: [youtube] Sign in to confirm you're not a bot."
    итог = diagnose(вывод, 1)
    assert итог.diagnosis is Diagnosis.LOGIN_REQUIRED
    assert not итог.is_ok


def test_неопознанный_отказ():
    итог = diagnose("ERROR: что-то совсем новое\n", 1)
    assert итог.diagnosis is Diagnosis.UNKNOWN
    assert "что-то совсем новое" in итог.detail


def test_проходящие_и_непроходящие_беды():
    # Сетевое пройдёт само — блокировка DNS у нас отпускала через минуты.
    assert Diagnosis.NETWORK.is_transient
    # Отсутствие входа и движка само не починится, ждать бессмысленно.
    assert not Diagnosis.LOGIN_REQUIRED.is_transient
    assert not Diagnosis.NO_JS_RUNTIME.is_transient


def test_настоящий_случай_2026_08_16_устаревший_ytdlp_молчит_с_кодом_ноль():
    """yt-dlp версии 2023.10.13 на современном YouTube завершался УСПЕШНО
    и печатал пустой список. Проверка «код возврата ноль» отвечала «всё хорошо».

    Симптом выглядел как «на канале нет роликов», а на деле программа была
    устаревшей на три года. Это отдельный диагноз, а не пустой канал.
    """
    итог = diagnose("", 0)

    assert итог.diagnosis is Diagnosis.EMPTY_LISTING
    assert not итог.is_ok
    assert "устаревш" in итог.detail


def test_настоящий_случай_2026_08_16_login_required_на_роликах_каналов():
    """16.08 посторонний популярный ролик отдавался, а ролики нужных каналов
    отвечали LOGIN_REQUIRED. Первая версия проверки на этом и обманулась.

    Разбор обязан опознать этот ответ как «нужен вход», а не как сетевую беду.
    """
    вывод = (
        "[debug] [youtube] rbYUHA9ZOg8: android_vr player response "
        "playability status: LOGIN_REQUIRED\n"
        "ERROR: [youtube] rbYUHA9ZOg8: Sign in to confirm you're not a bot."
    )
    assert diagnose(вывод, 1).diagnosis is Diagnosis.LOGIN_REQUIRED


def test_настоящий_случай_2026_08_29_блокировка_dns():
    """С 24 по 29.08 в журналах накопилось 458, потом 1011 ошибок getaddrinfo —
    домен youtube.com перемежающе не разрешался.

    Такое проходит само, и выкачка обязана это переждать, а не звать человека.
    """
    вывод = (
        'ERROR: Unable to download API page: [Errno 11001] getaddrinfo failed '
        "(caused by TransportError('[Errno 11001] getaddrinfo failed'))"
    )
    итог = diagnose(вывод, 1)

    assert итог.diagnosis is Diagnosis.NETWORK
    assert итог.diagnosis.is_transient


def test_настоящий_случай_2026_08_29_ложная_проверка_прав_на_вкладку():
    """При неудачной загрузке страницы yt-dlp советует skip=authcheck, и это
    выглядит как проблема с правами на канал. У нас оно появилось 29.08
    как следствие провала DNS — ложный след, стоивший времени.

    Причину приписывать нечестно: то же сообщение появится и при настоящей
    нехватке прав. Диагноз отдельный, а вывод один — повторить попытку.
    """
    вывод = (
        "ERROR: [youtube:tab] @SoyuzUS: Playlists that require authentication "
        "may not extract correctly without a successful webpage download."
    )
    итог = diagnose(вывод, 1)

    assert итог.diagnosis is Diagnosis.TAB_AUTHCHECK
    assert итог.diagnosis.is_transient


def test_общие_беды_отделены_от_частных():
    """Сеть либо есть, либо нет — убедившись на первом канале, перебирать
    остальные бессмысленно. 30.08 это стоило шести минут и четырёх
    одинаковых записей «остановлено» вместо одной внятной.
    """
    assert Diagnosis.NETWORK.is_global
    assert Diagnosis.LOGIN_REQUIRED.is_global
    assert Diagnosis.NO_JS_RUNTIME.is_global
    assert Diagnosis.EMPTY_LISTING.is_global

    # А эти могут быть особенностью конкретного канала.
    assert not Diagnosis.TAB_AUTHCHECK.is_global
    assert not Diagnosis.UNKNOWN.is_global
    assert not Diagnosis.OK.is_global
