from collections import Counter
from collections.abc import Mapping, Sequence
from math import log2
from typing import NamedTuple

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon, pdist, squareform
from spacy.tokens import Doc

from ..constants import DELTA_VARIANTS, FUNCTION_UD_POS
from ..morph_stats import tag_to_ud_pos
from ..utils import is_punctuation, iter_doc_units, parse_word

ZERO_SEGMENTS = 0.5


class ZetaScore(NamedTuple):
    """
    Оценка Zeta слова - разность долей сегментов двух корпусов с этим словом

    Атрибуты:
        word (str): Слово
        dp_target (float): Доля сегментов целевого корпуса со словом
        dp_comparison (float): Доля сегментов корпуса сравнения со словом
        zeta (float): Zeta - разность долей, от −1 до 1
        log_zeta (float): Логарифмическая Zeta - двоичный логарифм отношения долей
    """

    word: str
    dp_target: float
    dp_comparison: float
    zeta: float
    log_zeta: float


def frequency_table(
    corpus: Mapping[str, Sequence[str]], n_mfw: int | None = 100, culling: float = 0.0
) -> pd.DataFrame:
    """
    Таблица относительных частот самых частых единиц корпуса

    Описание:
        Строки - тексты, столбцы - единицы (слова или символьные N-граммы)
        по убыванию средней относительной частоты по текстам, при равенстве -
        по алфавиту; значение - частота единицы в тексте, деленная на его длину.
        Отсев (culling) оставляет единицы, встречающиеся хотя бы в заданной доле
        текстов, как в stylo; n_mfw - число самых частых единиц. Средние
        и доли текстов считаются по счетчикам текстов, таблица собирается только
        для отобранных единиц: память растет как тексты × n_mfw, а не тексты × словарь

    Аргументы:
        corpus (dict[str, list[str]]): Единицы текстов по именам текстов
        n_mfw (int): Число самых частых единиц; None - все
        culling (float): Наименьшая доля текстов, в которых встречается единица

    Вывод:
        DataFrame: Таблица относительных частот

    Исключения:
        ValueError: Если корпус пуст, в нем есть пустой текст или после отсева
            не осталось единиц
    """
    if not corpus:
        raise ValueError("В корпусе нет текстов")
    if any(len(units) == 0 for units in corpus.values()):
        raise ValueError("В корпусе есть текст без единиц")
    if not 0 <= culling <= 1:
        raise ValueError("Доля текстов для отсева должна быть в пределах от 0 до 1")
    rows = {
        name: {unit: count / len(units) for unit, count in Counter(units).items()}
        for name, units in corpus.items()
    }
    means: Counter[str] = Counter()
    documents: Counter[str] = Counter()
    for row in rows.values():
        means.update(row)
        documents.update(row.keys())
    n_texts = len(rows)
    selected = sorted(
        (unit for unit in means if documents[unit] / n_texts >= culling),
        key=lambda unit: (-means[unit] / n_texts, unit),
    )
    if n_mfw:
        selected = selected[:n_mfw]
    if not selected:
        raise ValueError("После отсева не осталось единиц")
    columns = {unit: [row.get(unit, 0.0) for row in rows.values()] for unit in selected}
    return pd.DataFrame(columns, index=list(rows))


def z_scores(table: pd.DataFrame) -> pd.DataFrame:
    """
    Стандартизация таблицы частот по столбцам

    Описание:
        z = (x − mean) / sd с выборочным стандартным отклонением, как scale() в R
        и stylo; столбец с одинаковыми частотами во всех текстах дает нули

    Аргументы:
        table (DataFrame): Таблица относительных частот

    Вывод:
        DataFrame: Таблица z-оценок
    """
    std = table.std(axis=0, ddof=1)
    scaled = (table - table.mean(axis=0)) / std.where(std > 0, 1.0)
    scaled.loc[:, std <= 0] = 0.0
    return scaled


def delta(
    corpus: Mapping[str, Sequence[str]],
    n_mfw: int | None = 100,
    variant: str = "burrows",
    culling: float = 0.0,
) -> pd.DataFrame:
    """
    Вычисление расстояний между текстами по дельте Барроуза и ее вариантам

    Описание:
        Тексты описываются z-оценками относительных частот n самых частых единиц
        корпуса (frequency_table, z_scores), расстояния считаются как в stylo:
        burrows - манхэттенское расстояние между z-оценками, деленное на n
        (Burrows 2002); quadratic - евклидово, деленное на n (Argamon 2008,
        dist.argamon); eder - манхэттенское с весами (n − rank + 2) / n по рангу
        единицы (dist.eder); cosine - косинусное 1 − cos (Smith и Aldridge 2011,
        Evert и др. 2015, dist.wurzburg)
        Единицами могут быть словоформы в нижнем регистре (обычный выбор
        для дельты) или символьные N-граммы (CharNgramsExtractor)

    Ссылки:
        https://aclanthology.org/W15-0709.pdf
        https://github.com/computationalstylistics/stylo

    Аргументы:
        corpus (dict[str, list[str]]): Единицы текстов по именам текстов
        n_mfw (int): Число самых частых единиц; None - все
        variant (str): Вариант дельты из DELTA_VARIANTS
        culling (float): Наименьшая доля текстов, в которых встречается единица

    Вывод:
        DataFrame: Симметричная матрица расстояний с именами текстов

    Исключения:
        ValueError: Если вариант неизвестен или текстов меньше двух
    """
    if variant not in DELTA_VARIANTS:
        raise ValueError(f"Неизвестный вариант дельты: {variant}")
    if len(corpus) < 2:
        raise ValueError("Для расстояний нужно не меньше двух текстов")
    scores = z_scores(frequency_table(corpus, n_mfw, culling))
    n_units = scores.shape[1]
    values = scores.to_numpy()
    if variant == "burrows":
        distances = pdist(values, "cityblock") / n_units
    elif variant == "quadratic":
        distances = pdist(values, "euclidean") / n_units
    elif variant == "eder":
        weights = (n_units - np.arange(1, n_units + 1) + 2) / n_units
        distances = pdist(values * weights, "cityblock")
    else:
        distances = pdist(values, "cosine")
    return pd.DataFrame(squareform(distances), index=scores.index, columns=scores.index)


def zeta(
    target: Sequence[str] | Sequence[Sequence[str]],
    comparison: Sequence[str] | Sequence[Sequence[str]],
    segment_size: int = 2000,
    top_n: int | None = None,
) -> list[ZetaScore]:
    """
    Вычисление Zeta - маркеров предпочитаемых и избегаемых слов

    Описание:
        Каждый текст обоих корпусов делится на сегменты примерно по segment_size
        слов (число сегментов - округленное отношение длины к размеру, не меньше
        одного), для слова считается доля сегментов каждого корпуса, где оно
        встречается (DP). Zeta = DP_target − DP_comparison от −1 до 1 (Burrows
        2007, Craig и Kinney 2009 в записи stylo; классическая Zeta Крейга
        DP_target + (1 − DP_comparison) больше на единицу), логарифмическая
        Zeta = log2(DP_target / DP_comparison) (Schöch и др. 2018), нулевая доля
        заменяется на половину сегмента. В начале списка слова, предпочитаемые
        целевым корпусом, в конце - избегаемые

    Ссылки:
        https://dh2010.cch.kcl.ac.uk/academic-programme/abstracts/papers/html/ab-659.html
        https://github.com/computationalstylistics/stylo

    Аргументы:
        target (list[str]|list[list[str]]): Слова целевого корпуса - один текст
            или список текстов
        comparison (list[str]|list[list[str]]): Слова корпуса сравнения
        segment_size (int): Размер сегмента в словах
        top_n (int): Количество слов с начала списка; None - все

    Вывод:
        list[ZetaScore]: Слова по убыванию Zeta, при равенстве - по убыванию
            логарифмической Zeta и по алфавиту

    Исключения:
        ValueError: Если размер сегмента меньше единицы или один из корпусов пуст
    """
    if segment_size < 1:
        raise ValueError("Размер сегмента должен быть больше 0")
    presence_target, n_target = _segment_presence(target, segment_size)
    presence_comparison, n_comparison = _segment_presence(comparison, segment_size)
    if not n_target or not n_comparison:
        raise ValueError("В источнике данных отсутствуют слова")
    scores = []
    for word in set(presence_target) | set(presence_comparison):
        dp_target = presence_target.get(word, 0) / n_target
        dp_comparison = presence_comparison.get(word, 0) / n_comparison
        log_zeta = log2(
            (dp_target or ZERO_SEGMENTS / n_target)
            / (dp_comparison or ZERO_SEGMENTS / n_comparison)
        )
        scores.append(
            ZetaScore(word, dp_target, dp_comparison, dp_target - dp_comparison, log_zeta)
        )
    scores.sort(key=lambda score: (-score.zeta, -score.log_zeta, score.word))
    return scores[:top_n] if top_n else scores


def _segment_presence(
    texts: Sequence[str] | Sequence[Sequence[str]], segment_size: int
) -> tuple[Counter[str], int]:
    if texts and all(isinstance(text, str) for text in texts):
        texts = [texts]  # type: ignore[list-item]
    presence: Counter[str] = Counter()
    n_segments = 0
    for text in texts:
        if not text:
            continue
        for segment in np.array_split(
            np.asarray(text, dtype=object), max(1, round(len(text) / segment_size))
        ):
            presence.update(set(segment.tolist()))
            n_segments += 1
    return presence, n_segments


def kilgarriff_chi2(words_a: Sequence[str], words_b: Sequence[str], n_mfw: int = 500) -> float:
    """
    Вычисление расстояния хи-квадрат Килгарриффа между двумя корпусами

    Описание:
        По n самым частым словам объединенного корпуса (Kilgarriff 2001):
        для каждого слова ожидаемые частоты в корпусах пропорциональны их объемам,
        χ² = Σ (O − E)² / E по словам и обоим корпусам. Величина растет с объемом
        корпусов, поэтому пары корпусов сравнимы между собой при равных объемах

    Ссылки:
        https://www.sketchengine.eu/wp-content/uploads/comparing_corpora_2001.pdf

    Аргументы:
        words_a (list[str]): Слова первого корпуса
        words_b (list[str]): Слова второго корпуса
        n_mfw (int): Число самых частых слов объединенного корпуса

    Вывод:
        float: Значение хи-квадрат

    Исключения:
        ValueError: Если один из корпусов пуст
    """
    counts_a = Counter(words_a)
    counts_b = Counter(words_b)
    size_a = sum(counts_a.values())
    size_b = sum(counts_b.values())
    if not size_a or not size_b:
        raise ValueError("В источнике данных отсутствуют слова")
    joint = counts_a + counts_b
    words = sorted(joint, key=lambda word: (-joint[word], word))[:n_mfw]
    total = size_a + size_b
    chi2 = 0.0
    for word in words:
        expected_a = size_a * joint[word] / total
        expected_b = size_b * joint[word] / total
        chi2 += (counts_a[word] - expected_a) ** 2 / expected_a
        chi2 += (counts_b[word] - expected_b) ** 2 / expected_b
    return chi2


def mendenhall_curve(words: Sequence[str]) -> dict[int, float]:
    """
    Вычисление кривой Менденхолла - распределения слов по длине

    Описание:
        Доля слов каждой длины в символах (Mendenhall 1887); профиль автора,
        сравнимый между текстами независимо от их объема

    Аргументы:
        words (list[str]): Слова текста

    Вывод:
        dict[int, float]: Доли слов по длине, по возрастанию длины

    Исключения:
        ValueError: Если слов нет
    """
    if not words:
        raise ValueError("В источнике данных отсутствуют слова")
    counts = Counter(len(word) for word in words)
    return {length: counts[length] / len(words) for length in sorted(counts)}


def mendenhall_distance(words_a: Sequence[str], words_b: Sequence[str]) -> float:
    """
    Вычисление расстояния между кривыми Менденхолла двух текстов

    Описание:
        Расстояние Йенсена-Шеннона с основанием 2 между распределениями слов
        по длине - от 0 (распределения совпадают) до 1

    Аргументы:
        words_a (list[str]): Слова первого текста
        words_b (list[str]): Слова второго текста

    Вывод:
        float: Расстояние Йенсена-Шеннона
    """
    curve_a = mendenhall_curve(words_a)
    curve_b = mendenhall_curve(words_b)
    lengths = sorted(set(curve_a) | set(curve_b))
    return float(
        jensenshannon(
            [curve_a.get(length, 0.0) for length in lengths],
            [curve_b.get(length, 0.0) for length in lengths],
            base=2,
        )
    )


def function_words_profile(source: Sequence[str] | Doc) -> dict[str, float]:
    """
    Вычисление профиля служебных слов - долей служебных частей речи

    Описание:
        Доли предлогов, сочинительных и подчинительных союзов, частиц, местоимений,
        детерминативов и междометий (FUNCTION_UD_POS) среди слов текста; по первому
        разбору pymorphy3 для списка слов и по разметке для Doc с частями речи,
        знаки препинания в обоих случаях не считаются словами.
        Служебные слова не зависят от темы текста, поэтому их профиль -
        классический признак авторства

    Аргументы:
        source (list[str]|Doc): Слова текста или объект Doc

    Вывод:
        dict[str, float]: Доли по частям речи из FUNCTION_UD_POS

    Исключения:
        ValueError: Если слов нет
    """
    if isinstance(source, Doc):
        units = list(iter_doc_units(source))
        tagged = source.has_annotation("POS")
        tags = [
            unit[0].pos_ if tagged and len(unit) == 1 else _word_pos("".join(t.text for t in unit))
            for unit in units
        ]
    else:
        tags = [_word_pos(word) for word in source if not is_punctuation(word)]
    if not tags:
        raise ValueError("В источнике данных отсутствуют слова")
    counts = Counter(tags)
    return {pos: counts[pos] / len(tags) for pos in FUNCTION_UD_POS}


def _word_pos(word: str) -> str | None:
    parse = parse_word(word)
    return tag_to_ud_pos(parse.tag, parse.normal_form, word)
