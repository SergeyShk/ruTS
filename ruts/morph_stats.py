import pymorphy2
from .constants import MORPHOLOGY_STATS_DESC
from .extractors import WordsExtractor
from collections import Counter, OrderedDict
from typing import Dict, Tuple

class MorphStats(object):
    """
    Класс для вычисления морфологических статистик текста

    Описание:
        Для морфологического разбора текста используется библиотека pymorphy2
        Описание статистик взяты из корпуса OpenCorpora

    Ссылки:
        https://pymorphy2.readthedocs.io/en/0.2/user/index.html
        http://opencorpora.org/dict.php?act=gram

    Аргументы:
        text (str): Строка текста
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
        ValueError: Если анализируемый текст является пустой строкой
    """

    def __init__(
        self,
        text: str,
        words_extractor: WordsExtractor = None
    ):
        words_extractor = WordsExtractor(text)
        if not text:
            raise ValueError("Анализируемый текст пуст")

        morph = pymorphy2.MorphAnalyzer()
        self.words = words_extractor.extract()
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

    def get_stats(
        self,
        *args: Tuple[str, ...],
        filter_none: bool = False
    ) -> Dict[str, Dict[str, int]]:
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
        stats = dict()
        for arg in args:
            if filter_none:
                stats[arg] = dict((k, v) for (k, v) in dict(Counter(vars(self).get(arg))).items() if k)
            else:
                stats[arg] = dict(Counter(vars(self).get(arg)))
        return stats

    def explain_text(
        self,
        *args: Tuple[str, ...],
        filter_none: bool = False
    ) -> Dict[str, Dict[str, str]]:
        """
        Разбор текста по морфологическим статистикам

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения

        Вывод:
            dict[str, dict[str, str]]: Справочник слов текста с морфологическими статистиками
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        values = tuple(zip(*(vars(self).get(arg) for arg in args)))
        if filter_none:
            explains = tuple(dict((k, v) for (k, v) in dict(zip(args, value)).items() if v) for value in values)
        else:
            explains = tuple(dict(zip(args, value)) for value in values)
        print(tuple(zip(self.words, explains)))

    def print_stats(
        self,
        *args: Tuple[str, ...],
        filter_none: bool = False
    ):
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
            stat_desc = MORPHOLOGY_STATS_DESC.get(stat)
            print(f"{stat_desc.get('name').center(40, '-')}")
            value_desc = stat_desc.get('values')
            for value, number in OrderedDict(sorted(values.items(), key=lambda x: x[1], reverse=True)).items():
                if filter_none and not value:
                    continue
                print(f"{value_desc.get(value) if value else 'Неизвестно':30}|{str(number):^10}")
            print()

    @staticmethod
    def __check_stat(*args: Tuple[str, ...]) -> bool:
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
                print(f"Реализованные морфологичесские статистики: {tuple(MORPHOLOGY_STATS_DESC.keys())}")
                raise KeyError(arg + " отсутствует в справочнике морфологических статистик")
        return True


if __name__ == "__main__":
    from pprint import pprint
    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
    ms = MorphStats(text)
    print(ms.pos)
    pprint(ms.get_stats())
    ms.print_stats('pos', 'tense')
    ms.explain_text(filter_none=True)