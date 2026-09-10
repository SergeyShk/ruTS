from collections import Counter, OrderedDict

from spacy.tokens import Doc

from .constants import MORPHOLOGY_STATS_DESC
from .extractors import WordsExtractor
from .utils import get_morph_analyzer


class MorphStats:
    """
    Класс для вычисления морфологических статистик текста

    Описание:
        Для морфологического разбора текста используется библиотека pymorphy3
        Описание статистик взяты из корпуса OpenCorpora

    Ссылки:
        https://github.com/no-plagiarism/pymorphy3
        http://opencorpora.org/dict.php?act=gram

    Пример использования:
        >>> from ruts import MorphStats
        >>> text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
        >>> ms = MorphStats(text)
        >>> ms.get_stats()
        {'animacy': {None: 11},
        'aspect': {None: 5, 'impf': 1, 'perf': 5},
        'case': {None: 11},
        'gender': {None: 11},
        'involvement': {None: 10, 'excl': 1},
        'mood': {None: 7, 'impr': 1, 'indc': 3},
        'number': {None: 7, 'plur': 3, 'sing': 1},
        'person': {None: 9, '2per': 1, '3per': 1},
        'pos': {'ADVB': 1, 'CONJ': 4, 'INFN': 2, 'VERB': 4},
        'tense': {None: 8, 'futr': 1, 'past': 1, 'pres': 1},
        'transitivity': {None: 5, 'intr': 2, 'tran': 4},
        'voice': {None: 11}}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        tags (tuple[str]): Кортеж извлеченных тэгов OpenCorpora
        pos (tuple[str]): Кортеж значений части речи
        animacy (tuple[str]): Кортеж значений одушевленности
        aspect (tuple[str]): Кортеж значений вида
        case (tuple[str]): Кортеж значений падежа
        gender (tuple[str]): Кортеж значений пола
        involvement (tuple[str]): Кортеж значений совместности
        mood (tuple[str]): Кортеж значений наклонения
        number (tuple[str]): Кортеж значений числа
        person (tuple[str]): Кортеж значений лица
        tense (tuple[str]): Кортеж значений времени
        transitivity (tuple[str]): Кортеж значений переходности
        voice (tuple[str]): Кортеж значений залога

    Методы:
        get_stats: Получение вычисленных морфологических статистик текста
        explain_text: Разбор текста по морфологическим статистикам
        print_stats: Отображение вычисленных морфологических статистик текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
    """

    def __init__(self, source: str | Doc, words_extractor: WordsExtractor | None = None):
        if isinstance(source, Doc):
            text = source.text
            self.words = tuple(word.text for word in source)
        elif isinstance(source, str):
            text = source
            if not words_extractor:
                words_extractor = WordsExtractor()
            self.words = words_extractor.extract(text)
        else:
            raise TypeError("Некорректный источник данных")
        if not self.words:
            raise ValueError("В источнике данных отсутствуют слова")

        morph = get_morph_analyzer()
        self.tags = tuple(morph.parse(word)[0].tag for word in self.words)
        self.pos = tuple(tag.POS for tag in self.tags)
        self.animacy = tuple(tag.animacy for tag in self.tags)
        self.aspect = tuple(tag.aspect for tag in self.tags)
        self.case = tuple(tag.case for tag in self.tags)
        self.gender = tuple(tag.gender for tag in self.tags)
        self.involvement = tuple(tag.involvement for tag in self.tags)
        self.mood = tuple(tag.mood for tag in self.tags)
        self.number = tuple(tag.number for tag in self.tags)
        self.person = tuple(tag.person for tag in self.tags)
        self.tense = tuple(tag.tense for tag in self.tags)
        self.transitivity = tuple(tag.transitivity for tag in self.tags)
        self.voice = tuple(tag.voice for tag in self.tags)

    def get_stats(self, *args: str, filter_none: bool = False) -> dict[str, dict[str, int]]:
        """
        Получение вычисленных морфологических статистик текста

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения

        Вывод:
            dict[str, dict[str, int]]: Справочник вычисленных морфологических статистик текста
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        stats: dict[str, dict[str, int]] = {}
        for arg in args:
            counts = dict(Counter(getattr(self, arg)))
            stats[arg] = {k: v for (k, v) in counts.items() if k} if filter_none else counts
        return stats

    def explain_text(
        self, *args: str, filter_none: bool = False
    ) -> tuple[tuple[str, dict[str, str]], ...]:
        """
        Разбор текста по морфологическим статистикам

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения

        Вывод:
            tuple[str, dict[str, str]]: Кортеж слов текста с морфологическими статистиками
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        values = tuple(zip(*(getattr(self, arg) for arg in args), strict=False))
        if filter_none:
            explains = tuple(
                {k: v for (k, v) in dict(zip(args, value, strict=False)).items() if v}
                for value in values
            )
        else:
            explains = tuple(dict(zip(args, value, strict=False)) for value in values)
        return tuple(zip(self.words, explains, strict=False))

    def print_stats(self, *args: str, filter_none: bool = False) -> None:
        """
        Отображение вычисленных морфологических статистик текста с описанием на экран

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        stats = self.get_stats(*args)
        for stat, values in stats.items():
            stat_desc = MORPHOLOGY_STATS_DESC[stat]
            print(f"{stat_desc['name'].center(40, '-')}")
            value_desc = stat_desc["values"]
            for value, number in OrderedDict(
                sorted(values.items(), key=lambda x: x[1], reverse=True)
            ).items():
                if filter_none and not value:
                    continue
                print(f"{value_desc.get(value) if value else 'Неизвестно':30}|{number!s:^10}")
            print()

    @staticmethod
    def __check_stat(*args: str) -> bool:
        """
        Проверка выбранных морфологических статистик

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик

        Вывод:
            bool: Результат проверки

        Исключения:
            KeyError: Если выбранная статистика отсутствует в справочнике
        """
        for arg in args:
            if not MORPHOLOGY_STATS_DESC.get(arg):
                print(
                    f"Реализованные морфологичесские статистики: {tuple(MORPHOLOGY_STATS_DESC.keys())}"
                )
                raise KeyError(arg + " отсутствует в справочнике морфологических статистик")
        return True
