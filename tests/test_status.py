"""Проверки снимка состояния.

Состояние собирается из живого снимка, а не из текста журнала. Раньше было
наоборот — в строках искались «остановлено — » и «: проверка — », — и пока
журнал был только по-русски, это работало. С переводом журнала окно ослепло
бы молча, а слепота без предупреждения хуже слепоты.

Главное свойство осталось прежним: **свежесть журнала не признак работы.**
Журнал разрежен, и двухчасовой ролик даёт двухчасовую тишину при полностью
здоровой выкачке. Поэтому «работает ли» приходит снаружи, от того, кто видит
процессы.
"""

from core.livestate import LiveState
from core.status import RunState, build_status


def test_ничего_не_известно_и_процесс_мёртв():
    состояние = build_status(process_running=False, archive_count=1527)
    assert состояние.state is RunState.IDLE
    assert "1527" in состояние.headline()


def test_живой_процесс_качает():
    живое = LiveState(channel="SoyuzUS", file_name="Мы купили Джип. [Xv82JVLZ8ew].mp4")
    состояние = build_status(process_running=True, live=живое)

    assert состояние.state is RunState.RUNNING
    assert "Мы купили Джип" in состояние.current_file
    assert состояние.channel == "SoyuzUS"


def test_настоящий_случай_двухчасовой_ролик_не_считается_простоем():
    """Ролик SoyuzUS на 4,7 ГБ качается 2 ч 49 мин, и всё это время журнал
    молчит. Судили бы по свежести — сочли бы выкачку мёртвой, и человек полез
    бы её «чинить».
    """
    живое = LiveState(file_name="С домом на колёсах по каньонам США. [rbYUHA9ZOg8].mp4")

    assert build_status(process_running=True, live=живое).state is RunState.RUNNING
    assert build_status(process_running=False, live=живое).state is RunState.IDLE


def test_пауза_между_роликами_это_работа():
    живое = LiveState(file_name="что-то.mp4", sleeping=True)
    состояние = build_status(process_running=True, live=живое)

    assert состояние.state is RunState.BETWEEN
    assert состояние.state.is_working


def test_остановка_требует_человека_даже_при_живом_процессе():
    """Процесс ещё жив, но делать ему нечего: куки сами не появятся.
    Показать «качает» значило бы соврать.
    """
    живое = LiveState(stopped_reason="нужен вход в аккаунт YouTube")
    состояние = build_status(process_running=True, live=живое)

    assert состояние.state is RunState.NEEDS_HUMAN
    assert "вход в аккаунт" in состояние.headline()


def test_отказы_считаются():
    assert build_status(process_running=True, live=LiveState(errors=3)).errors == 3


def test_размер_и_скорость_последнего_файла():
    живое = LiveState(size_bytes=630_911_795, speed_bps=36_300_000.0)
    состояние = build_status(process_running=True, live=живое)

    assert состояние.last_size_bytes == 630_911_795
    assert состояние.last_speed_bps == 36_300_000.0


def test_у_остановленной_не_показываем_текущий_файл():
    """Файл, который качался в момент остановки, уже не качается. Оставить
    его на виду — сказать, что работа идёт.
    """
    живое = LiveState(file_name="что-то.mp4", stopped_reason="сетевой сбой")
    assert build_status(process_running=True, live=живое).current_file == ""


def test_шапка_читается_человеком():
    живое = LiveState(file_name="Мы купили Джип. [Xv82JVLZ8ew].mp4")
    шапка = build_status(process_running=True, live=живое).headline()

    assert "качает" in шапка
    assert "Джип" in шапка


def test_шапка_переводится():
    """Переводчик передаётся доводом: ядру нельзя знать ни про язык
    интерфейса, ни про то, откуда он берётся.
    """
    словарь = {"не запущена": "not running", "в архиве {} роликов": "{} videos archived"}
    шапка = build_status(process_running=False, archive_count=7).headline(
        lambda с: словарь.get(с, с)
    )

    assert "not running" in шапка
    assert "7 videos archived" in шапка


def test_без_снимка_не_роняем():
    """Окно наблюдения не имеет права падать. Снимка может не быть вовсе —
    выкачка ещё ни разу не запускалась.
    """
    состояние = build_status(process_running=True, live=None)
    assert состояние.state is RunState.RUNNING
    assert состояние.current_file == ""
