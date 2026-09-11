from math import sqrt

from spacy.tokens import Doc

from .basic_stats import BasicStats
from .constants import (
    LIX_LONG_WORD_LETTER_FACTOR,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
    SIS_GRADE_STAGES,
    SMOG_COMPLEX_SYL_FACTOR,
)
from .extractors import SentsExtractor, WordsExtractor


class ReadabilityStats:
    """
    Класс для вычисления основных метрик удобочитаемости текста

    Описание:
        Коэффициенты формул, адаптированных для русского языка, задаются пресетом:
            plainrussian - проект Plain Russian Language (Бегтин), 68 текстов с метками класса
            fiction - Оборнева (2005/2006), около 6 млн слов художественных текстов
            academic - Соловьёв, Иванов, Солнышкина (2018), учебники 5-11 классов
        Пресет задает коэффициенты теста Флеша-Кинкайда и индекса Флеша, коэффициенты
        индексов Колман-Лиау, SMOG и ARI во всех пресетах взяты из plainrussian

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
        'gunning_fog_index': 6.0}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        preset (str): Пресет коэффициентов (plainrussian, fiction, academic)

    Атрибуты:
        bs (BasicStats): Объект основных статистик текста
        preset (str): Название пресета коэффициентов
        coefficients (dict[str, tuple[float, float, float]]): Коэффициенты формул пресета
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

    Методы:
        sis_grade_by_stage: Формула Соловьёва, Иванова, Солнышкиной (2023) для ступени обучения
        get_stats: Получение вычисленных метрик удобочитаемости текста
        print_stats: Отображение вычисленных метрик удобочитаемости текста с описанием на экран

    Исключения:
        ValueError: Если в источнике данных отсутствуют слова
        ValueError: Если указан неизвестный пресет коэффициентов
    """

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        preset: str = "plainrussian",
    ):
        if preset not in READABILITY_PRESETS:
            raise ValueError(
                f"Неизвестный пресет коэффициентов: {preset}. "
                f"Доступные пресеты: {tuple(READABILITY_PRESETS)}"
            )
        self.preset = preset
        self.coefficients = READABILITY_PRESETS[preset]
        self.bs = BasicStats(source, sents_extractor, words_extractor)
        if not self.bs.n_words:
            raise ValueError("В источнике данных отсутствуют слова")

    @property
    def flesch_kincaid_grade(self) -> float:
        return calc_flesch_kincaid_grade(
            self.bs.n_syllables,
            self.bs.n_words,
            self.bs.n_sents,
            *self.coefficients["flesch_kincaid_grade"],
        )

    @property
    def flesch_reading_easy(self) -> float:
        return calc_flesch_reading_easy(
            self.bs.n_syllables,
            self.bs.n_words,
            self.bs.n_sents,
            *self.coefficients["flesch_reading_easy"],
        )

    @property
    def coleman_liau_index(self) -> float:
        return calc_coleman_liau_index(
            self.bs.n_letters,
            self.bs.n_words,
            self.bs.n_sents,
            *self.coefficients["coleman_liau_index"],
        )

    @property
    def smog_index(self) -> float:
        return calc_smog_index(
            self.bs.count_words_by_syllables(SMOG_COMPLEX_SYL_FACTOR),
            self.bs.n_sents,
            *self.coefficients["smog_index"],
        )

    @property
    def automated_readability_index(self) -> float:
        return calc_automated_readability_index(
            self.bs.n_letters,
            self.bs.n_words,
            self.bs.n_sents,
            *self.coefficients["automated_readability_index"],
        )

    @property
    def lix(self) -> float:
        return calc_lix(
            self.bs.count_words_by_letters(LIX_LONG_WORD_LETTER_FACTOR),
            self.bs.n_words,
            self.bs.n_sents,
        )

    @property
    def rix(self) -> float:
        return calc_rix(
            self.bs.count_words_by_letters(LIX_LONG_WORD_LETTER_FACTOR), self.bs.n_sents
        )

    @property
    def sis_grade(self) -> float:
        return calc_sis_grade(self.bs.n_letters, self.bs.n_words, self.bs.n_sents)

    @property
    def matskovsky_index(self) -> float:
        return calc_matskovsky_index(
            self.bs.count_words_by_syllables(4), self.bs.n_words, self.bs.n_sents
        )

    @property
    def dale_chall_index(self) -> float:
        return calc_dale_chall_index(
            self.bs.count_words_by_syllables(SMOG_COMPLEX_SYL_FACTOR),
            self.bs.n_words,
            self.bs.n_sents,
        )

    @property
    def gunning_fog_index(self) -> float:
        return calc_gunning_fog_index(
            self.bs.count_words_by_syllables(SMOG_COMPLEX_SYL_FACTOR),
            self.bs.n_words,
            self.bs.n_sents,
        )

    def sis_grade_by_stage(self, stage: str) -> float:
        """
        Вычисление формулы Соловьёва, Иванова, Солнышкиной (2023) для ступени обучения

        Аргументы:
            stage (str): Ступень обучения (2-4, 5-7, 8-11)

        Вывод:
            float: Значение формулы

        Исключения:
            ValueError: Если указана неизвестная ступень обучения
        """
        if stage not in SIS_GRADE_STAGES:
            raise ValueError(
                f"Неизвестная ступень обучения: {stage}. "
                f"Доступные ступени: {tuple(SIS_GRADE_STAGES)}"
            )
        return calc_sis_grade(
            self.bs.n_letters, self.bs.n_words, self.bs.n_sents, *SIS_GRADE_STAGES[stage]
        )

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных метрик удобочитаемости текста

        Вывод:
            dict[str, float]: Справочник вычисленных метрик удобочитаемости текста
        """
        return {stat: getattr(self, stat) for stat in READABILITY_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных метрик удобочитаемости текста с описанием на экран"""
        print(f"{'Метрика':^45}|{'Значение':^10}")
        print("-" * 55)
        stats = self.get_stats()
        for stat, value in READABILITY_STATS_DESC.items():
            print(f"{value:45}|{stats.get(stat):^10.2f}")


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
        float: Значение теста
    """
    return (a * n_words / n_sents) + (b * n_syllables / n_words) - c


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
        float: Значение индекса
    """
    return c - (a * n_words / n_sents) - (b * n_syllables / n_words)


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
        n_letters (int): Количество букв
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение индекса
    """
    return (a * n_letters / n_words * 100) - (b * n_sents / n_words * 100) - c


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
        float: Значение индекса
    """
    return (a * sqrt(b * n_complex / n_sents)) + c


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
        n_letters (int): Количество букв
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a
        b (float): Коэффициент b
        c (float): Коэффициент c

    Вывод:
        float: Значение индекса
    """
    return (a * n_letters / n_words) + (b * n_words / n_sents) - c


def calc_lix(n_long_words: int, n_words: int, n_sents: int) -> float:
    """
    Вычисление индекса удобочитаемости LIX

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Значения индекса лежат в пределах от 0 до 100 и могут интерпретироваться следующим образом:
            0-30 - Очень простые тексты, детская литература
            30-40 - Простые тексты, художественная литература, газетные статьи
            40-50 - Тексты средней сложности, журнальные статьи
            50-60 - Сложные тексты, научно-популярные статьи, профессиональная литература, официальные тексты
            60-100 - Очень сложные тексты, написанные канцелярским языком, законы
        В канонической формуле длинным считается слово длиннее 6 букв, поэтому
        класс ReadabilityStats передает количество слов с числом букв не меньше 7

    Ссылки:
        https://en.wikipedia.org/wiki/Lix_(readability_test)
        https://ru.wikipedia.org/wiki/LIX

    Аргументы:
        n_long_words (int): Количество длинных слов
        n_words (int): Количество слов
        n_sents (int): Количество предложений

    Вывод:
        float: Значение индекса
    """
    return (n_words / n_sents) + (100 * n_long_words / n_words)


def calc_rix(n_long_words: int, n_sents: int) -> float:
    """
    Вычисление индекса удобочитаемости RIX

    Описание:
        Упрощенный спутник индекса LIX (1983, Anderson), не зависящий от языка
        Чем выше показатель, тем сложнее текст для чтения
        Значения индекса могут интерпретироваться следующим образом:
            < 0.2 - 1-й класс
            0.2-0.5 - 2-й класс
            0.5-0.8 - 3-й класс
            0.8-1.3 - 4-й класс
            1.3-1.8 - 5-й класс
            1.8-2.4 - 6-й класс
            2.4-3.0 - 7-й класс
            3.0-3.7 - 8-й класс
            3.7-4.5 - 9-й класс
            4.5-5.3 - 10-й класс
            5.3-6.2 - 11-й класс
            6.2-7.2 - 12-й класс
            > 7.2 - Студент университета
        Как и для LIX, длинным считается слово длиннее 6 букв, поэтому
        класс ReadabilityStats передает количество слов с числом букв не меньше 7

    Ссылки:
        https://en.wikipedia.org/wiki/Lix_(readability_test)

    Аргументы:
        n_long_words (int): Количество длинных слов
        n_sents (int): Количество предложений

    Вывод:
        float: Значение индекса
    """
    return n_long_words / n_sents


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
        n_letters (int): Количество букв
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a (свободный член)
        b (float): Коэффициент b (при средней длине предложения в словах)
        c (float): Коэффициент c (при средней длине слова в буквах)

    Вывод:
        float: Значение формулы
    """
    return a + (b * n_words / n_sents) + (c * n_letters / n_words)


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
        https://www.dialog-21.ru/media/4262/ivanovvv.pdf

    Аргументы:
        n_complex (int): Количество сложных слов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a (при средней длине предложения в словах)
        b (float): Коэффициент b (при доле сложных слов в процентах)
        c (float): Коэффициент c (свободный член)

    Вывод:
        float: Значение формулы
    """
    return (a * n_words / n_sents) + (b * 100 * n_complex / n_words) + c


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
        float: Значение индекса
    """
    return (a * 100 * n_complex / n_words) + (b * n_words / n_sents)


def calc_gunning_fog_index(n_complex: int, n_words: int, n_sents: int, a: float = 0.4) -> float:
    """
    Вычисление индекса Ганнинга

    Описание:
        Индекс туманности Ганнинга (1952, Gunning)
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Используется в адаптации проекта Plain Russian Language (Бегтин): сложным считается слово
        с числом слогов больше четырех, поэтому класс ReadabilityStats передает количество слов
        с числом слогов не меньше 5
        SEO-сервисы дополнительно умножают результат на 0.78, обоснование этого множителя не опубликовано

    Ссылки:
        https://en.wikipedia.org/wiki/Gunning_fog_index
        https://github.com/infoculture/plainrussian

    Аргументы:
        n_complex (int): Количество сложных слов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        a (float): Коэффициент a

    Вывод:
        float: Значение индекса
    """
    return a * ((n_words / n_sents) + (100 * n_complex / n_words))
