"""Проверки разбора списка каналов.

Здесь тоже большая часть — на отказ. Молчаливо отброшенный канал означает,
что он просто перестанет качаться, и заметят это через недели.
"""

from core.channels import parse_channels


def test_обычный_разбор():
    result = parse_channels("SoyuzUS|https://www.youtube.com/@SoyuzUS/videos\n")
    assert result.problems == ()
    assert len(result.channels) == 1
    assert result.channels[0].name == "SoyuzUS"
    assert result.channels[0].url == "https://www.youtube.com/@SoyuzUS/videos"


def test_комментарии_и_пустые_строки_пропускаются():
    text = "# список каналов\n\nSoyuzUS|https://www.youtube.com/@SoyuzUS/videos\n\n"
    result = parse_channels(text)
    assert len(result.channels) == 1
    assert result.problems == ()


def test_пробелы_вокруг_полей_обрезаются():
    result = parse_channels("  SoyuzUS  |  https://www.youtube.com/@SoyuzUS/videos  \n")
    assert result.channels[0].name == "SoyuzUS"
    assert result.channels[0].url.endswith("/videos")


def test_порядок_каналов_сохраняется():
    # Порядок задаёт очередь обхода — он должен быть тем, что написал человек.
    text = (
        "Первый|https://example.com/a\n"
        "Второй|https://example.com/b\n"
        "Третий|https://example.com/c\n"
    )
    assert [c.name for c in parse_channels(text).channels] == ["Первый", "Второй", "Третий"]


def test_строка_без_разделителя_не_теряется():
    result = parse_channels("просто текст без разделителя\n")
    assert result.channels == ()
    assert len(result.problems) == 1
    assert result.problems[0].line_number == 1
    assert "разделител" in result.problems[0].reason


def test_отказ_на_пустом_названии():
    result = parse_channels("|https://example.com/a\n")
    assert result.channels == ()
    assert "название" in result.problems[0].reason


def test_отказ_на_пустом_адресе():
    result = parse_channels("Канал|\n")
    assert result.channels == ()
    assert "адрес" in result.problems[0].reason


def test_отказ_на_адресе_без_схемы():
    # Без схемы это не адрес, а обрывок — качать по нему нечего.
    result = parse_channels("Канал|www.youtube.com/@X/videos\n")
    assert result.channels == ()
    assert "http" in result.problems[0].reason


def test_отказ_на_недопустимых_символах_в_названии():
    # Название уезжает в имя папки. Узнать о беде лучше при разборе списка,
    # чем на середине скачивания.
    result = parse_channels('Канал: часть 2|https://example.com/a\n')
    assert result.channels == ()
    assert "папк" in result.problems[0].reason


def test_отказ_на_тёзках():
    # Два канала в одну папку — перемешанный архив, который потом не разобрать.
    text = "Канал|https://example.com/a\nКанал|https://example.com/b\n"
    result = parse_channels(text)
    assert len(result.channels) == 1
    assert len(result.problems) == 1
    assert "строку 1" in result.problems[0].reason


def test_одна_плохая_строка_не_роняет_остальные():
    # Ошибка в одной строке не должна оставлять человека без всех каналов.
    text = (
        "Хороший|https://example.com/a\n"
        "плохая строка\n"
        "Тоже хороший|https://example.com/b\n"
    )
    result = parse_channels(text)
    assert [c.name for c in result.channels] == ["Хороший", "Тоже хороший"]
    assert result.problems[0].line_number == 2


def test_настоящий_случай_2026_08_16_подвальчик_только_по_id():
    """У «Уютного подвальчика» хендл не угадывается — ни @uytniypodvalchik,
    ни @podvalchik, ни @UytnyPodvalchik не существуют, все дали 404.

    Канал открывается только по идентификатору. Разбор обязан принимать такой
    адрес наравне с хендлом, иначе канал не добавить вовсе.
    """
    text = "Уютный подвальчик|https://www.youtube.com/channel/UCeemTTAKVjHucKYFmc8V3Ug/videos\n"
    result = parse_channels(text)

    assert result.problems == ()
    assert result.channels[0].name == "Уютный подвальчик"
    assert "UCeemTTAKVjHucKYFmc8V3Ug" in result.channels[0].url


def test_настоящий_случай_2026_08_16_пробел_в_названии_допустим():
    """Название «Уютный подвальчик» с пробелом — законное имя папки,
    отбрасывать его нельзя.
    """
    result = parse_channels("Уютный подвальчик|https://example.com/a\n")
    assert result.problems == ()
    assert result.channels[0].name == "Уютный подвальчик"


# --- запись списка ----------------------------------------------------------


def test_запись_и_чтение_списка_обратимы():
    """Окно правит этот файл. Потеря канала при записи означала бы, что он
    просто перестанет качаться — молча, пока кто-нибудь не заметит.
    """
    from core.channels import format_channels

    исходный = parse_channels(
        "SoyuzUS|https://www.youtube.com/@SoyuzUS/videos\n"
        "Уютный подвальчик|https://www.youtube.com/channel/UCeemTTAKVjHucKYFmc8V3Ug/videos\n"
    )
    повторный = parse_channels(format_channels(исходный.channels))

    assert повторный.channels == исходный.channels
    assert повторный.problems == ()


def test_пустой_список_записывается_без_поломки():
    from core.channels import format_channels

    текст = format_channels([])
    assert parse_channels(текст).channels == ()


def test_в_записанном_списке_остаётся_объяснение_формата():
    from core.channels import format_channels

    assert "Формат:" in format_channels([])
