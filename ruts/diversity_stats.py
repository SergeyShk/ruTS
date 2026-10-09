from collections.abc import Sequence

import anyts
from anyts.constants import (
    DIVERSITY_LOG_BASE,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
)
from anyts.diversity_stats import (
    HeapsFit as HeapsFit,
    WindowStats as WindowStats,
    ZipfMandelbrot as ZipfMandelbrot,
    calc_alpha2 as calc_alpha2,
    calc_baayen_p as calc_baayen_p,
    calc_brunet_w as calc_brunet_w,
    calc_cttr as calc_cttr,
    calc_dttr as calc_dttr,
    calc_dugast_k as calc_dugast_k,
    calc_entropy as calc_entropy,
    calc_evenness as calc_evenness,
    calc_frequency_spectrum as calc_frequency_spectrum,
    calc_gini_simpson_index as calc_gini_simpson_index,
    calc_hapax_index as calc_hapax_index,
    calc_hapax_ratio as calc_hapax_ratio,
    calc_hdd as calc_hdd,
    calc_heaps_beta as calc_heaps_beta,
    calc_herdan_vm as calc_herdan_vm,
    calc_honore_r as calc_honore_r,
    calc_httr as calc_httr,
    calc_inverse_simpson_index as calc_inverse_simpson_index,
    calc_mamtld as calc_mamtld,
    calc_mattr as calc_mattr,
    calc_michea_m as calc_michea_m,
    calc_msttr as calc_msttr,
    calc_mtld as calc_mtld,
    calc_mtldw as calc_mtldw,
    calc_mttr as calc_mttr,
    calc_perplexity as calc_perplexity,
    calc_rttr as calc_rttr,
    calc_sichel_s as calc_sichel_s,
    calc_simpson_index as calc_simpson_index,
    calc_sttr as calc_sttr,
    calc_ttr as calc_ttr,
    calc_windowed as calc_windowed,
    calc_yule_i as calc_yule_i,
    calc_yule_k as calc_yule_k,
    calc_zipf_alpha as calc_zipf_alpha,
    check_params as check_params,
    fit_heaps as fit_heaps,
    fit_zipf_mandelbrot as fit_zipf_mandelbrot,
    vocabulary_growth as vocabulary_growth,
)
from anyts.utils import iter_doc_words
from spacy.tokens import Doc

from .constants import DIVERSITY_STATS_DESC
from .exceptions import SourceTypeError
from .extractors import WordsExtractor
from .utils import strip_marks


class DiversityStats(anyts.DiversityStats):
    """
    Класс для вычисления основных метрик лексического разнообразия текста

    Описание:
        Лексическое разнообразие - это количественная характеристика текста,
        отражающая степень богатства словаря при построении текста заданной длины
        Соглашения, принятые в библиотеке (совпадают с koRpus и lexical-diversity Кайла):
            логарифмические меры Summer, Maas и Dugast считаются по основанию 10,
            LexicalRichness, textcomplexity и zipfR используют натуральный логарифм
            окно MATTR и MSTTR равно 50 словам, quanteda и koRpus используют 100
            порог TTR для MTLD равен 0.72, минимальная длина фактора - 10 слов;
            фактор закрывается при TTR не больше порога (включительно), в lexical-diversity
            и TAALED сравнение строгое, поэтому значения расходятся на факторах,
            где TTR попадает ровно в 0.72
            размер выборки HD-D равен 42 словам
        Все соглашения вынесены в параметры класса

    Ссылки:
        https://ru.wikipedia.org/wiki/Коэффициент_лексического_разнообразия
        https://en.wikipedia.org/wiki/Lexical_diversity
        https://ru.wikipedia.org/wiki/Мера_разнообразия
        https://en.wikipedia.org/wiki/Diversity_index
        https://core.ac.uk/download/pdf/82620241.pdf

    Пример использования:
        >>> from ruts import DiversityStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> ds = DiversityStats(text)
        >>> ds.ttr
        0.7333333333333333
        >>> ds.yule_k
        444.44444444444446
        >>> ds.windowed("ttr", window_len=5)
        WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc); слова всегда
            приводятся к нижнему регистру
        words_extractor (WordsExtractor): Инструмент для извлечения слов; для Doc
            применяется к тексту Doc, без него слова берутся из токенов
        window_len (int): Размер окна для MATTR и сегмента для MSTTR
        mtld_threshold (float): Порог TTR для MTLD, MA-MTLD и MTLD-W
        mtld_min_len (int): Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W
        hdd_sample_size (int): Размер выборки для HD-D
        log_base (float): Основание логарифма для метрик Summer, Maas и Dugast

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов в нижнем регистре
        frequency_spectrum (dict[int, int]): Спектр частот - количество лексем с заданной частотой
        ttr (float): Метрика Type-Token Ratio (TTR)
        rttr (float): Метрика Root Type-Token Ratio (RTTR)
        cttr (float): Метрика Corrected Type-Token Ratio (CTTR)
        httr (float): Метрика Herdan Type-Token Ratio (HTTR)
        sttr (float): Метрика Summer Type-Token Ratio (STTR)
        mttr (float): Метрика Maas Type-Token Ratio (MTTR)
        dttr (float): Метрика Dugast Type-Token Ratio (DTTR)
        mattr (float): Метрика Moving Average Type-Token Ratio (MATTR)
        msttr (float): Метрика Mean Segmental Type-Token Ratio (MSTTR)
        mtld (float): Метрика Measure of Textual Lexical Diversity (MTLD)
        mamtld (float): Метрика Moving Average Measure of Textual Lexical Diversity (MA-MTLD)
        mtldw (float): Метрика MTLD со скользящим окном и заворотом текста (MTLD-W)
        hdd (float): Метрика Hypergeometric Distribution D (HD-D)
        simpson_index (float): Индекс Симпсона (D)
        inverse_simpson_index (float): Обратный индекс Симпсона (1/D)
        gini_simpson_index (float): Индекс Джини-Симпсона (1-D)
        hapax_index (float): Гапакс-индекс, он же Honoré's R
        honore_r (float): Псевдоним для гапакс-индекса
        yule_k (float): Характеристика Юла (Yule's K)
        yule_i (float): Обратная характеристика Юла (Yule's I)
        herdan_vm (float): Мера Хердана (Herdan's Vm)
        sichel_s (float): Мера Сишела (Sichel's S)
        michea_m (float): Мера Мишеа (Michéa's M)
        brunet_w (float): Мера Брюне (Brunet's W)
        dugast_k (float): Мера Дюга (Dugast's k)
        baayen_p (float): Мера Баайена (Baayen's P)
        hapax_ratio (float): Доля гапаксов среди лексем
        alpha2 (float): Показатель α₂
        entropy (float): Энтропия Шеннона в битах
        evenness (float): Выравненность - отношение энтропии к максимальной
        perplexity (float): Перплексия
        zipf_alpha (float): Наклон закона Ципфа
        heaps_beta (float): Показатель закона Хипса

    Методы:
        windowed: Оконный расчет метрики со средним и доверительным интервалом
        get_stats: Получение вычисленных метрик лексического разнообразия текста
        print_stats: Отображение вычисленных метрик лексического разнообразия текста с описанием на экран

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
            или экстрактор не WordsExtractor
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если параметры метрик заданы некорректно
    """

    stats_desc = DIVERSITY_STATS_DESC
    stats_headers = ("Метрика", "Значение")

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        window_len: int = MATTR_WINDOW_LEN,
        mtld_threshold: float = MTLD_TTR_THRESHOLD,
        mtld_min_len: int = MTLD_MIN_LEN,
        hdd_sample_size: int = HDD_SAMPLE_SIZE,
        log_base: float = DIVERSITY_LOG_BASE,
    ):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError("Экстрактор слов должен быть WordsExtractor")
        check_params(window_len, mtld_threshold, mtld_min_len, hdd_sample_size, log_base)
        if isinstance(source, Doc) and words_extractor is None:
            words: Sequence[str] = [
                strip_marks(word) for _, _, word in iter_doc_words(source, join_hyphens=True)
            ]
        elif isinstance(source, Doc | str):
            text = source.text if isinstance(source, Doc) else source
            words = (words_extractor or WordsExtractor()).extract(text)
        else:
            raise SourceTypeError("Некорректный источник данных")
        super().__init__(
            [word.lower() for word in words],
            window_len,
            mtld_threshold,
            mtld_min_len,
            hdd_sample_size,
            log_base,
        )
