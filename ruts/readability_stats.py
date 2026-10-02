from collections.abc import Mapping
from math import nan

import anyts.readability_stats
from anyts.readability_stats import (
    calc_consensus_grade as calc_consensus_grade,
    calc_gunning_fog_index as calc_gunning_fog_index,
    calc_lix as calc_lix,
    calc_rix as calc_rix,
    flesch_reading_easy_to_grade as flesch_reading_easy_to_grade,
)
from anyts.utils import safe_divide
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .constants import (
    GRADE_AGE_LEVELS,
    POSTGRADUATE_LEVEL,
    READABILITY_GRADE_STATS,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
    READING_SPEED_NORMS,
    READING_SPEED_WPM,
    SIS_GRADE_FREQ_STAGES,
    SIS_GRADE_STAGES,
    SMOG_COMPLEX_SYL_FACTOR,
)
from .exceptions import ParameterError
from .extractors import SentsExtractor, WordsExtractor

# Ядро возвращает времена в порядке скоростей нормы, а ruTS - при верхней и нижней ее границе
_NORMS_FROM_MAX = {norm: speeds[::-1] for norm, speeds in READING_SPEED_NORMS.items()}


def check_preset(preset: str) -> None:
    """
    Проверка названия пресета коэффициентов

    Аргументы:
        preset (str): Название пресета

    Исключения:
        ParameterError: Если пресет не строка или неизвестен
    """
    if not isinstance(preset, str) or preset not in READABILITY_PRESETS:
        raise ParameterError(
            f"Неизвестный пресет коэффициентов: {preset!r}. "
            f"Доступные пресеты: {tuple(READABILITY_PRESETS)}"
        )


class ReadabilityStats(anyts.readability_stats.ReadabilityStats):
    """
    Класс для вычисления основных метрик удобочитаемости текста

    Описание:
        Коэффициенты формул, адаптированных для русского языка, задаются пресетом:
            plainrussian - проект Plain Russian Language (Бегтин), 68 текстов с метками класса
            fiction - Оборнева (2005/2006), около 6 млн слов художественных текстов
            academic - Соловьёв, Иванов, Солнышкина (2018), учебники 5-11 классов
        Пресет задает коэффициенты теста Флеша-Кинкайда и индекса Флеша, коэффициенты
        индексов Колман-Лиау, SMOG и ARI во всех пресетах взяты из plainrussian
        Интерпретирующий слой: сводный класс по медиане формул класса, соответствие
        класса возрасту по таблице plainrussian и время чтения

    Пример использования:
        >>> from ruts import ReadabilityStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> rs = ReadabilityStats(text)
        >>> rs.get_stats()
        {'flesch_kincaid_grade': -2.0633333333333326,
        'flesch_reading_easy': 87.16833333333334,
        'coleman_liau_index': 1.1700000000000053,
        'smog_index': 0.05,
        'automated_readability_index': 0.2941666666666656,
        'lix': 28.333333333333336,
        'rix': 2.0,
        'sis_grade': 1.5166666666666675,
        'matskovsky_index': 9.351,
        'dale_chall_index': 4.095000000000001,
        'gunning_fog_index': 6.0,
        'consensus_grade': 1.5,
        'reading_time': 0.08333333333333333}
        >>> rs.describe_grade()
        '1-3-й класс (6-8 лет)'

    Аргументы:
        source (str|Doc|BasicStats): Источник данных - строка, объект Doc или готовый
            объект BasicStats, чтобы не считать базовые статистики повторно
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        preset (str): Пресет коэффициентов (plainrussian, fiction, academic)

    Атрибуты:
        bs (BasicStats): Объект основных статистик текста
        preset (str): Название пресета коэффициентов
        coefficients (dict[str, tuple[float, float, float]]): Коэффициенты формул пресета,
            копия справочника READABILITY_PRESETS, которую можно менять для отдельного объекта;
            формула, которой в нем нет, считается с английскими коэффициентами ядра anyTS
        flesch_kincaid_grade (float): Тест Флеша-Кинкайда
        flesch_reading_easy (float): Индекс удобочитаемости Флеша
        coleman_liau_index (float): Индекс Колман-Лиау
        smog_index (float): Индекс SMOG
        automated_readability_index (float): Автоматический индекс удобочитаемости
        lix (float): Индекс удобочитаемости LIX
        rix (float): Индекс удобочитаемости RIX
        sis_grade (float): Формула Соловьёва, Иванова, Солнышкиной (2023)
        matskovsky_index (float): Формула Мацковского
        dale_chall_index (float): Индекс Дейла-Чейла в адаптации plainrussian
        gunning_fog_index (float): Индекс Ганнинга в адаптации plainrussian
        consensus_grade (float): Сводный класс по всем формулам класса и индексу Флеша
        reading_time (float): Время чтения в минутах при скорости 180 слов в минуту
        mu_index (float): Индекс µ ядра anyTS для испанского языка, вне get_stats

    Методы:
        sis_grade_by_stage: Формула Соловьёва, Иванова, Солнышкиной (2023) для ступени обучения
        sis_grade_by_freq: Формула Соловьёва, Иванова, Солнышкиной (2023) с частотностью слов
        describe_grade: Класс школы и возраст читателя для сводного класса или отдельной формулы
        reading_time_by_speed: Время чтения при заданной скорости
        reading_time_by_norm: Время чтения в границах нормы из справочника READING_SPEED_NORMS
        get_stats: Получение вычисленных метрик удобочитаемости текста
        print_stats: Отображение вычисленных метрик удобочитаемости текста с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка, не объект Doc и не BasicStats ruTS
            или экстрактор другого типа
        SourceError: Если в источнике данных отсутствуют слова или предложения
        ParameterError: Если пресет коэффициентов не строка или неизвестен
    """

    basic_stats_class = BasicStats
    presets = READABILITY_PRESETS
    grade_stats = READABILITY_GRADE_STATS
    stats_desc = READABILITY_STATS_DESC
    stats_headers = ("Метрика", "Значение")
    smog_complex_syl_factor = SMOG_COMPLEX_SYL_FACTOR
    grade_age_levels = GRADE_AGE_LEVELS
    postgraduate_level = POSTGRADUATE_LEVEL
    reading_speed = READING_SPEED_WPM
    reading_speed_norms = _NORMS_FROM_MAX

    def __init__(
        self,
        source: str | Doc | BasicStats,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        preset: str = "plainrussian",
    ):
        super().__init__(source, sents_extractor, words_extractor, preset)

    @property
    def sis_grade(self) -> float:
        return calc_sis_grade(self._n_word_letters, self.bs.n_words, self.bs.n_sents)

    @property
    def matskovsky_index(self) -> float:
        return calc_matskovsky_index(
            self.bs.count_words_by_syllables(4), self.bs.n_words, self.bs.n_sents
        )

    @property
    def dale_chall_index(self) -> float:
        return calc_dale_chall_index(
            self.bs.count_words_by_syllables(self.smog_complex_syl_factor),
            self.bs.n_words,
            self.bs.n_sents,
        )

    @property
    def _n_word_letters(self) -> int:
        """Количество букв в учтенных словах, а не во всем тексте"""
        return sum(n_letters * count for n_letters, count in self.bs.c_letters.items())

    def sis_grade_by_stage(self, stage: str) -> float:
        """
        Вычисление формулы Соловьёва, Иванова, Солнышкиной (2023) для ступени обучения

        Аргументы:
            stage (str): Ступень обучения (2-4, 5-7, 8-11)

        Вывод:
            float: Значение формулы

        Исключения:
            ParameterError: Если указана неизвестная ступень обучения
        """
        _check_stage(stage, SIS_GRADE_STAGES)
        return calc_sis_grade(
            self._n_word_letters, self.bs.n_words, self.bs.n_sents, *SIS_GRADE_STAGES[stage]
        )

    def sis_grade_by_freq(self, mean_ipm: float, stage: str | None = None) -> float:
        """
        Вычисление формулы Соловьёва, Иванова, Солнышкиной (2023) с частотностью слов

        Аргументы:
            mean_ipm (float): Средняя частотность знаменательных слов текста по словарю
                Ляшевской и Шарова (FREQ2), например LexicalStats(text).mean_ipm_content
            stage (str): Ступень обучения (2-4, 5-7, 8-11); если не задана,
                используется общая формула

        Вывод:
            float: Значение формулы

        Исключения:
            ParameterError: Если указана неизвестная ступень обучения
        """
        if stage is None:
            return calc_sis_grade_freq(
                self._n_word_letters, self.bs.n_words, self.bs.n_sents, mean_ipm
            )
        _check_stage(stage, SIS_GRADE_FREQ_STAGES)
        return calc_sis_grade_freq(
            self._n_word_letters,
            self.bs.n_words,
            self.bs.n_sents,
            mean_ipm,
            *SIS_GRADE_FREQ_STAGES[stage],
        )


def _check_stage(stage: str, stages: Mapping[str, tuple[float, ...]]) -> None:
    """Проверка ступени обучения формулы Соловьёва, Иванова, Солнышкиной"""
    if not isinstance(stage, str) or stage not in stages:
        raise ParameterError(
            f"Неизвестная ступень обучения: {stage!r}. Доступные ступени: {tuple(stages)}"
        )


def calc_flesch_kincaid_grade(
    n_syllables: int,
    n_words: int,
    n_sents: int,
    a: float = 0.318,
    b: float = 14.2,
    c: float = 30.5,
) -> float:
    """
    Вычисление теста Флеша-Кинкайда

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Коэффициенты по умолчанию взяты из актуальной версии проекта Plain Russian Language (Бегтин)
        Альтернативные коэффициенты для русского языка:
            Оборнева (2005/2006): 0.5, 8.4, 15.59
            Соловьёв, Иванов, Солнышкина (2018, FKG_SIS): 0.36, 5.76, 11.97

    Ссылки:
        https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch–Kincaid_grade_level
        https://github.com/infoculture/plainrussian

    Аргументы:
        n_syllables (int): Количество слогов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение теста, nan без слов или предложений
    """
    return anyts.readability_stats.calc_flesch_kincaid_grade(
        n_syllables, n_words, n_sents, a, b, c
    )


def calc_flesch_reading_easy(
    n_syllables: int,
    n_words: int,
    n_sents: int,
    a: float = 1.3,
    b: float = 60.1,
    c: float = 206.835,
) -> float:
    """
    Вычисление индекса удобочитаемости Флеша

    Описание:
        Чем выше показатель, тем легче текст для чтения
        Значения индекса лежат в пределах от 0 до 100 и могут интерпретироваться следующим образом:
            100-90 - 5-й класс
            90-80 - 6-й класс
            80-70 - 7-й класс
            70-60 - 8-й и 9-й класс
            60-50 - 10-й и 11-й класс
            50-30 - Студент университета
            30-0 - Выпускник университета
        Коэффициенты по умолчанию взяты из работы Оборневой (2005/2006, вариант А)
        Вариант Б тех же работ, используемый казанской группой: 1.52, 65.14, 206.836

    Ссылки:
        https://ru.wikipedia.org/wiki/Индекс_удобочитаемости
        https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch_reading_ease

    Аргументы:
        n_syllables (int): Количество слогов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение индекса, nan без слов или предложений
    """
    return anyts.readability_stats.calc_flesch_reading_easy(n_syllables, n_words, n_sents, a, b, c)


def calc_coleman_liau_index(
    n_letters: int,
    n_words: int,
    n_sents: int,
    a: float = 0.055,
    b: float = 0.35,
    c: float = 20.33,
) -> float:
    """
    Вычисление индекса Колман-Лиау

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Коэффициенты по умолчанию взяты из проекта Plain Russian Language (Бегтин)

    Ссылки:
        https://ru.wikipedia.org/wiki/Индекс_Колман_—_Лиау
        https://en.wikipedia.org/wiki/Coleman–Liau_index

    Аргументы:
        n_letters (int): Количество букв в словах
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение индекса, nan без слов
    """
    return anyts.readability_stats.calc_coleman_liau_index(n_letters, n_words, n_sents, a, b, c)


def calc_smog_index(
    n_complex: int, n_sents: int, a: float = 1.1, b: float = 64.6, c: float = 0.05
) -> float:
    """
    Вычисление индекса SMOG

    Описание:
        Simple Measure of Gobbledygook («Простое измерение разглагольствований»)
        Наиболее авторитетная метрика читабельности
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Коэффициенты по умолчанию взяты из проекта Plain Russian Language (Бегтин) и
        получены для порога сложного слова в 5 слогов, поэтому класс ReadabilityStats
        передает количество слов с числом слогов не меньше 5

    Ссылки:
        https://en.wikipedia.org/wiki/SMOG

    Аргументы:
        n_complex (int): Количество сложных слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение индекса, nan без предложений
    """
    return anyts.readability_stats.calc_smog_index(n_complex, n_sents, a, b, c)


def calc_automated_readability_index(
    n_letters: int,
    n_words: int,
    n_sents: int,
    a: float = 6.26,
    b: float = 0.2805,
    c: float = 31.04,
) -> float:
    """
    Вычисление автоматического индекса удобочитаемости

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Значения индекса могут интерпретироваться следующим образом:
            1 - 6-7 лет
            2 - 7-8 лет
            3 - 8-9 лет
            4 - 9-10 лет
            5 - 10-11 лет
            6 - 11-12 лет
            7 - 12-13 лет
            8 - 13-14 лет
            9 - 14-15 лет
            10 - 15-16 лет
            11 - 16-17 лет
            12 - 17-18 лет
        Коэффициенты по умолчанию взяты из проекта Plain Russian Language (Бегтин)

    Ссылки:
        https://en.wikipedia.org/wiki/Automated_readability_index
        https://ru.wikipedia.org/wiki/Автоматический_индекс_удобочитаемости

    Аргументы:
        n_letters (int): Количество букв в словах
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение индекса, nan без слов или предложений
    """
    return anyts.readability_stats.calc_automated_readability_index(
        n_letters, n_words, n_sents, a, b, c
    )


def calc_sis_grade(
    n_letters: int,
    n_words: int,
    n_sents: int,
    a: float = -17.5,
    b: float = 0.56,
    c: float = 2.45,
) -> float:
    """
    Вычисление формулы Соловьёва, Иванова, Солнышкиной (2023)

    Описание:
        Формула удобочитаемости для русских академических текстов, полученная на корпусе
        из 154 учебников для 2-11 классов (Russian Academic Corpus, 5.7 млн токенов)
        Результатом является класс школы, средняя ошибка около одного класса
        В отличие от теста Флеша-Кинкайда использует среднюю длину слова в буквах, а не в слогах
        Коэффициенты по умолчанию соответствуют общей формуле, коэффициенты для отдельных
        ступеней обучения (2-4, 5-7 и 8-11 классы) заданы в справочнике SIS_GRADE_STAGES

    Ссылки:
        http://ftp.pdmi.ras.ru/pub/publicat/znsl/v529/p140.pdf
        https://link.springer.com/article/10.1007/s10958-024-07436-y

    Аргументы:
        n_letters (int): Количество букв в словах
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a (свободный член)
        b (float): Коэффициент b (при средней длине предложения в словах)
        c (float): Коэффициент c (при средней длине слова в буквах)

    Вывод:
        float: Значение формулы, nan без слов или предложений
    """
    return a + safe_divide(b * n_words, n_sents, nan) + safe_divide(c * n_letters, n_words, nan)


def calc_sis_grade_freq(
    n_letters: int,
    n_words: int,
    n_sents: int,
    mean_ipm: float,
    a: float = -14.46,
    b: float = 0.58,
    c: float = 2.15,
    d: float = -0.0026,
) -> float:
    """
    Вычисление формулы Соловьёва, Иванова, Солнышкиной (2023) с частотностью слов

    Описание:
        Вариант общей формулы с четвертым признаком FREQ2 - средней частотностью слов
        текста (ipm) по словарю Ляшевской и Шарова: чем чаще слова, тем ниже класс
        В статье значения FREQ2 лежат в пределах 200-1000, что соответствует средней
        частотности знаменательных слов (LexicalStats.mean_ipm_content): среднее
        по всем словам с учетом союзов и предлогов в разы больше
        Коэффициенты по умолчанию соответствуют общей формуле, коэффициенты для ступеней
        обучения (2-4, 5-7 и 8-11 классы) заданы в справочнике SIS_GRADE_FREQ_STAGES
        На наборе TextsByGrade формула с частотностью дает ту же корреляцию с классом,
        что и формула без нее (ρ Спирмена 0.76 против 0.77), как и в статье

    Ссылки:
        http://ftp.pdmi.ras.ru/pub/publicat/znsl/v529/p140.pdf

    Аргументы:
        n_letters (int): Количество букв в словах
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        mean_ipm (float): Средняя частотность слов (ipm)
        a (float): Коэффициент a (свободный член)
        b (float): Коэффициент b (при средней длине предложения в словах)
        c (float): Коэффициент c (при средней длине слова в буквах)
        d (float): Коэффициент d (при средней частотности)

    Вывод:
        float: Значение формулы, nan без слов или предложений
    """
    return calc_sis_grade(n_letters, n_words, n_sents, a, b, c) + d * mean_ipm


def calc_matskovsky_index(
    n_complex: int,
    n_words: int,
    n_sents: int,
    a: float = 0.62,
    b: float = 0.123,
    c: float = 0.051,
) -> float:
    """
    Вычисление формулы Мацковского

    Описание:
        Первая формула удобочитаемости для русского языка (1976, Мацковский),
        полученная методом последовательных интервалов
        Чем выше показатель, тем сложнее текст для чтения
        Сложным считается слово с числом слогов больше трех, поэтому класс ReadabilityStats
        передает количество слов с числом слогов не меньше 4

    Ссылки:
        https://dialogue-conf.org/media/4302/ivanovvv.pdf

    Аргументы:
        n_complex (int): Количество сложных слов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a (при средней длине предложения в словах)
        b (float): Коэффициент b (при доле сложных слов в процентах)
        c (float): Коэффициент c (свободный член)

    Вывод:
        float: Значение формулы, nan без слов или предложений
    """
    return (
        safe_divide(a * n_words, n_sents, nan) + safe_divide(b * 100 * n_complex, n_words, nan) + c
    )


def calc_dale_chall_index(
    n_complex: int,
    n_words: int,
    n_sents: int,
    a: float = 0.552,
    b: float = 0.273,
) -> float:
    """
    Вычисление индекса Дейла-Чейла

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Оригинальная формула использует список из 3000 знакомых слов, для русского языка
        такого свободного списка нет, поэтому применяется адаптация проекта Plain Russian
        Language (Бегтин), где вместо незнакомых слов используется доля сложных слов
        Сложным считается слово с числом слогов больше четырех, поэтому класс ReadabilityStats
        передает количество слов с числом слогов не меньше 5
        Оригинальные коэффициенты формулы: 0.1579, 0.0496

    Ссылки:
        https://en.wikipedia.org/wiki/Dale–Chall_readability_formula
        https://github.com/infoculture/plainrussian

    Аргументы:
        n_complex (int): Количество сложных слов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a (при доле сложных слов в процентах)
        b (float): Коэффициент b (при средней длине предложения в словах)

    Вывод:
        float: Значение индекса, nan без слов или предложений
    """
    return safe_divide(a * 100 * n_complex, n_words, nan) + safe_divide(b * n_words, n_sents, nan)


def grade_to_age(
    grade: float,
    levels: tuple[tuple[int, int, str, str], ...] = GRADE_AGE_LEVELS,
    above: tuple[str, str] = POSTGRADUATE_LEVEL,
) -> str:
    """
    Получение класса школы и возраста читателя по значению формулы класса

    Описание:
        Соответствие взято из таблицы GRADE_TEXT проекта Plain Russian Language:
            1-3 - 1-3-й класс, 6-8 лет
            4-6 - 4-6-й класс, 9-11 лет
            7-9 - 7-9-й класс, 12-14 лет
            10-11 - 10-11-й класс, 15-16 лет
            12-14 - 1-3-й курс вуза, 17-19 лет
            15-17 - 4-6-й курс вуза, 20-22 года
            больше 17 - аспирантура, старше 22 лет
        Значение округляется арифметически, значения меньше 1 относятся к 1-3-му классу
        Применимо к формулам, результатом которых является класс: тест Флеша-Кинкайда,
        индексы Колман-Лиау, SMOG, ARI, Дейла-Чейла и Ганнинга, формула Соловьёва,
        Иванова, Солнышкиной, сводный класс

    Ссылки:
        https://github.com/infoculture/plainrussian

    Аргументы:
        grade (float): Значение формулы класса
        levels (list[tuple[int, int, str, str]]): Ступени - первый и последний год,
            ступень и возраст - по возрастанию
        above (tuple[str, str]): Ступень и возраст после последней ступени

    Вывод:
        str: Класс школы и возраст читателя

    Исключения:
        ParameterError: Если значение не конечное число
    """
    return anyts.readability_stats.grade_to_age(grade, levels, above)


def calc_reading_time(n_words: int, wpm: float = READING_SPEED_WPM) -> float:
    """
    Вычисление времени чтения текста

    Описание:
        Норма чтения про себя для взрослого - 120-180 слов в минуту (Кузнецов и Хромов, 1991)
        Нормы чтения вслух по ФГОС для начальной школы, слов в минуту:
            1 класс - 25-40
            2 класс - 60-80
            3 класс - 80-100
            4 класс - 90-110
        Нормы доступны в справочнике READING_SPEED_NORMS

    Аргументы:
        n_words (int): Количество слов
        wpm (float): Скорость чтения, слов в минуту

    Вывод:
        float: Время чтения в минутах

    Исключения:
        ParameterError: Если скорость чтения не положительное число
    """
    return anyts.readability_stats.calc_reading_time(n_words, wpm)
