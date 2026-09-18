from collections.abc import Sequence
from functools import cache, cached_property
from math import log2, log10, nan
from statistics import fmean

from spacy.tokens import Doc

from .cohesion_stats import WordInfo, unit_info, unit_text, word_info
from .constants import FREQUENCY_BANDS, LEXICAL_STATS_DESC, RESOURCES_DIR
from .datasets.freq2011 import Entry, FreqDict
from .exceptions import SourceError, SourceTypeError
from .extractors import NUMBER_PATTERN, WordsExtractor
from .utils import iter_doc_units, normalize_yo, safe_divide

TOP_LEMMAS_FILE = RESOURCES_DIR / "sharoff_top10000.txt"


class LexicalStats:
    """
    Класс для вычисления статистик лексической сложности текста

    Описание:
        Лексическая сложность (lexical sophistication по образцу TAALES) - насколько
        слова текста редки относительно языка: средняя частотность, диапазон
        и дисперсия лемм по частотному словарю Ляшевской и Шарова (FreqDict), доля
        слов из частотных полос топ-1000, 2000, 5000 и 10000 по вшитому списку Шарова,
        сюрпризал и перплексия по униграммной модели словаря, лексическая плотность
        Леммы для Doc с разметкой частей речи берутся из разбора pymorphy3 с частью
        речи токена, для строки и Doc без разметки - из первого разбора pymorphy3;
        дефисные слова, разрезанные spaCy, склеиваются (iter_doc_units)
        Числа (2020, 5.5, 3-й) словами не считаются: в словаре и списке их нет,
        и они выглядели бы как самые редкие слова текста
        Метрики по частотному словарю требуют загруженного FreqDict, полосы
        и лексическая плотность считаются без него

    Ссылки:
        https://doi.org/10.3758/s13428-017-0924-4 (Kyle, Crossley, Berger 2018, TAALES)
        http://dict.ruslang.ru/freq.php

    Пример использования:
        >>> from ruts import LexicalStats
        >>> text = "Кот сидел на окне и смотрел на птиц"
        >>> ls = LexicalStats(text)
        >>> ls.get_stats()
        {'coverage': 1.0,
        'mean_ipm': 8645.5375,
        'mean_ipm_content': 324.18,
        'mean_log_ipm': 3.0674194359404705,
        'mean_log_ipm_content': 2.316850597556863,
        'mean_range': 99.75,
        'mean_dispersion': 95.125,
        'surprisal': 9.74182176626998,
        'perplexity': 856.2105288389297,
        'p_top1000': 0.75,
        'p_top2000': 0.875,
        'p_top5000': 1.0,
        'p_top10000': 1.0,
        'p_beyond_top10000': 0.0,
        'lexical_density': 0.625}
        >>> ls.band_coverage(unique=True)
        {1000: 0.7142857142857143, 2000: 0.8571428571428571, 5000: 1.0, 10000: 1.0}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        freq_dict (FreqDict): Частотный словарь; если не задан, используется FreqDict()
            из директории по умолчанию

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        lemmas (tuple[str]): Кортеж лемм в нижнем регистре
        n_words (int): Количество слов
        n_content_words (int): Количество знаменательных слов
        n_found (int): Количество слов, найденных в частотном словаре
        ranks (tuple[int|None]): Кортеж рангов лемм по вшитому списку, None вне топ-10000
        coverage (float): Доля слов, найденных в частотном словаре
        mean_ipm (float): Средняя частотность найденных слов
        mean_ipm_content (float): Средняя частотность знаменательных слов - FREQ2 формулы
            Соловьёва, Иванова, Солнышкиной 2023 года (в статье значения 200-1000)
        mean_log_ipm (float): Средний десятичный логарифм частотности найденных слов
        mean_log_ipm_content (float): То же по знаменательным словам
        mean_range (float): Средний диапазон R найденных слов
        mean_dispersion (float): Средняя дисперсия D найденных слов
        surprisal (float): Средний сюрпризал слов по униграммной модели словаря в битах
        perplexity (float): Униграммная перплексия - 2 в степени сюрпризала
        p_top1000 (float): Доля слов с леммой из топ-1000
        p_top2000 (float): Доля слов с леммой из топ-2000
        p_top5000 (float): Доля слов с леммой из топ-5000
        p_top10000 (float): Доля слов с леммой из топ-10000
        p_beyond_top10000 (float): Доля слов с леммой вне топ-10000
        lexical_density (float): Доля знаменательных слов

    Методы:
        band_coverage: Доли слов или лемм по частотным полосам
        get_stats: Получение вычисленных статистик лексической сложности текста
        print_stats: Отображение вычисленных статистик с описанием на экран

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют слова
        DatasetNotFoundError: При обращении к метрикам по словарю, если словарь не загружен
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        freq_dict: FreqDict | None = None,
    ):
        infos: list[WordInfo]
        if isinstance(source, Doc):
            units = [unit for unit in iter_doc_units(source) if not is_number(unit_text(unit))]
            self.words = tuple(unit_text(unit) for unit in units)
            if source.has_annotation("POS"):
                infos = [unit_info(unit) for unit in units]
            else:
                infos = [word_info(word) for word in self.words]
        elif isinstance(source, str):
            if not words_extractor:
                words_extractor = WordsExtractor()
            self.words = tuple(
                word for word in words_extractor.extract(source) if not is_number(word)
            )
            infos = [word_info(word) for word in self.words]
        else:
            raise SourceTypeError("Некорректный источник данных")
        if not self.words:
            raise SourceError("В источнике данных отсутствуют слова")
        self.freq_dict = freq_dict if freq_dict is not None else FreqDict()
        self.lemmas = tuple(info.lemma for info in infos)
        self._content = tuple(info.content for info in infos)
        self.n_words = len(self.words)
        self.n_content_words = sum(self._content)
        self.ranks = tuple(get_rank(lemma) for lemma in self.lemmas)
        self.lexical_density = self.n_content_words / self.n_words
        bands = self.band_coverage()
        self.p_top1000 = bands[1000]
        self.p_top2000 = bands[2000]
        self.p_top5000 = bands[5000]
        self.p_top10000 = bands[10000]
        self.p_beyond_top10000 = 1 - bands[10000]

    @cached_property
    def entries(self) -> tuple[Entry | None, ...]:
        """
        Статьи частотного словаря для каждого слова, None для слов вне словаря
        """
        return tuple(self.freq_dict.lookup(lemma) for lemma in self.lemmas)

    @property
    def n_found(self) -> int:
        return sum(1 for entry in self.entries if entry)

    @property
    def coverage(self) -> float:
        return self.n_found / self.n_words

    @property
    def mean_ipm(self) -> float:
        return _mean([entry.ipm for entry in self.entries if entry])

    @property
    def mean_ipm_content(self) -> float:
        return _mean(
            [
                entry.ipm
                for entry, content in zip(self.entries, self._content, strict=True)
                if entry and content
            ]
        )

    @property
    def mean_log_ipm(self) -> float:
        return _mean([log10(entry.ipm) for entry in self.entries if entry])

    @property
    def mean_log_ipm_content(self) -> float:
        return _mean(
            [
                log10(entry.ipm)
                for entry, content in zip(self.entries, self._content, strict=True)
                if entry and content
            ]
        )

    @property
    def mean_range(self) -> float:
        return _mean([entry.range for entry in self.entries if entry])

    @property
    def mean_dispersion(self) -> float:
        return _mean([entry.dispersion for entry in self.entries if entry])

    @cached_property
    def surprisal(self) -> float:
        return calc_surprisal(self.lemmas, self.freq_dict)

    @property
    def perplexity(self) -> float:
        return 2**self.surprisal

    def band_coverage(
        self, bands: Sequence[int] = FREQUENCY_BANDS, unique: bool = False
    ) -> dict[int, float]:
        """
        Доли слов по частотным полосам вшитого списка

        Аргументы:
            bands (list[int]): Границы полос - размеры топ-списков
            unique (bool): Считать по уникальным леммам, а не по словам

        Вывод:
            dict[int, float]: Доля слов с леммой из топ-N для каждой границы N
        """
        ranks = [get_rank(lemma) for lemma in set(self.lemmas)] if unique else list(self.ranks)
        return {
            band: safe_divide(sum(1 for rank in ranks if rank and rank <= band), len(ranks))
            for band in bands
        }

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных статистик лексической сложности текста

        Вывод:
            dict[str, float]: Справочник вычисленных статистик
        """
        return {stat: getattr(self, stat) for stat in LEXICAL_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных статистик лексической сложности текста с описанием на экран"""
        print(f"{'Статистика':^58}|{'Значение':^10}")
        print("-" * 68)
        stats = self.get_stats()
        for stat, value in LEXICAL_STATS_DESC.items():
            print(f"{value:58}|{stats.get(stat):^10.2f}")


def is_number(word: str) -> bool:
    """
    Проверка, является ли слово числом по шаблону NUMBER_PATTERN

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    return NUMBER_PATTERN.fullmatch(word.lower()) is not None


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else nan


@cache
def load_top_lemmas() -> dict[str, int]:
    """
    Загрузка вшитого списка самых частых лемм

    Описание:
        10 000 лемм интернет-корпуса Лидского университета (С. А. Шаров) в порядке
        убывания частоты, файл resources/sharoff_top10000.txt (CC BY 2.5); леммы
        приводятся к нижнему регистру без буквы ё, у дублей (еще, ещё) остается
        меньший ранг

    Вывод:
        dict[str, int]: Ранг каждой леммы, начиная с 1
    """
    with TOP_LEMMAS_FILE.open(encoding="utf-8") as file:
        lemmas = [normalize_yo(line.strip()) for line in file if line.strip()]
    ranks: dict[str, int] = {}
    for rank, lemma in enumerate(lemmas, 1):
        ranks.setdefault(lemma, rank)
    return ranks


def get_rank(lemma: str) -> int | None:
    """
    Получение ранга леммы по вшитому списку самых частых лемм

    Аргументы:
        lemma (str): Лемма в любом регистре, с ё или без

    Вывод:
        int|None: Ранг от 1 до 10 000, None если леммы в списке нет
    """
    return load_top_lemmas().get(normalize_yo(lemma))


def calc_surprisal(lemmas: Sequence[str], freq_dict: FreqDict) -> float:
    """
    Вычисление среднего сюрпризала слов по униграммной модели частотного словаря

    Описание:
        Среднее по словам −log2 P(w), где P(w) = ipm / 10⁶; слова вне словаря
        получают минимальную частоту словаря (0.4 ipm), поэтому сюрпризал определен
        для всех слов. Перплексия текста - 2 в степени сюрпризала

    Аргументы:
        lemmas (list[str]): Леммы слов
        freq_dict (FreqDict): Частотный словарь

    Вывод:
        float: Средний сюрпризал в битах, nan для пустого списка
    """
    floor = freq_dict.min_ipm
    return _mean([-log2(max(freq_dict.ipm(lemma), floor) / 1_000_000) for lemma in lemmas])
