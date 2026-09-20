from math import isnan

import pytest
import spacy

from ruts import VerseStats
from ruts.constants import VERSE_STATS_DESC
from ruts.datasets import StressDict
from ruts.datasets.stress_dict import FILENAME
from ruts.exceptions import SourceError, SourceTypeError
from ruts.verse_stats import (
    _ending_key,
    _group_labels,
    _rhymes,
    accentuate,
    detect_meter,
    rhyme_scheme,
    split_stanzas,
    word_stress,
)

ROWS = (
    ("без", "б^ез"),
    ("бога", "б^ога"),
    ("бором", "б^ором"),
    ("будто", "б^удто"),
    ("буря", "б^уря"),
    ("бушует", "буш^ует"),
    ("был", "б^ыл"),
    ("в", "в"),
    ("весна", "весн^а"),
    ("ветер", "в^етер"),
    ("вечные", "в^ечные"),
    ("виденье", "вид^енье"),
    ("вихри", "в^ихри"),
    ("владенья", "влад^енья"),
    ("воевода", "воев^ода"),
    ("воды", "в^оды"),
    ("все", "вс^е"),
    ("всех", "вс^ех"),
    ("вы", "в^ы"),
    ("выдумать", "в^ыдумать"),
    ("гений", "г^ений"),
    ("гор", "г^ор"),
    ("девушка", "д^евушка"),
    ("дитя", "д^итя"),
    ("дозором", "доз^ором"),
    ("друг", "др^уг"),
    ("друга", "др^уга"),
    ("дядя", "д^ядя"),
    ("елка", "^елка"),
    ("еще", "^еще"),
    ("же", "ж^е"),
    ("желание", "жел^ание"),
    ("желания", "жел^ания"),
    ("жемчужною", "жемч^ужною"),
    ("жизнь", "ж^изнь"),
    ("забывший", "заб^ывший"),
    ("забывших", "заб^ывших"),
    ("завоет", "зав^оет"),
    ("замок", "зам^ок"),
    ("занемог", "занем^ог"),
    ("заплачет", "запл^ачет"),
    ("заставил", "заст^авил"),
    ("зверь", "зв^ерь"),
    ("звоном", "зв^оном"),
    ("и", "^и"),
    ("изгнанники", "изгн^анники"),
    ("каждая", "к^аждая"),
    ("как", "к^ак"),
    ("когда", "когд^а"),
    ("конца", "конц^а"),
    ("кораблях", "корабл^ях"),
    ("корова", "кор^ова"),
    ("красоты", "крас^оты"),
    ("краю", "кра^ю"),
    ("кроет", "кр^оет"),
    ("крутя", "крут^я"),
    ("кто-нибудь", "кт^о-нибудь"),
    ("лазурною", "лаз^урною"),
    ("лучше", "л^учше"),
    ("мглою", "мгл^ою"),
    ("мгновенье", "мгнов^енье"),
    ("мечта", "мечт^а"),
    ("мил", "м^ил"),
    ("милого", "м^илого"),
    ("мимолетное", "мимол^етное"),
    ("мной", "мн^ой"),
    ("моем", "мо^ем"),
    ("мог", "м^ог"),
    ("мой", "м^ой"),
    ("море", "м^оре"),
    ("много", "мн^ого"),
    ("мороз", "мор^оз"),
    ("мчитесь", "мч^итесь"),
    ("на", "н^а"),
    ("над", "н^ад"),
    ("не", "н^е"),
    ("небесные", "неб^есные"),
    ("небо", "н^ебо"),
    ("несчастлива", "несч^астлива"),
    ("несчастливая", "несчастл^ивая"),
    ("о", "^о"),
    ("обходит", "обх^одит"),
    ("окне", "окн^е"),
    ("он", "^он"),
    ("она", "он^а"),
    ("пела", "п^ела"),
    ("передо", "пер^едо"),
    ("плывут", "плыв^ут"),
    ("по-прежнему", "по-пр^ежнему"),
    ("по-своему", "по-св^оему"),
    ("побежали", "побеж^али"),
    ("помню", "п^омню"),
    ("похожи", "пох^ожи"),
    ("правил", "пр^авил"),
    ("прежнему", "пр^ежнему"),
    ("приветствую", "прив^етствую"),
    ("принимаю", "приним^аю"),
    ("радость", "р^адость"),
    ("реки", "р^еки"),
    ("ручьи", "ручь^и"),
    ("с", "с"),
    ("самых", "с^амых"),
    ("свои", "сво^и"),
    ("свою", "сво^ю"),
    ("себя", "себ^я"),
    ("севера", "с^евера"),
    ("семьи", "с^емьи"),
    ("семья", "семь^я"),
    ("снежные", "сн^ежные"),
    ("степью", "ст^епью"),
    ("стоит", "сто^ит"),
    ("сторону", "ст^орону"),
    ("странники", "стр^анники"),
    ("счастливые", "счастл^ивые"),
    ("тебя", "теб^я"),
    ("то", "т^о"),
    ("тучки", "т^учки"),
    ("ты", "т^ы"),
    ("уважать", "уваж^ать"),
    ("узнаю", "узн^аю"),
    ("усталых", "уст^алых"),
    ("ушедших", "уш^едших"),
    ("хоре", "хор^е"),
    ("цепью", "ц^епью"),
    ("церковном", "церк^овном"),
    ("честных", "ч^естных"),
    ("черные", "ч^ерные"),
    ("чистой", "ч^истой"),
    ("чудное", "ч^удное"),
    ("чужом", "чуж^ом"),
    ("шкурою", "шк^урою"),
    ("шутку", "ш^утку"),
    ("щита", "щит^а"),
    ("южную", "^южную"),
    ("я", "^я"),
    ("явилась", "яв^илась"),
)
ONEGIN = """Мой дядя самых честных правил,
Когда не в шутку занемог,
Он уважать себя заставил
И лучше выдумать не мог."""
CLOUDS = """Тучки небесные, вечные странники!
Степью лазурною, цепью жемчужною
Мчитесь вы, будто как я же, изгнанники,
С милого севера в сторону южную."""
STORM = """Буря мглою небо кроет,
Вихри снежные крутя;
То, как зверь, она завоет,
То заплачет, как дитя,"""
FROST = """Не ветер бушует над бором,
Не с гор побежали ручьи,
Мороз-воевода дозором
Обходит владенья свои."""
SPRING = """О, весна без конца и без краю —
Без конца и без краю мечта!
Узнаю тебя, жизнь! Принимаю!
И приветствую звоном щита!"""
CHOIR = """Девушка пела в церковном хоре
О всех усталых в чужом краю,
О всех кораблях, ушедших в море,
О всех, забывших радость свою."""
PROSE = (
    "Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему."
)


@pytest.fixture(scope="module")
def stress_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    lines = "\n".join("\t".join(row) for row in sorted(ROWS)) + "\n"
    path.joinpath(FILENAME).write_text(lines, encoding="utf-8")
    return StressDict(data_dir=path)


@pytest.fixture(scope="module")
def nlp():
    return spacy.load("ru_core_news_sm")


def test_word_stress(stress_dict):
    assert word_stress("корова", stress_dict) == 1
    assert word_stress("Корова", stress_dict) == 1
    assert word_stress("ёжик", stress_dict) == 0
    assert word_stress("мой", stress_dict) == 0
    assert word_stress("еще", stress_dict) == 1
    assert word_stress("ещё", stress_dict) == 1
    assert word_stress("бою", stress_dict) == 1
    assert word_stress("спешит", stress_dict) == 1
    assert word_stress("кто-нибудь", stress_dict) == 0
    assert word_stress("по-прежнему", stress_dict) == 1
    assert word_stress("мороз-воевода", stress_dict) == 4
    assert word_stress("все-таки", stress_dict) == 0
    assert word_stress("желанье", stress_dict) == 1
    assert word_stress("желанья", stress_dict) == 1
    assert word_stress("забыв", stress_dict) == 1
    assert word_stress("забывши", stress_dict) == 1
    assert word_stress("собака", stress_dict) is None
    assert word_stress("собака-корова", stress_dict) is None
    assert word_stress("вздрогнув", stress_dict) is None
    assert word_stress("ь", stress_dict) is None
    assert word_stress("xyz", stress_dict) is None


def test_iamb(stress_dict):
    vs = VerseStats(ONEGIN, stress_dict)
    assert vs.n_lines == 4
    assert vs.n_stanzas == 1
    assert vs.lines[0] == "Мой дядя самых честных правил,"
    assert vs.stanzas == (vs.lines,)
    assert vs.mean_line_len == 8.5
    assert vs.meter == "ямб"
    assert vs.n_feet == 4
    assert vs.c_feet == {4: 4}
    assert vs.p_deviations == 0.0
    assert vs.p_pyrrhics == pytest.approx(3 / 16)
    assert vs.stress_profile == (0.75, 1.0, 0.5, 1.0)
    assert vs.stresses[0] == (1, 3, 5, 7)
    assert vs.stresses[1] == (1, 3, 7)
    assert vs.patterns == ("cCcCcCcCc", "cCcCcccC", "cccCcCcCc", "cCcCcccC")
    assert vs.rhyme_schemes == ("ABAB",)
    assert vs.p_rhymed == 1.0
    assert vs.c_clausulas == {"мужская": 2, "женская": 2}
    assert vs.p_masculine == 0.5
    assert vs.p_feminine == 0.5
    assert vs.p_dactylic == 0.0
    assert vs.c_stressed_vowels["а"] == 5
    assert vs.c_stressed_vowels["я"] == 2
    assert vs.accentuate().split("\n")[1] == "Когда́ не в шу́тку занемо́г,"
    assert vs.get_stats() == {
        "n_lines": 4,
        "n_stanzas": 1,
        "meter": "ямб",
        "n_feet": 4,
        "p_deviations": 0.0,
        "p_pyrrhics": pytest.approx(3 / 16),
        "p_rhymed": 1.0,
        "p_masculine": 0.5,
        "p_feminine": 0.5,
        "p_dactylic": 0.0,
    }
    assert list(vs.get_stats()) == list(VERSE_STATS_DESC)


def test_other_meters(stress_dict):
    clouds = VerseStats(CLOUDS, stress_dict)
    assert (clouds.meter, clouds.n_feet) == ("дактиль", 4)
    assert clouds.patterns[0] == "CccCccCccCcc"
    assert clouds.c_clausulas == {"дактилическая": 4}
    assert clouds.p_dactylic == 1.0
    assert clouds.rhyme_schemes == ("ABAB",)
    storm = VerseStats(STORM, stress_dict)
    assert (storm.meter, storm.n_feet) == ("хорей", 4)
    assert storm.patterns[1] == "CcCcccC"
    frost = VerseStats(FROST, stress_dict)
    assert (frost.meter, frost.n_feet) == ("амфибрахий", 3)
    assert frost.patterns[2] == "ccccCccCc"
    spring = VerseStats(SPRING, stress_dict)
    assert (spring.meter, spring.n_feet) == ("анапест", 3)
    # Словарное краю́ подогнано под метр, узна́ю в анакрузе не считается отклонением
    assert spring.accentuate().split("\n")[0] == "О, весна́ без конца́ и без кра́ю —"
    assert spring.stresses[2] == (1, 4, 5, 8)
    assert spring.p_deviations == pytest.approx(1 / 12)


def test_no_meter(stress_dict):
    choir = VerseStats(CHOIR, stress_dict)
    assert choir.meter is None
    assert choir.n_feet is None
    assert choir.c_feet == {}
    assert isnan(choir.p_deviations)
    assert isnan(choir.p_pyrrhics)
    assert choir.stress_profile == ()
    assert choir.accentuate().split("\n")[0] == "Де́вушка пе́ла в церко́вном хо́ре"
    assert choir.rhyme_schemes == ("ABAB",)
    prose = VerseStats(PROSE, stress_dict)
    assert prose.meter is None
    assert prose.n_lines == 1
    assert prose.rhyme_schemes == ("-",)
    assert prose.p_rhymed == 0.0
    # Без многосложных слов со словарным ударением метр не подбирается
    short = VerseStats("Ночь. Дом. Хмурота.\nИ не", stress_dict)
    assert short.meter is None
    assert short.stresses == ((0, 1), ())
    assert short.c_clausulas == {}
    assert isnan(short.p_masculine)
    assert short.accentuate() == "Но́чь. До́м. Хмурота.\nИ не"


def test_weak_words(stress_dict):
    text = "Я помню чудное мгновенье:\nПередо мной явилась ты,"
    vs = VerseStats(text, stress_dict)
    assert vs.meter == "ямб"
    assert vs.patterns == ("cCcCcccCc", "cccCcCcC")
    assert vs.accentuate().split("\n")[1] == "Передо мно́й яви́лась ты́,"


def test_resolve_by_rhyme(stress_dict):
    text = """Мой дядя самых честных правил,
Когда не в шутку шкурою,
Он уважать себя заставил
И лучше самых хмуроты."""
    vs = VerseStats(text, stress_dict)
    assert vs.meter == "ямб"
    assert vs.stresses[3] == (1, 3, 5)
    assert vs.rhyme_schemes == ("ABAB",)
    assert vs.accentuate().split("\n")[3] == "И лу́чше са́мых хму́роты."
    # Слово вне словаря с единственным иктом получает его
    single = VerseStats(f"{ONEGIN}\nКогда не в шутку и хмурота", stress_dict)
    assert single.accentuate().split("\n")[4] == "Когда́ не в шу́тку и хмуро́та"


def test_candidates_only_for_last_word(stress_dict):
    # Кандидаты слова вне словаря в середине строки не переходят на последнее слово
    text = """Мой дядя самых честных правил,
Когда не в шутку он был мил,
Он зюзюкали и заставил
И лучше выдумать не мог."""
    vs = VerseStats(text, stress_dict)
    assert vs.stresses[2] == (3, 7)
    assert vs.accentuate().split("\n")[2] == "Он зюзюка́ли и заста́вил"
    # После сброса метра кандидаты отброшенного метра не используются
    text = f"{CHOIR.rsplit(' ', 1)[0]} бармаглою."
    vs = VerseStats(text, stress_dict)
    assert vs.meter is None
    assert vs.stresses[3] == (1, 3, 5)
    assert vs.accentuate().split("\n")[3].endswith("ра́дость бармаглою.")


def test_yo_and_anacrusis_not_moved(stress_dict):
    vs = VerseStats(f"{ONEGIN}\nЁлка стоит в моём окне", stress_dict)
    assert vs.accentuate().split("\n")[4] == "Ё́лка стои́т в моё́м окне́"
    assert vs.p_deviations == 0.0
    vs = VerseStats(f"{FROST}\nПлывут, и чёрные ручьи", stress_dict)
    assert vs.accentuate().split("\n")[4] == "Плыву́т, и чё́рные ручьи́"
    assert vs.p_deviations == pytest.approx(1 / 13)
    # Двусложное слово в анакрузе тоже остается на месте
    vs = VerseStats(f"{ONEGIN}\nВоды не в шутку занемог", stress_dict)
    assert vs.accentuate().split("\n")[4] == "Во́ды не в шу́тку занемо́г"


def test_too_many_moves(stress_dict):
    # Два слова на слабых позициях переносятся на икты, если все такие слова двусложные
    line = "Когда реки воды текут"
    vs = VerseStats(f"{ONEGIN}\n{line}", stress_dict)
    assert vs.meter == "ямб"
    assert vs.p_deviations == 0.0
    assert vs.accentuate().split("\n")[4] == "Когда́ реки́ воды́ теку́т"
    # Три переноса на восемнадцать словарных ударений - еще подгонка подвижных форм
    vs = VerseStats(f"{ONEGIN}\n{line}\nКогда воды не в шутку мог", stress_dict)
    assert vs.meter == "ямб"
    assert vs.accentuate().split("\n")[5] == "Когда́ воды́ не в шу́тку мо́г"
    # Четыре переноса на восемнадцать - больше VERSE_MAX_MOVED, метр не подобран,
    # ударения остаются словарными
    vs = VerseStats(f"{ONEGIN}\n{line}\n{line}", stress_dict)
    assert vs.meter is None
    assert vs.accentuate().split("\n")[4] == "Когда́ ре́ки во́ды текут"
    # Та же доля переносов на длинном тексте - метр подобран
    vs = VerseStats(f"{ONEGIN}\n{ONEGIN}\n{ONEGIN}\n{line}\n{line}", stress_dict)
    assert vs.meter == "ямб"


def test_hard_g_adverbs():
    assert _rhymes(_ending_key("много", 0), _ending_key("бога", 0))
    assert not _rhymes(_ending_key("много", 0), _ending_key("снова", 0))
    assert _rhymes(_ending_key("злого", 0), _ending_key("снова", 0))
    assert _rhymes(_ending_key("немного", 1), _ending_key("порога", 1))


def test_group_labels():
    assert "".join(_group_labels([0, 1, 0, 1, 2, 3, 2, 3, None, 4, None, 4])) == "ABABCDCD-E-E"
    labels = _group_labels([number // 2 for number in range(120)])
    assert "".join(labels[:8]) == "AABBCCDD"
    assert "".join(labels[50:56]) == "ZZaabb"
    assert "".join(labels[102:112]) == "zzAABBCCAA"
    assert len(set(labels)) == 52


def test_stanzas(stress_dict):
    text = f"{ONEGIN}\n\n* * *\n\n{STORM}\n"
    vs = VerseStats(text, stress_dict)
    assert vs.n_stanzas == 2
    assert vs.n_lines == 8
    assert len(vs.stanzas[0]) == 4
    assert vs.rhyme_schemes == ("ABAB", "ABAB")
    assert vs.meter is None
    assert vs.accentuate().split("\n")[4] == ""
    assert vs.accentuate().count("\n") == 8
    assert split_stanzas(text) == [ONEGIN.split("\n"), STORM.split("\n")]
    assert split_stanzas("  \n\n") == []


def test_doc(stress_dict, nlp):
    vs = VerseStats(nlp(STORM), stress_dict)
    assert vs.meter == "хорей"
    assert vs.lines == tuple(STORM.split("\n"))


def test_errors(stress_dict):
    with pytest.raises(SourceTypeError):
        VerseStats(1, stress_dict)  # type: ignore[arg-type]
    with pytest.raises(SourceError):
        VerseStats("", stress_dict)
    with pytest.raises(SourceError):
        VerseStats("123\n* * *\nabc", stress_dict)


def test_print_stats(stress_dict, capsys):
    VerseStats(ONEGIN, stress_dict).print_stats()
    captured = capsys.readouterr().out
    assert "Метр" in captured
    assert "ямб" in captured
    assert "0.19" in captured
    VerseStats(PROSE, stress_dict).print_stats()
    assert "None" in capsys.readouterr().out


def test_functions(stress_dict):
    assert accentuate("Ёжик и корова", stress_dict) == "Ё́жик и коро́ва"
    assert accentuate("Собака, замок, кто-нибудь!", stress_dict) == "Собака, замо́к, кто́-нибудь!"
    assert detect_meter(ONEGIN, stress_dict) == "ямб"
    assert detect_meter(PROSE, stress_dict) is None
    assert rhyme_scheme(ONEGIN, stress_dict) == "ABAB"
    assert rhyme_scheme(f"{ONEGIN}\n\n{STORM}", stress_dict) == "ABAB ABAB"


def test_ending_key():
    assert _ending_key("правил", 0) == ("а", "ф", 1)
    assert _ending_key("занемог", 2) == ("о", "к", 0)
    assert _ending_key("странники", 0) == ("а", "н", 2)
    assert _ending_key("моя", 1) == ("а", "", 0)
    assert _ending_key("рая", 0) == ("а", "й", 1)
    assert _ending_key("всего", 1) == ("о", "", 0)
    assert _ending_key("нового", 0) == ("о", "ф", 2)
    assert _ending_key("много", 0) == ("о", "к", 1)
    assert _ending_key("злого", 0) == ("о", "ф", 1)
    assert _ending_key("смеётся", 1) == ("о", "ц", 1)
    assert _ending_key("смеется", 1) == ("е", "ц", 1)
    assert _ending_key("местность", 0) == ("е", "сн", 1)
    assert _ending_key("вновь", 0) == ("о", "ф", 0)
    assert _ending_key("русский", 0) == ("у", "ск", 1)
    assert _ending_key("слов", 0) == ("о", "ф", 0)
    assert _ending_key("слово", 2) is None
    assert _ending_key("слово", -1) is None
    assert _rhymes(("о", "к", 0), ("о", "к", 0))
    assert _rhymes(("е", "т", 0), ("о", "т", 0))
    assert _rhymes(("е", "т", 0), ("э", "т", 0))
    assert not _rhymes(("о", "т", 0), ("э", "т", 0))
    assert not _rhymes(("а", "в", 1), ("а", "в", 2))
    assert not _rhymes(("а", "в", 1), ("а", "н", 1))
    assert not _rhymes(None, ("а", "в", 1))
