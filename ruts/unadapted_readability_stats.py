from __future__ import annotations

import anyts.unadapted_readability_stats
from anyts.unadapted_readability_stats import (
    calc_dickes_steiwer as calc_dickes_steiwer,
    calc_eflaw as calc_eflaw,
    calc_elf as calc_elf,
    calc_forcast as calc_forcast,
    calc_fucks as calc_fucks,
    calc_gulpease as calc_gulpease,
    calc_linsear_write as calc_linsear_write,
    calc_powers_sumner_kearl as calc_powers_sumner_kearl,
    calc_strain_index as calc_strain_index,
    calc_wheeler_smith as calc_wheeler_smith,
    calc_wiener_sachtextformel as calc_wiener_sachtextformel,
)

from .basic_stats import BasicStats
from .constants import CORE_MESSAGES, UNADAPTED_READABILITY_STATS_DESC


class UnadaptedReadabilityStats(anyts.unadapted_readability_stats.UnadaptedReadabilityStats):
    """
    Класс для вычисления формул удобочитаемости других языков с исходными коэффициентами

    Описание:
        Формулы, созданные для английского, немецкого и итальянского языков, с опубликованными
        коэффициентами, без калибровки под русский язык, по основным статистикам ruTS - буквам
        и слогам русских слов: значения сравнивают русские тексты между собой (Dickes-Steiwer -
        тексты одной длины) и с другими инструментами, но не дают класс русской школы и в сводный
        класс не входят; формулы с коэффициентами для русского языка - ReadabilityStats

    Пример использования:
        >>> from ruts import UnadaptedReadabilityStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> urs = UnadaptedReadabilityStats(text)
        >>> round(urs.forcast, 2), round(urs.gulpease, 2)
        (13.0, 65.67)

    Аргументы:
        source (str|Doc|BasicStats): Источник данных - строка, объект Doc или готовый
            объект BasicStats
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений; не
            используется для готовых основных статистик
        words_extractor (WordsExtractor): Инструмент для извлечения слов; не используется
            для готовых основных статистик

    Атрибуты:
        bs (BasicStats): Основные статистики текста
        forcast (float): Класс FORCAST
        linsear_write (float): Класс Linsear Write
        powers_sumner_kearl (float): Класс Пауэрса-Самнера-Керла
        eflaw (float): Индекс EFLAW Макалпайна
        wiener_sachtextformel_1 (float): Венская формула 1
        wiener_sachtextformel_2 (float): Венская формула 2
        wiener_sachtextformel_3 (float): Венская формула 3
        wiener_sachtextformel_4 (float): Венская формула 4
        dickes_steiwer (float): Индекс Дикеса-Штайвера
        gulpease (float): Индекс Gulpease
        fucks (float): Индекс Фукса
        strain_index (float): Индекс Strain
        elf (float): Формула легкости на слух (ELF)
        wheeler_smith (float): Индекс Уилера-Смита

    Методы:
        get_stats: Получение вычисленных формул
        to_dataframe: Получение формул таблицей из одной строки
        describe: Прочтение формулы по шкале; шкал у этих формул нет - None
        print_stats: Отображение вычисленных формул с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка, не объект Doc и не BasicStats
            или экстрактор другого типа
        SourceError: Если в источнике данных отсутствуют слова или предложения
    """

    basic_stats_class = BasicStats
    stats_desc = UNADAPTED_READABILITY_STATS_DESC
    stats_headers = ("Метрика", "Значение")
    messages = CORE_MESSAGES
