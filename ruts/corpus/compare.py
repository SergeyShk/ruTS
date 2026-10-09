from collections.abc import Callable, Mapping, Sequence
from itertools import pairwise
from math import isnan, nan
from numbers import Integral

import numpy as np
import pandas as pd
from anyts.corpus.compare import (
    COMPARISON_COLUMNS as COMPARISON_COLUMNS,
    bootstrap_median_diff as bootstrap_median_diff,
    calc_cliff_delta as calc_cliff_delta,
    calc_cohen_d as calc_cohen_d,
    check_comparison_params as check_comparison_params,
    compare_features as compare_features,
    holm_correction as holm_correction,
)
from anyts.utils import check_integer, check_sequence, check_words, count_words_by_spans

from ..basic_stats import BasicStats, punctuation_profile
from ..constants import MORPHOLOGY_STATS_DESC, OPENING_MARKS, SYMMETRIC_MARKS
from ..diversity_stats import DiversityStats
from ..exceptions import ParameterError, SourceError, SourceTypeError
from ..extractors import SentsExtractor, WordsExtractor
from ..morph_stats import MorphStats
from ..readability_stats import ReadabilityStats
from ..utils import iter_text_sents, iter_text_words

Features = Callable[[str], Mapping[str, float]]

# Монотонно повторяют другие признаки (ранговое сравнение дает те же U, p и |δ|) или постоянны
REDUNDANT_FEATURES = frozenset(
    {
        "readability_reading_time",
        "diversity_gini_simpson_index",
        "diversity_inverse_simpson_index",
        "diversity_simpson_index",
        "diversity_cttr",
        "diversity_dttr",
        "diversity_perplexity",
        "diversity_michea_m",
        "morph_pos_AUX",
        "morph_pos_PUNCT",
        "morph_pos_SYM",
        "morph_mood_Cnd",
        "morph_mood_Ind",
        "morph_voice_Mid",
        "morph_voice_Act",
        "morph_number_Sing",
        "morph_aspect_Imp",
        "morph_animacy_Inan",
        "morph_transitivity_Intr",
        "morph_involvement_Ex",
    }
)


def split_windows(text: str, window: int | None = 1000, min_words: int | None = None) -> list[str]:
    """
    Разбиение текста на окна по словам

    Описание:
        Текст режется подряд на окна ровно по window слов; неполный остаток в конце
        становится окном, только если в нем не меньше min_words слов (по умолчанию
        окно целиком, то есть остаток отбрасывается), так что окна разных текстов
        одной длины и признаки, зависящие от длины, сравнимы. Граница проходит перед первым
        словом окна и открывающими знаками перед ним (кавычки, скобки, тире), так
        что пунктуация остается в окнах; при window=None окно - весь текст

    Аргументы:
        text (str): Строка текста
        window (int): Размер окна в словах; None - текст целиком
        min_words (int): Наименьшее число слов в окне; None - окно целиком,
            при window=None - одно слово

    Вывод:
        list[str]: Окна текста; пустой список для текста без слов или короче min_words

    Исключения:
        ParameterError: Если размер окна или min_words меньше единицы или min_words
            больше окна
    """
    if not isinstance(text, str):
        raise SourceTypeError(f"Ожидается строка текста, а не {type(text).__name__}")
    _check_windows(window, min_words)
    min_words = _min_words(window, min_words)
    words = list(iter_text_words(text))
    if not words:
        return []
    size = len(words) if window is None else window
    chunks = [
        np.arange(start, min(start + size, len(words))) for start in range(0, len(words), size)
    ]
    boundaries = [0]
    for chunk in chunks[1:]:
        start = words[chunk[0]][0]
        previous_end = words[chunk[0] - 1][1]
        boundary = start
        while boundary > previous_end and (
            text[boundary - 1].isspace() or text[boundary - 1] in OPENING_MARKS
        ):
            boundary -= 1
        while (
            boundary < start
            and text[boundary] in SYMMETRIC_MARKS
            and (boundary == previous_end or text[boundary - 1] in ".!?…,;)]»")
        ):
            boundary += 1
            previous_end = boundary
        boundaries.append(boundary)
    boundaries.append(len(text))
    return [
        text[start:end].strip()
        for (start, end), chunk in zip(pairwise(boundaries), chunks, strict=True)
        if len(chunk) >= min_words
    ]


def _min_words(window: int | None, min_words: int | None) -> int:
    """Наименьшее число слов в окне: заданное, окно целиком или одно слово при window=None"""
    if min_words is not None:
        return min_words
    return 1 if window is None else window


def _check_windows(window: int | None, min_words: int | None) -> None:
    """Проверка размера окна и наименьшего числа слов в нем"""
    if window is not None:
        check_integer(window, "size of a window")
        if window < 1:
            raise ParameterError("Размер окна должен быть больше 0")
    if min_words is not None:
        check_integer(min_words, "smallest number of words in a window")
        if min_words < 1:
            raise ParameterError("Наименьшее число слов в окне должно быть больше 0")
        if window is not None and min_words > window:
            raise ParameterError("Наименьшее число слов в окне не может быть больше окна")


def text_features(text: str) -> dict[str, float]:
    """
    Вычисление признаков текста для сравнения корпусов

    Описание:
        Признаки с префиксом по источнику: basic_ - доли длинных, сложных,
        простых, одно- и многосложных слов, букв, пробелов и знаков препинания,
        буквы и слоги на слово (BasicStats); readability_ - формулы удобочитаемости
        и сводный класс (ReadabilityStats); diversity_ - меры лексического
        разнообразия (DiversityStats); morph_ - доли частей речи и значений
        морфологических признаков, например morph_pos_NOUN, morph_case_Gen
        (MorphStats по pymorphy3; признак, которого нет в окне, - nan); sents_ -
        средняя длина предложения, ее разброс и автокорреляция соседних длин;
        punct_ - частоты знаков на 1000 слов и доля буквы ё. Признаки, повторяющие
        другие, отброшены (REDUNDANT_FEATURES)
        Доли пробелов, букв и знаков считаются по символам как есть, поэтому
        верстку издания (отступы, двойные пробелы) стоит выровнять заранее

    Аргументы:
        text (str): Строка текста

    Вывод:
        dict[str, float]: Признаки; неопределенные значения - nan

    Исключения:
        SourceError: Если в тексте нет слов
    """
    if not isinstance(text, str):
        raise SourceTypeError(f"Ожидается строка текста, а не {type(text).__name__}")
    positions = list(iter_text_words(text))
    spans = [(start, stop) for start, stop, sent in iter_text_sents(text) if sent.strip()]
    words = _FixedWordsExtractor(tuple(word for _, _, word in positions))
    sents = _FixedSentsExtractor(tuple(text[start:stop] for start, stop in spans))
    basic = BasicStats(text, sents, words, normalize=True)
    features: dict[str, float] = {}
    for key in (
        "p_long_words",
        "p_complex_words",
        "p_simple_words",
        "p_monosyllable_words",
        "p_polysyllable_words",
        "p_letters",
        "p_spaces",
        "p_punctuations",
    ):
        features[f"basic_{key}"] = float(getattr(basic, key))
    features["basic_letters_per_word"] = basic.n_letters / basic.n_words
    features["basic_syllables_per_word"] = basic.n_syllables / basic.n_words
    for key, score in ReadabilityStats(basic).get_stats().items():
        features[f"readability_{key}"] = float(score)
    lowered = _FixedWordsExtractor(tuple(word.lower() for word in words.words))
    for key, score in DiversityStats(text, words_extractor=lowered).get_stats().items():
        features[f"diversity_{key}"] = float(score)
    morph = MorphStats(text, words_extractor=words)
    n_words = len(morph.words)
    stats = morph.get_stats(filter_none=True)
    for category, desc in MORPHOLOGY_STATS_DESC.items():
        counts = stats.get(category, {})
        denominator = n_words if category == "pos" else sum(counts.values())
        for label in desc["values"]:
            features[f"morph_{category}_{label}"] = (
                counts.get(label, 0) / denominator if denominator else nan
            )
    features.update(
        sentence_rhythm(count_words_by_spans([start for start, _, _ in positions], spans))
    )
    features.update(
        (f"punct_{key}", float(value))
        for key, value in punctuation_profile(text, basic.n_words).items()
    )
    return {key: value for key, value in features.items() if key not in REDUNDANT_FEATURES}


class _FixedWordsExtractor(WordsExtractor):
    """Экстрактор с готовыми словами, чтобы не токенизировать текст дважды"""

    def __init__(self, words: tuple[str, ...]) -> None:
        super().__init__()
        self.words = words

    def extract(self, text: str) -> tuple[str, ...]:
        return self.words


class _FixedSentsExtractor(SentsExtractor):
    """Экстрактор с готовыми предложениями, чтобы не делить текст дважды"""

    def __init__(self, sents: tuple[str, ...]) -> None:
        super().__init__()
        self.sents = sents

    def extract(self, text: str) -> tuple[str, ...]:
        return self.sents


def sentence_rhythm(lengths: Sequence[int]) -> dict[str, float]:
    """
    Вычисление признаков ритма предложений

    Описание:
        Средняя длина предложения в словах, стандартное отклонение, коэффициент
        вариации и автокорреляция лага 1 - связь длин соседних предложений
        (Yule 1939); автокорреляция требует не меньше трех предложений

    Аргументы:
        lengths (list[int]): Длины предложений в словах

    Вывод:
        dict[str, float]: Признаки sents_mean, sents_std, sents_cv, sents_autocorr
    """
    check_sequence(lengths, "sentence lengths")
    if not all(isinstance(length, Integral) for length in lengths):
        raise SourceTypeError("Длины предложений должны быть целыми числами")
    values = np.asarray(lengths, dtype=float)
    if not len(values):
        return dict.fromkeys(("sents_mean", "sents_std", "sents_cv", "sents_autocorr"), nan)
    mean = float(values.mean())
    std = float(values.std(ddof=1)) if len(values) > 1 else nan
    centered = values - mean
    variance = float((centered**2).sum())
    autocorr = (
        float((centered[:-1] * centered[1:]).sum() / variance)
        if len(values) > 2 and variance
        else nan
    )
    return {
        "sents_mean": mean,
        "sents_std": std,
        "sents_cv": std / mean if mean and not isnan(std) else nan,
        "sents_autocorr": autocorr,
    }


def corpus_features(
    texts: Sequence[str],
    window: int | None = 1000,
    features: Features = text_features,
    min_words: int | None = None,
) -> pd.DataFrame:
    """
    Вычисление признаков окон корпуса

    Описание:
        Каждый текст режется на окна (split_windows), для каждого окна считаются
        признаки; строки - окна с индексом (номер текста, номер окна), столбцы -
        признаки. Тексты без слов и окна короче min_words пропускаются

    Аргументы:
        texts (list[str]): Тексты корпуса
        window (int): Размер окна в словах; None - тексты целиком
        features (callable): Функция признаков текста; по умолчанию text_features
        min_words (int): Наименьшее число слов в окне; None - окно целиком,
            при window=None - одно слово

    Вывод:
        DataFrame: Признаки окон

    Исключения:
        SourceError: Если в корпусе нет окна из min_words и более слов
        ParameterError: Если размер окна или min_words меньше единицы или min_words
            больше окна
    """
    check_words(texts, "texts")
    if not callable(features):
        raise SourceTypeError(f"Признаки должны быть функцией, а не {type(features).__name__}")
    _check_windows(window, min_words)
    rows = {}
    for text_index, text in enumerate(texts):
        for window_index, chunk in enumerate(split_windows(text, window, min_words)):
            rows[text_index, window_index] = dict(features(chunk))
    if not rows:
        if not any(next(iter_text_words(text), None) for text in texts):
            raise SourceError("В источнике данных отсутствуют слова")
        advice = "уменьшите window" if min_words is None else "уменьшите min_words"
        raise SourceError(
            f"В источнике данных нет окна из {_min_words(window, min_words)} и более слов: "
            f"{advice}"
        )
    table = pd.DataFrame.from_dict(rows, orient="index").astype(float)
    table.index = pd.MultiIndex.from_tuples(table.index, names=["text", "window"])
    return table


def compare_corpora(
    a: Sequence[str],
    b: Sequence[str],
    window: int | None = 1000,
    features: Features | None = None,
    labels: tuple[str, str] = ("A", "B"),
    n_bootstrap: int = 1000,
    seed: int | None = 0,
    min_words: int | None = None,
) -> pd.DataFrame:
    """
    Сравнение двух корпусов по всем признакам текста

    Описание:
        Тексты обоих корпусов режутся на окна одинакового размера, чтобы убрать
        зависимость признаков от длины, для каждого окна считаются признаки
        (text_features или своя функция), для каждого признака сравниваются
        два набора значений: средние и медианы, разность медиан с перцентильным
        бутстрэп-интервалом 95%, d Коэна, дельта Клиффа, AUC признака как одиночного
        классификатора (доля пар окон, где значение в A больше, чем в B, ничьи
        за половину; дельта Клиффа равна 2·AUC − 1), U-критерий Манна-Уитни
        с двусторонним p-значением и поправкой Холма на число признаков.
        Неопределенные и бесконечные значения признака отбрасываются, при менее
        чем двух значениях на стороне статистики признака - nan. Строки отсортированы
        по убыванию модуля дельты Клиффа, признаки без статистик - в конце
        Один инструмент для атрибуции авторства, сравнения жанров и переводов,
        отличия сгенерированных текстов от человеческих; для отдельных слов
        то же делает keyness

    Ссылки:
        https://doi.org/10.1037/0033-2909.114.3.494
        https://en.wikipedia.org/wiki/Mann–Whitney_U_test

    Аргументы:
        a (list[str]): Тексты первого корпуса
        b (list[str]): Тексты второго корпуса
        window (int): Размер окна в словах; None - тексты целиком
        features (callable): Функция признаков текста; None - text_features
        labels (tuple[str, str]): Имена корпусов для столбцов (mean_<a>, ...)
        n_bootstrap (int): Число выборок бутстрэпа
        seed (int): Зерно генератора случайных чисел; None - случайное
        min_words (int): Наименьшее число слов в окне; None - окно целиком,
            при window=None - одно слово

    Вывод:
        DataFrame: Признаки × статистики сравнения (COMPARISON_COLUMNS
            с именами корпусов в столбцах)

    Исключения:
        SourceError: Если в одном из корпусов нет окна из min_words и более слов
        ParameterError: Если размер окна или min_words меньше единицы или min_words
            больше окна
        ParameterError: Если число выборок меньше единицы
    """
    check_comparison_params(labels, n_bootstrap, seed)
    check_words(a, "texts")
    check_words(b, "texts")
    if features is not None and not callable(features):
        raise SourceTypeError(f"Признаки должны быть функцией, а не {type(features).__name__}")
    _check_windows(window, min_words)
    feature_function = text_features if features is None else features
    tables = []
    for label, corpus in zip(labels, (a, b), strict=False):
        try:
            tables.append(corpus_features(corpus, window, feature_function, min_words))
        except SourceError as error:
            raise SourceError(f"Корпус {label}: {error}") from error
    table_a, table_b = tables
    return compare_features(table_a, table_b, labels, n_bootstrap, seed)
