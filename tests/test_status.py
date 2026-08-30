"""Проверки снимка состояния.

Все образцы строк — из настоящих журналов выкачки. Главное свойство здесь:
**свежесть журнала не признак работы.** Журнал разрежен, и двухчасовой ролик
даёт двухчасовую тишину при полностью здоровой выкачке.
"""

from core.status import RunState, Status, build_status

ЖУРНАЛ = [
    "16:48:21  замок свободен",
    "16:48:23  SoyuzUS: проверка — доступ есть, форматы отдаются",
    "16:43:54    качаю 2026-08-29 - Мы купили Джип. [Xv82JVLZ8ew].mp4",
    "16:44:11      готово 601.7 МБ, 34.62 МБ/с",
]


def test_пустой_журнал_при_мёртвом_процессе():
    состояние = build_status([], process_running=False, archive_count=1527)
    assert состояние.state is RunState.IDLE
    assert "1527" in состояние.headline()


def test_живой_процесс_качает():
    состояние = build_status(ЖУРНАЛ, process_running=True)
    assert состояние.state is RunState.RUNNING
    assert "Мы купили Джип" in состояние.current_file
    assert состояние.channel == "SoyuzUS"


def test_настоящий_случай_двухчасовой_ролик_не_считается_простоем():
    """Ролик SoyuzUS на 4,7 ГБ качается 2 ч 49 мин, и всё это время журнал молчит.

    Если судить по свежести журнала, выкачку сочли бы мёртвой и человек полез
    бы её «чинить». Признак работы приходит снаружи, от того, кто видит процессы.
    """
    журнал = ["16:43:54    качаю 2026-08-15 - С домом на колёсах по каньонам США. [rbYUHA9ZOg8].mp4"]

    живая = build_status(журнал, process_running=True)
    мёртвая = build_status(журнал, process_running=False)

    assert живая.state is RunState.RUNNING
    assert мёртвая.state is RunState.IDLE


def test_пауза_между_роликами_это_работа():
    журнал = ЖУРНАЛ + ["[download] Sleeping 26.78 seconds ..."]
    состояние = build_status(журнал, process_running=True)

    assert состояние.state is RunState.BETWEEN
    assert состояние.state.is_working


def test_загрузка_после_паузы_снова_качает():
    журнал = ЖУРНАЛ + [
        "[download] Sleeping 26.78 seconds ...",
        "16:49:02    качаю 2026-08-28 - Следующий. [aaaaaaaaaaa].mp4",
    ]
    assert build_status(журнал, process_running=True).state is RunState.RUNNING


def test_остановка_требует_человека_даже_при_живом_процессе():
    """Остановленный канал важнее того, что процесс ещё дышит: без человека
    дальше ничего не будет.
    """
    журнал = ЖУРНАЛ + ["16:50:00  MurkPOWER: остановлено — нужен вход в аккаунт YouTube"]
    состояние = build_status(журнал, process_running=True)

    assert состояние.state is RunState.NEEDS_HUMAN
    assert "вход в аккаунт" in состояние.stopped_reason
    assert "вход в аккаунт" in состояние.headline()


def test_отказы_считаются():
    журнал = ЖУРНАЛ + [
        "ERROR: [youtube] G02jtMoGy2g: Sign in to confirm.",
        "ERROR: [youtube] IMyAvT64D8g: getaddrinfo failed",
    ]
    assert build_status(журнал, process_running=True).errors == 2


def test_размер_и_скорость_последнего_файла():
    состояние = build_status(
        ["[download] 100% of  462.12MiB in 00:01:46 at 4.35MiB/s"], process_running=True
    )
    assert состояние.last_size_bytes == int(462.12 * 1024**2)
    assert состояние.last_speed_bps is not None


def test_имя_файла_без_пути():
    журнал = [r"[download] Destination: D:\Video\Архивы с YouTube\SoyuzUS\ролик.f399.mp4"]
    assert build_status(журнал, process_running=True).current_file == "ролик.f399.mp4"


def test_у_остановленной_не_показываем_текущий_файл():
    # Иначе человек решит, что что-то ещё качается.
    журнал = ЖУРНАЛ + ["16:50:00  SoyuzUS: остановлено — куки истекли"]
    assert build_status(журнал, process_running=True).current_file == ""


def test_шапка_читается_человеком():
    состояние: Status = build_status(ЖУРНАЛ, process_running=True)
    строка = состояние.headline()
    assert "качает" in строка
    assert "Джип" in строка
