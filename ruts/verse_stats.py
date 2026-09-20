import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from math import nan
from typing import Any

from spacy.tokens import Doc

from .constants import (
    RHYME_WINDOW,
    STRESS_CORRECTIONS,
    VERSE_CLAUSULAS,
    VERSE_MAX_DEVIATIONS,
    VERSE_METERS,
    VERSE_PROCLITICS,
    VERSE_STATS_DESC,
    VERSE_WEAK_WORDS,
)
from .datasets.stress_dict import StressDict
from .exceptions import SourceError, SourceTypeError
from .phon_stats import VOWELS
from .utils import normalize_yo, safe_divide

ACUTE = "\u0301"
WORD_PATTERN = re.compile(r"[а-яё]+(?:-[а-яё]+)*", re.IGNORECASE)
# Частицы, не несущие ударения в составных словах
PARTICLES = frozenset({"то", "нибудь", "либо", "ка", "таки", "де", "с", "тка"})
# Поэтические стяжения -ие > -ье: слово ищется в словаре в полной форме
CONTRACTED_ENDINGS = (
    ("ьями", "иями"),
    ("ьем", "ием"),
    ("ьям", "иям"),
    ("ьях", "иях"),
    ("ье", "ие"),
    ("ья", "ия"),
    ("ьи", "ии"),
    ("ью", "ию"),
)
# Деепричастия ищутся в словаре как причастия с тем же ударением
CONVERB_ENDINGS = (
    ("вшись", "вшийся"),
    ("вши", "вший"),
    ("в", "вший"),
    ("аясь", "ающийся"),
    ("яясь", "яющийся"),
    ("уясь", "ующийся"),
    ("юясь", "юющийся"),
    ("ясь", "ящийся"),
    ("ась", "ащийся"),
    ("ая", "ающий"),
    ("яя", "яющий"),
    ("уя", "ующий"),
    ("юя", "юющий"),
    ("я", "ящий"),
    ("а", "ащий"),
)
# Фонетический ключ рифмы: ударные гласные и редукция безударных
STRESSED_VOWELS = {
    "а": "а", "я": "а", "о": "о", "ё": "о", "у": "у", "ю": "у", "э": "э", "е": "е", "и": "и", "ы": "и",
}  # fmt: skip
IOTATED = frozenset("еёюя")
DEVOICE = str.maketrans("бвгджз", "пфктшс")
CLUSTER_SIMPLIFICATIONS = (
    ("стн", "сн"),
    ("здн", "зн"),
    ("стл", "сл"),
    ("лнц", "нц"),
    ("рдц", "рц"),
    ("вств", "ств"),
    ("нтск", "нск"),
    ("тч", "ч"),
    ("дч", "ч"),
    ("тц", "ц"),
    ("дц", "ц"),
    ("тс", "ц"),
    ("дс", "ц"),
)
PATTERN_STRESSED = "C"
PATTERN_UNSTRESSED = "c"


@dataclass(slots=True)
class _Word:
    """Слово стихотворной строки"""

    text: str
    start: int
    end: int
    n_syllables: int
    offset: int
    stress: int | None
    fixed: bool = False
    result: int = -1

    @property
    def stressed_position(self) -> int:
        """Номер ударного слога в строке, -1 у безударного слова"""
        return self.offset + self.result if self.result >= 0 else -1


@dataclass(slots=True)
class _Line:
    """Стихотворная строка"""

    text: str
    words: list[_Word]
    n_syllables: int
    stanza: int
    key: tuple[str, str, int] | None = None
    candidates: list[int] = field(default_factory=list)


class VerseStats:
    """
    Класс для вычисления стиховедческих статистик текста

    Описание:
        Текст делится на строки и строфы (по пустым строкам), в словах расставляются
        ударения по словарю StressDict, затем по алгоритму Барахнина, Кожемякиной
        и Кузнецовой подбирается силлабо-тонический метр: у каждого из пяти метров
        свои позиции сильных слогов (иктов), выбирается тот, при котором меньше всего
        ударений многосложных слов попадает на слабые позиции. Найденный метр снимает
        оставшуюся неоднозначность: односложные слова ударны только на икте,
        служебные слова безударны вне икта, у слов без словарного ударения
        и у форм с подвижным ударением (реки́ - ре́ки) ударение ставится на икт
        внутри слова, а у последнего слова строки - еще и по рифме с соседними
        Метр не определяется (None), если после подгонки больше десятой части
        ударений многосложных слов (VERSE_MAX_DEVIATIONS) остается на слабых
        позициях - так отсеиваются дольник, акцентный стих, верлибр и проза
        Рифма ищется в окне RHYME_WINDOW строк внутри строфы по фонетическому
        ключу окончания: ударная гласная, следующие за ней согласные (после
        оглушения и упрощения групп) и число заударных слогов; опорный согласный
        открытых мужских окончаний и заударные гласные не сравниваются - так
        считаются и точные, и приблизительные рифмы. Схема рифмовки записывается
        буквами по порядку появления, нерифмованные строки - дефисом: ABAB, -A-A
        На наборе RIFMA (5121 строфа с ручной разметкой) ударения совпадают
        с разметкой у 97% слов, пары рифмующихся строк находятся с точностью 93%
        и полнотой 90%

    Ссылки:
        Барахнин В. Б., Кожемякина О. Ю., Кузнецова О. С. Определение стихотворного
        размера по расстановке ударений. CEUR Workshop Proceedings, 2019, т. 2523
        https://ceur-ws.org/Vol-2523/paper27.pdf
        https://github.com/Koziev/Rifma

    Пример использования:
        >>> from ruts import VerseStats
        >>> text = '''Мой дядя самых честных правил,
        ... Когда не в шутку занемог,
        ... Он уважать себя заставил
        ... И лучше выдумать не мог.'''
        >>> vs = VerseStats(text)
        >>> vs.meter, vs.n_feet, vs.p_deviations, vs.rhyme_schemes
        ('ямб', 4, 0.0, ('ABAB',))
        >>> vs.patterns[0], vs.c_clausulas
        ('cCcCcCcCc', {'мужская': 2, 'женская': 2})
        >>> print(vs.accentuate())
        Мой дя́дя са́мых че́стных пра́вил,
        Когда́ не в шу́тку занемо́г,
        Он уважа́ть себя́ заста́вил
        И лу́чше вы́думать не мо́г.

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Атрибуты:
        lines (tuple[str]): Строки с русскими словами
        stanzas (tuple[tuple[str, ...], ...]): Строки по строфам
        n_lines (int): Количество строк
        n_stanzas (int): Количество строф
        meter (str|None): Метр - ямб, хорей, дактиль, амфибрахий, анапест или None
        n_feet (int|None): Преобладающее число стоп в строке
        c_feet (dict[int, int]): Распределение строк по числу стоп
        p_deviations (float): Доля ударений многосложных слов на слабых позициях
            (отклонений от метра), nan без метра
        p_pyrrhics (float): Доля иктов без ударения (пиррихии в двусложных метрах)
        stress_profile (tuple[float, ...]): Доля ударных иктов по позициям в строке
        stresses (tuple[tuple[int, ...], ...]): Номера ударных слогов каждой строки
        patterns (tuple[str, ...]): Схемы строк из символов c (безударный слог) и C (ударный)
        rhyme_schemes (tuple[str, ...]): Схемы рифмовки строф
        p_rhymed (float): Доля рифмованных строк
        c_clausulas (dict[str, int]): Распределение окончаний строк по типам
        p_masculine (float): Доля мужских окончаний (ударение на последнем слоге)
        p_feminine (float): Доля женских окончаний (один заударный слог)
        p_dactylic (float): Доля дактилических окончаний (два заударных слога)
        c_stressed_vowels (dict[str, int]): Распределение ударных гласных
        mean_line_len (float): Средняя длина строки в слогах

    Методы:
        get_stats: Получение вычисленных статистик стиха
        print_stats: Отображение вычисленных статистик стиха с описанием на экран
        accentuate: Получение текста с расставленными ударениями

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют строки со словами
        DatasetNotFoundError: Если словарь ударений не загружен
    """

    def __init__(self, source: str | Doc, stress_dict: StressDict | None = None):
        if isinstance(source, Doc):
            text = source.text
        elif isinstance(source, str):
            text = source
        else:
            raise SourceTypeError("Некорректный источник данных")
        self.stress_dict = stress_dict if stress_dict is not None else StressDict()
        lines = _parse_lines(text, self.stress_dict)
        if not lines:
            raise SourceError("В источнике данных отсутствуют строки со словами")
        self._lines = lines
        self.lines = tuple(line.text for line in lines)
        n_stanzas = lines[-1].stanza + 1
        self.stanzas = tuple(
            tuple(line.text for line in lines if line.stanza == number)
            for number in range(n_stanzas)
        )
        self.n_lines = len(lines)
        self.n_stanzas = n_stanzas
        self.mean_line_len = sum(line.n_syllables for line in lines) / len(lines)

        meter = _fit_meter(lines)
        _assign_stresses(lines, meter)
        p_deviations = _deviations(lines, meter)
        if meter is not None and p_deviations > VERSE_MAX_DEVIATIONS:
            meter = None
            p_deviations = nan
            _assign_stresses(lines, meter)
        self.meter = meter
        self.p_deviations = p_deviations
        _resolve_by_rhyme(lines)
        self.stresses = tuple(
            tuple(word.stressed_position for word in line.words if word.result >= 0)
            for line in lines
        )
        self.patterns = tuple(
            "".join(
                PATTERN_STRESSED if position in stressed else PATTERN_UNSTRESSED
                for position in range(line.n_syllables)
            )
            for line, stressed in zip(lines, self.stresses, strict=True)
        )

        feet: Counter[int] = Counter()
        n_ictuses = 0
        n_pyrrhics = 0
        profile_hits: Counter[int] = Counter()
        profile_totals: Counter[int] = Counter()
        if meter is not None:
            foot_len, ictus = VERSE_METERS[meter]
            for line, stressed in zip(lines, self.stresses, strict=True):
                ictuses = range(ictus, line.n_syllables, foot_len)
                feet[len(ictuses)] += 1
                for number, position in enumerate(ictuses):
                    n_ictuses += 1
                    profile_totals[number] += 1
                    if position in stressed:
                        profile_hits[number] += 1
                    else:
                        n_pyrrhics += 1
        self.c_feet = dict(sorted(feet.items()))
        self.n_feet = feet.most_common(1)[0][0] if feet else None
        self.p_pyrrhics = safe_divide(n_pyrrhics, n_ictuses, nan)
        self.stress_profile = tuple(
            profile_hits[number] / profile_totals[number] for number in sorted(profile_totals)
        )

        clausulas: Counter[str] = Counter()
        for line, stressed in zip(lines, self.stresses, strict=True):
            # Строка без ударений и строка с неизвестным ударением последнего слова
            # не учитываются
            last = next((word for word in reversed(line.words) if word.n_syllables), None)
            if stressed and last is not None and (last.result >= 0 or last.stress is not None):
                tail = line.n_syllables - 1 - stressed[-1]
                clausulas[VERSE_CLAUSULAS[min(tail, len(VERSE_CLAUSULAS) - 1)]] += 1
        self.c_clausulas = {name: clausulas[name] for name in VERSE_CLAUSULAS if clausulas[name]}
        n_clausulas = sum(clausulas.values())
        self.p_masculine = safe_divide(clausulas[VERSE_CLAUSULAS[0]], n_clausulas, nan)
        self.p_feminine = safe_divide(clausulas[VERSE_CLAUSULAS[1]], n_clausulas, nan)
        self.p_dactylic = safe_divide(clausulas[VERSE_CLAUSULAS[2]], n_clausulas, nan)

        schemes = []
        n_rhymed = 0
        for number in range(n_stanzas):
            scheme = _rhyme_scheme([line.key for line in lines if line.stanza == number])
            schemes.append(scheme)
            n_rhymed += sum(letter != "-" for letter in scheme)
        self.rhyme_schemes = tuple(schemes)
        self.p_rhymed = n_rhymed / len(lines)

        vowels: Counter[str] = Counter()
        for line in lines:
            for word in line.words:
                if word.result >= 0:
                    vowels[_vowel(word.text, word.result)] += 1
        self.c_stressed_vowels = dict(sorted(vowels.items(), key=lambda item: -item[1]))

    def get_stats(self) -> dict[str, Any]:
        """
        Получение вычисленных статистик стиха

        Вывод:
            dict[str, object]: Справочник вычисленных статистик стиха
        """
        return {stat: getattr(self, stat) for stat in VERSE_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных статистик стиха с описанием на экран"""
        print(f"{'Статистика':^40}|{'Значение':^12}")
        print("-" * 52)
        for stat, value in self.get_stats().items():
            text = f"{value:.2f}" if isinstance(value, float) else str(value)
            print(f"{VERSE_STATS_DESC[stat]:40}|{text:^12}")

    def accentuate(self) -> str:
        """
        Получение текста с расставленными ударениями

        Описание:
            После ударной гласной каждого ударного слова ставится знак акута (U+0301);
            безударные слова (клитики, односложные вне икта) и слова без найденного
            ударения остаются без знака. Возвращаются только строки со словами
            (как в lines), строфы разделяются пустой строкой

        Вывод:
            str: Текст с ударениями
        """
        return "\n\n".join(
            "\n".join(_accentuate_line(line) for line in self._lines if line.stanza == number)
            for number in range(self.n_stanzas)
        )


def word_stress(word: str, stress_dict: StressDict | None = None) -> int | None:
    """
    Определение ударного слога слова

    Описание:
        Слоги считаются по гласным с нуля; у слов с буквой ё ударение на ней,
        у односложных слов - на единственном слоге; иначе ударение берется
        из словаря StressDict с поправками STRESS_CORRECTIONS. Составные слова
        через дефис ищутся целиком, затем по частям (частицы -то, -нибудь, -ка
        безударны, ударение последней знаменательной части считается главным);
        поэтические стяжения (желанье - желание) и деепричастия (забыв - забывший)
        ищутся в словаре по полной форме

    Аргументы:
        word (str): Слово
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        int|None: Номер ударного слога, None если слово не найдено или в нем нет гласных

    Исключения:
        DatasetNotFoundError: Если словарь ударений не загружен
    """
    if stress_dict is None:
        stress_dict = StressDict()
    return _word_stress(word.lower(), stress_dict)


def _word_stress(word: str, stress_dict: StressDict) -> int | None:
    """Ударный слог слова в нижнем регистре - см. word_stress"""
    n_syllables = _count_vowels(word)
    if not n_syllables:
        return None
    if "ё" in word:
        return _count_vowels(word[: word.index("ё")])
    if n_syllables == 1:
        return 0
    stress = _lookup(word, stress_dict)
    if stress is not None:
        return stress
    if "-" in word:
        return _compound_stress(word, stress_dict)
    for contracted, full in CONTRACTED_ENDINGS:
        if word.endswith(contracted):
            stress = _lookup(word.removesuffix(contracted) + full, stress_dict)
            if stress is not None:
                n_stem = _count_vowels(word.removesuffix(contracted))
                return stress if stress < n_stem else max(n_stem, stress - 1)
    for converb, participle in CONVERB_ENDINGS:
        if word.endswith(converb):
            stem = word.removesuffix(converb)
            stress = _lookup(stem + participle, stress_dict)
            if stress is not None and stress < _count_vowels(stem) + _count_vowels(converb):
                return stress
    return None


def _lookup(word: str, stress_dict: StressDict) -> int | None:
    """Ударный слог по поправкам и словарю"""
    key = normalize_yo(word)
    if key in STRESS_CORRECTIONS:
        return STRESS_CORRECTIONS[key]
    return stress_dict.lookup(key)


def _compound_stress(word: str, stress_dict: StressDict) -> int | None:
    """Главное ударение составного слова через дефис по последней знаменательной части"""
    stress = None
    offset = 0
    for part in word.split("-"):
        n_syllables = _count_vowels(part)
        if n_syllables and part not in PARTICLES:
            part_stress = _word_stress(part, stress_dict)
            if part_stress is None:
                return None
            stress = offset + part_stress
        offset += n_syllables
    return stress


def _count_vowels(text: str) -> int:
    """Число гласных букв - слогов"""
    return sum(letter in VOWELS for letter in text)


def _vowel(word: str, stress: int) -> str:
    """Ударная гласная слова по номеру слога"""
    vowels = [letter for letter in word if letter in VOWELS]
    return vowels[stress]


def split_stanzas(text: str) -> list[list[str]]:
    """
    Деление текста на строфы и строки

    Описание:
        Строфы разделяются пустыми строками, строки без русских слов (номера,
        звездочки) пропускаются

    Аргументы:
        text (str): Текст стихотворения

    Вывод:
        list[list[str]]: Строки по строфам
    """
    stanzas = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.strip() for line in block.split("\n") if WORD_PATTERN.search(line)]
        if lines:
            stanzas.append(lines)
    return stanzas


def _parse_lines(text: str, stress_dict: StressDict) -> list[_Line]:
    """Разбор текста на строки со словами и словарными ударениями"""
    lines = []
    for number, stanza in enumerate(split_stanzas(text)):
        for line_text in stanza:
            words = []
            offset = 0
            for match in WORD_PATTERN.finditer(line_text):
                word_text = match.group().lower()
                n_syllables = _count_vowels(word_text)
                stress = _word_stress(word_text, stress_dict)
                word = _Word(word_text, match.start(), match.end(), n_syllables, offset, stress)
                word.fixed = (
                    n_syllables > 1
                    and stress is not None
                    and word_text not in VERSE_WEAK_WORDS
                    and word_text not in VERSE_PROCLITICS
                )
                words.append(word)
                offset += n_syllables
            lines.append(_Line(line_text, words, offset, number))
    return lines


def _fit_meter(lines: Sequence[_Line]) -> str | None:
    """
    Подбор метра по словарным ударениям многосложных слов

    Описание:
        Для каждого метра считаются ударения многосложных слов на слабых позициях
        (нарушения) и на иктах; выбирается метр с наименьшим числом нарушений,
        при равенстве - с наибольшим числом ударных иктов, затем первый по порядку
        VERSE_METERS. Ударение в анакрузе - на слогах до первого икта строки -
        нарушением не считается: в трехсложных метрах оно обычно (Ста́ли дни
        холоднее). Если ударений для подбора нет, метр не определен
    """
    best: tuple[tuple[int, int], str] | None = None
    for name, (foot_len, ictus) in VERSE_METERS.items():
        violations = 0
        hits = 0
        for line in lines:
            for word in line.words:
                if not word.fixed or word.stress is None:
                    continue
                position = word.offset + word.stress
                if position % foot_len == ictus:
                    hits += 1
                elif position >= ictus:
                    violations += 1
        score = (violations, -hits)
        if best is None or score < best[0]:
            best = (score, name)
    if best is None or best[0] == (0, 0):
        return None
    return best[1]


def _conflicts(line: _Line, meter: str) -> list[_Word]:
    """Многосложные слова строки со словарным ударением на слабой позиции"""
    foot_len, ictus = VERSE_METERS[meter]
    return [
        word
        for word in line.words
        if word.fixed
        and word.stress is not None
        and (word.offset + word.stress) % foot_len != ictus
    ]


def _deviations(lines: Sequence[_Line], meter: str | None) -> float:
    """
    Доля ударений многосложных слов на слабых позициях после подгонки под метр

    Описание:
        Ударения в анакрузе не считаются; без метра - nan
    """
    if meter is None:
        return nan
    foot_len, ictus = VERSE_METERS[meter]
    total = 0
    deviations = 0
    for line in lines:
        for word in line.words:
            if word.n_syllables > 1 and word.result >= 0:
                total += 1
                position = word.stressed_position
                deviations += position >= ictus and position % foot_len != ictus
    return safe_divide(deviations, total, nan)


def _assign_stresses(lines: Sequence[_Line], meter: str | None) -> None:
    """
    Расстановка ударений в словах по метру

    Описание:
        Клитики безударны; односложные слова ударны на икте; служебные слова
        ударны, если словарное ударение попадает на икт; у остальных слов
        словарное ударение сохраняется или переносится на икт (см. _movable);
        слово без словарного ударения получает единственный икт, при нескольких
        иктах кандидаты запоминаются для снятия по рифме (по умолчанию -
        последний); без метра ставится словарное ударение
    """
    for line in lines:
        movable = _movable(line, meter)
        for word in line.words:
            candidates = _ictuses(word, meter)
            if not word.n_syllables or word.text in VERSE_PROCLITICS:
                word.result = -1
            elif word.n_syllables == 1:
                word.result = 0 if candidates or meter is None else -1
            elif word.text in VERSE_WEAK_WORDS and word.stress is not None:
                word.result = word.stress if word.stress in candidates or meter is None else -1
            elif word.stress is not None:
                word.result = candidates[0] if word in movable else word.stress
            elif len(candidates) == 1:
                word.result = candidates[0]
            elif candidates:
                word.result = candidates[-1]
                line.candidates = candidates
            else:
                word.result = -1
        _set_ending(line)


def _movable(line: _Line, meter: str | None) -> list[_Word]:
    """
    Слова строки, чье словарное ударение переносится на икт

    Описание:
        Переносятся ударения слов на слабой позиции с единственным иктом в слове,
        если такое слово в строке одно или все они двусложные (формы с подвижным
        ударением: воды́ - во́ды), и только когда после переноса в строке
        не остается нарушений - иначе строка считается неметрической и ударения
        сохраняются
    """
    if meter is None:
        return []
    conflicts = _conflicts(line, meter)
    movable = [
        word
        for word in conflicts
        if len(_ictuses(word, meter)) == 1 and (len(conflicts) == 1 or word.n_syllables == 2)
    ]
    return movable if len(movable) == len(conflicts) else []


def _ictuses(word: _Word, meter: str | None) -> list[int]:
    """Номера слогов слова, попадающих на икты метра"""
    if meter is None:
        return []
    foot_len, ictus = VERSE_METERS[meter]
    return [
        syllable
        for syllable in range(word.n_syllables)
        if (word.offset + syllable) % foot_len == ictus
    ]


def _set_ending(line: _Line) -> None:
    """Фонетический ключ окончания строки от последнего ударного слова"""
    tail: list[str] = []
    stress = None
    for word in reversed(line.words):
        if not word.n_syllables:
            continue
        tail.insert(0, word.text.replace("-", ""))
        if word.result >= 0:
            stress = word.result
            break
    line.key = _ending_key("".join(tail), stress) if stress is not None else None


def _resolve_by_rhyme(lines: Sequence[_Line]) -> None:
    """
    Снятие неоднозначности ударения последнего слова строки по рифме

    Описание:
        Если у последнего слова строки несколько кандидатов (икты в слове без
        словарного ударения), выбирается тот, при котором строка рифмуется
        с соседней в окне RHYME_WINDOW той же строфы
    """
    for number, line in enumerate(lines):
        if not line.candidates:
            continue
        last = next(word for word in reversed(line.words) if word.n_syllables)
        neighbours = [
            other.key
            for other in lines[max(0, number - RHYME_WINDOW) : number + RHYME_WINDOW + 1]
            if other is not line and other.stanza == line.stanza and not other.candidates
        ]
        for candidate in line.candidates:
            key = _ending_key(last.text.replace("-", ""), candidate)
            if any(_rhymes(key, other) for other in neighbours):
                last.result = candidate
                line.key = key
                break
        line.candidates = []


def _ending_key(tail: str, stress: int) -> tuple[str, str, int] | None:
    """
    Фонетический ключ окончания

    Описание:
        Ключ - ударная гласная (я/а, ё/о, ю/у, ы/и сведены; е сохраняется, чтобы
        рифмовать ё, записанное как е), группа согласных после нее без ь и ъ,
        с оглушением, упрощением непроизносимых сочетаний (стн - сн, тс - ц),
        стяжением двойных и заменой -ого/-его на -ово/-ево, и число заударных
        слогов; йотированная гласная сразу после ударной дает согласный й

    Аргументы:
        tail (str): Хвост строки от последнего ударного слова без дефисов
        stress (int): Номер ударного слога в хвосте

    Вывод:
        tuple[str, str, int]|None: Ключ окончания, None если слог вне хвоста
    """
    positions = [i for i, letter in enumerate(tail) if letter in VOWELS]
    if stress < 0 or stress >= len(positions):
        return None
    position = positions[stress]
    vowel = STRESSED_VOWELS[tail[position]]
    rest = tail[position + 1 :]
    if tail[position] in "ое" and rest == "го":
        rest = "во"
    elif rest.endswith(("ого", "его")):
        rest = rest[:-2] + "во"
    rest = re.sub(r"ть?ся$", "ца", rest)
    n_after = _count_vowels(rest)
    match = re.match(r"[^аеёиоуыэюя]*", rest)
    cluster = match.group().replace("ь", "").replace("ъ", "") if match else ""
    if not cluster and rest and rest[0] in IOTATED:
        cluster = "й"
    cluster = cluster.translate(DEVOICE)
    for sequence, simplified in CLUSTER_SIMPLIFICATIONS:
        cluster = cluster.replace(sequence.translate(DEVOICE), simplified.translate(DEVOICE))
    cluster = re.sub(r"(.)\1", r"\1", cluster)
    return vowel, cluster, n_after


def _rhymes(first: tuple[str, str, int] | None, second: tuple[str, str, int] | None) -> bool:
    """Проверка рифмы двух окончаний по ключам"""
    if first is None or second is None:
        return False
    vowel_1, cluster_1, n_after_1 = first
    vowel_2, cluster_2, n_after_2 = second
    if n_after_1 != n_after_2 or cluster_1 != cluster_2:
        return False
    return vowel_1 == vowel_2 or (
        "е" in (vowel_1, vowel_2) and {vowel_1, vowel_2} <= {"е", "о", "э"}
    )


def _rhyme_scheme(keys: Sequence[tuple[str, str, int] | None]) -> str:
    """
    Схема рифмовки строфы по ключам окончаний

    Описание:
        Каждая строка сравнивается с предыдущими в окне RHYME_WINDOW; рифмующиеся
        строки получают одну букву по порядку появления, нерифмованные - дефис
    """
    groups: list[int | None] = [None] * len(keys)
    n_groups = 0
    for number, key in enumerate(keys):
        for previous in range(number - 1, max(-1, number - 1 - RHYME_WINDOW), -1):
            if _rhymes(key, keys[previous]):
                if groups[previous] is None:
                    groups[previous] = n_groups
                    n_groups += 1
                groups[number] = groups[previous]
                break
    letters: dict[int, str] = {}
    scheme = []
    for group in groups:
        if group is None:
            scheme.append("-")
        else:
            letters.setdefault(group, chr(ord("A") + len(letters)))
            scheme.append(letters[group])
    return "".join(scheme)


def _accentuate_line(line: _Line) -> str:
    """Строка с акутами после ударных гласных"""
    text = line.text
    pieces = []
    position = 0
    for word in line.words:
        if word.result < 0:
            continue
        vowel = [i for i, letter in enumerate(word.text) if letter in VOWELS][word.result]
        cut = word.start + vowel + 1
        pieces.append(text[position:cut] + ACUTE)
        position = cut
    pieces.append(text[position:])
    return "".join(pieces)


def accentuate(text: str, stress_dict: StressDict | None = None) -> str:
    """
    Расстановка ударений в тексте по словарю

    Описание:
        После ударной гласной каждого слова ставится знак акута (U+0301):
        по букве ё, словарю StressDict с поправками и правилам word_stress;
        односложные предлоги, союзы и частицы (VERSE_PROCLITICS) и слова
        без найденного ударения остаются без знака. Метр не учитывается:
        для стихов с подгонкой ударений под метр служит VerseStats.accentuate

    Аргументы:
        text (str): Текст
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        str: Текст с ударениями

    Исключения:
        DatasetNotFoundError: Если словарь ударений не загружен
    """
    if stress_dict is None:
        stress_dict = StressDict()

    def mark(match: re.Match[str]) -> str:
        word = match.group()
        if word.lower() in VERSE_PROCLITICS:
            return word
        stress = _word_stress(word.lower(), stress_dict)
        if stress is None:
            return word
        vowel = [i for i, letter in enumerate(word.lower()) if letter in VOWELS][stress]
        return word[: vowel + 1] + ACUTE + word[vowel + 1 :]

    return WORD_PATTERN.sub(mark, text)


def detect_meter(text: str, stress_dict: StressDict | None = None) -> str | None:
    """
    Определение метра стихотворения

    Аргументы:
        text (str): Текст стихотворения
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        str|None: Метр - ямб, хорей, дактиль, амфибрахий, анапест; None, если
            силлабо-тонический метр не подобран
    """
    return VerseStats(text, stress_dict).meter


def rhyme_scheme(text: str, stress_dict: StressDict | None = None) -> str:
    """
    Определение схемы рифмовки стихотворения

    Аргументы:
        text (str): Текст стихотворения
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        str: Схемы строф через пробел, нерифмованные строки обозначены дефисом:
            ABAB, -A-A, AABB CC
    """
    return " ".join(VerseStats(text, stress_dict).rhyme_schemes)
