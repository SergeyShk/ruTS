import string
from pathlib import Path
from typing import TypedDict


class MorphologyStatDesc(TypedDict):
    name: str
    values: dict[str, str]


DEFAULT_DATA_DIR = Path(__file__).parent.parent.resolve() / "ruts_data"
RU_VOWELS = ["а", "е", "и", "у", "о", "я", "ё", "э", "ю", "ы"]
RU_VOWELS += list(map(str.upper, RU_VOWELS))
RU_CONSONANTS_LOW = ["к", "п", "с", "т", "ф", "х", "ц", "ч", "ш", "щ"]
RU_CONSONANTS_LOW += list(map(str.upper, RU_CONSONANTS_LOW))
RU_CONSONANTS_HIGH = ["б", "в", "г", "д", "ж", "з"]
RU_CONSONANTS_HIGH += list(map(str.upper, RU_CONSONANTS_HIGH))
RU_CONSONANTS_SONOR = ["л", "м", "н", "р"]
RU_CONSONANTS_SONOR += list(map(str.upper, RU_CONSONANTS_SONOR))
RU_CONSONANTS_YET = ["й", "Й"]
RU_CONSONANTS = RU_CONSONANTS_HIGH + RU_CONSONANTS_LOW + RU_CONSONANTS_SONOR + RU_CONSONANTS_YET
RU_MARKS = ["ь", "ъ", "Ь", "Ъ"]
RU_LETTERS = RU_CONSONANTS + RU_MARKS + RU_VOWELS
PUNCTUATIONS = string.punctuation + "—–…«»„“”‘’№"
SPACES = [" ", "\t"]
COMPLEX_SYL_FACTOR = 4
LONG_WORD_LETTER_FACTOR = 6
SMOG_COMPLEX_SYL_FACTOR = 5
LIX_LONG_WORD_LETTER_FACTOR = 7
BASIC_STATS_DESC = {
    "n_sents": "Предложения",
    "n_words": "Слова",
    "n_unique_words": "Уникальные слова",
    "n_long_words": "Длинные слова",
    "n_complex_words": "Сложные слова",
    "n_simple_words": "Простые слова",
    "n_monosyllable_words": "Односложные слова",
    "n_polysyllable_words": "Многосложные слова",
    "n_chars": "Символы",
    "n_letters": "Буквы",
    "n_spaces": "Пробелы",
    "n_syllables": "Слоги",
    "n_punctuations": "Знаки препинания",
}
READABILITY_STATS_DESC = {
    "flesch_kincaid_grade": "Тест Флеша-Кинкайда",
    "flesch_reading_easy": "Индекс удобочитаемости Флеша",
    "coleman_liau_index": "Индекс Колман-Лиау",
    "smog_index": "Индекс SMOG",
    "automated_readability_index": "Автоматический индекс удобочитаемости",
    "lix": "Индекс удобочитаемости LIX",
    "rix": "Индекс удобочитаемости RIX",
    "sis_grade": "Формула Соловьёва, Иванова, Солнышкиной",
    "matskovsky_index": "Формула Мацковского",
    "dale_chall_index": "Индекс Дейла-Чейла",
    "gunning_fog_index": "Индекс Ганнинга",
    "consensus_grade": "Сводный класс",
    "reading_time": "Время чтения (мин.)",
}
READABILITY_GRADE_STATS = (
    "flesch_kincaid_grade",
    "coleman_liau_index",
    "smog_index",
    "automated_readability_index",
    "sis_grade",
    "dale_chall_index",
    "gunning_fog_index",
)
GRADE_AGE_LEVELS: tuple[tuple[int, int, str, str], ...] = (
    (1, 3, "1-3-й класс", "6-8 лет"),
    (4, 6, "4-6-й класс", "9-11 лет"),
    (7, 9, "7-9-й класс", "12-14 лет"),
    (10, 11, "10-11-й класс", "15-16 лет"),
    (12, 14, "1-3-й курс вуза", "17-19 лет"),
    (15, 17, "4-6-й курс вуза", "20-22 года"),
)
POSTGRADUATE_LEVEL = ("аспирантура", "старше 22 лет")
READING_SPEED_WPM = 180
READING_SPEED_NORMS: dict[str, tuple[int, int]] = {
    "adult_silent": (120, 180),
    "grade_1": (25, 40),
    "grade_2": (60, 80),
    "grade_3": (80, 100),
    "grade_4": (90, 110),
}
_PLAINRUSSIAN_ADAPTED_COEFFICIENTS = {
    "coleman_liau_index": (0.055, 0.35, 20.33),
    "smog_index": (1.1, 64.6, 0.05),
    "automated_readability_index": (6.26, 0.2805, 31.04),
}
READABILITY_PRESETS: dict[str, dict[str, tuple[float, float, float]]] = {
    "plainrussian": {
        "flesch_kincaid_grade": (0.318, 14.2, 30.5),
        "flesch_reading_easy": (1.3, 60.1, 206.835),
        **_PLAINRUSSIAN_ADAPTED_COEFFICIENTS,
    },
    "fiction": {
        "flesch_kincaid_grade": (0.5, 8.4, 15.59),
        "flesch_reading_easy": (1.3, 60.1, 206.835),
        **_PLAINRUSSIAN_ADAPTED_COEFFICIENTS,
    },
    "academic": {
        "flesch_kincaid_grade": (0.36, 5.76, 11.97),
        "flesch_reading_easy": (1.52, 65.14, 206.836),
        **_PLAINRUSSIAN_ADAPTED_COEFFICIENTS,
    },
}
SIS_GRADE_STAGES: dict[str, tuple[float, float, float]] = {
    "2-4": (-2.59, 0.17, 0.61),
    "5-7": (-5.29, 0.20, 1.34),
    "8-11": (-3.26, 0.21, 1.35),
}
MORPHOLOGY_STATS_DESC: dict[str, MorphologyStatDesc] = {
    "pos": {
        "name": "Часть речи",
        "values": {
            "NOUN": "Имя существительное",
            "ADJF": "Имя прилагательное (полное)",
            "ADJS": "Имя прилагательное (краткое)",
            "COMP": "Компаратив",
            "VERB": "Глагол (личная форма)",
            "INFN": "Глагол (инфинитив)",
            "PRTF": "Причастие (полное)",
            "PRTS": "Причастие (краткое)",
            "GRND": "Деепричастие",
            "NUMR": "Числительное",
            "ADVB": "Наречие",
            "NPRO": "Местоимение-существительное",
            "PRED": "Предикатив",
            "PREP": "Предлог",
            "CONJ": "Союз",
            "PRCL": "Частица",
            "INTJ": "Междометие",
        },
    },
    "animacy": {
        "name": "Одушевленность",
        "values": {"anim": "Одушевлённое", "inan": "Неодушевлённое"},
    },
    "aspect": {
        "name": "Вид",
        "values": {"perf": "Совершенный", "impf": "Несовершенный"},
    },
    "case": {
        "name": "Падеж",
        "values": {
            "nomn": "Именительный",
            "gent": "Родительный",
            "datv": "Дательный",
            "accs": "Винительный",
            "ablt": "Творительный",
            "loct": "Предложный",
            "voct": "Звательный",
            "gen1": "Первый родительный",
            "gen2": "Второй родительный (частичный)",
            "acc2": "Второй винительный",
            "loc1": "Первый предложный",
            "loc2": "Второй предложный (местный)",
        },
    },
    "gender": {
        "name": "Род",
        "values": {
            "masc": "Мужской",
            "femn": "Женский",
            "neut": "Средний",
            "ms-f": "Общий",
        },
    },
    "involvement": {
        "name": "Совместность",
        "values": {
            "incl": "Говорящий включён в действие",
            "excl": "Говорящий не включён в действие",
        },
    },
    "mood": {
        "name": "Наклонение",
        "values": {"indc": "Изъявительное", "impr": "Повелительное"},
    },
    "number": {
        "name": "Число",
        "values": {"sing": "Единственное", "plur": "Множественное"},
    },
    "person": {"name": "Лицо", "values": {"1per": "1", "2per": "2", "3per": "3"}},
    "tense": {
        "name": "Время",
        "values": {"pres": "Настоящее", "past": "Прошедшее", "futr": "Будущее"},
    },
    "transitivity": {
        "name": "Переходность",
        "values": {"tran": "Переходный", "intr": "Непереходный"},
    },
    "voice": {
        "name": "Залог",
        "values": {"actv": "Действительный", "pssv": "Страдательный"},
    },
}
DIVERSITY_STATS_DESC = {
    "ttr": "Type-Token Ratio (TTR)",
    "rttr": "Root Type-Token Ratio (RTTR)",
    "cttr": "Corrected Type-Token Ratio (CTTR)",
    "httr": "Herdan Type-Token Ratio (HTTR)",
    "sttr": "Summer Type-Token Ratio (STTR)",
    "mttr": "Maas Type-Token Ratio (MTTR)",
    "dttr": "Dugast Type-Token Ratio (DTTR)",
    "mattr": "Moving Average Type-Token Ratio (MATTR)",
    "msttr": "Mean Segmental Type-Token Ratio (MSTTR)",
    "mtld": "Measure of Textual Lexical Diversity (MTLD)",
    "mamtld": "Moving Average Measure of Textual Lexical Diversity (MA-MTLD)",
    "mtldw": "Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W)",
    "hdd": "Hypergeometric Distribution D (HD-D)",
    "simpson_index": "Индекс Симпсона (D)",
    "inverse_simpson_index": "Обратный индекс Симпсона (1/D)",
    "gini_simpson_index": "Индекс Джини-Симпсона (1-D)",
    "hapax_index": "Гапакс-индекс (Honoré's R)",
    "yule_k": "Характеристика Юла (Yule's K)",
    "yule_i": "Обратная характеристика Юла (Yule's I)",
    "herdan_vm": "Мера Хердана (Herdan's Vm)",
    "sichel_s": "Мера Сишела (Sichel's S)",
    "michea_m": "Мера Мишеа (Michéa's M)",
    "brunet_w": "Мера Брюне (Brunet's W)",
    "dugast_k": "Мера Дюга (Dugast's k)",
    "baayen_p": "Мера Баайена (Baayen's P)",
    "hapax_ratio": "Доля гапаксов",
    "alpha2": "Показатель α₂",
    "entropy": "Энтропия Шеннона (бит)",
    "evenness": "Выравненность",
    "perplexity": "Перплексия",
    "zipf_alpha": "Наклон закона Ципфа (α)",
    "heaps_beta": "Показатель закона Хипса (β)",
}
STYLE_STATS_DESC = {
    "classic_nausea": "Классическая тошнота",
    "academic_nausea": "Академическая тошнота (%)",
    "water": "Водность (%)",
    "spam": "Заспамленность (%)",
    "zipf_naturalness": "Естественность по Ципфу (%)",
}
PHON_STATS_DESC = {
    "p_vowels": "Доля гласных",
    "p_sonorants": "Доля сонорных согласных",
    "p_voiced": "Доля звонких шумных согласных",
    "p_voiceless": "Доля глухих шумных согласных",
    "consonant_vowel_ratio": "Отношение согласных к гласным",
    "p_heavy_clusters": "Доля кластеров из 3 и более согласных",
    "p_hiatus": "Зияний гласных на слово",
    "cv_entropy": "Энтропия CV-шаблонов слов (бит)",
    "hardness": "Жёсткость",
    "alliteration": "Индекс аллитерации",
    "assonance": "Индекс ассонанса",
    "p_open_syllables": "Доля открытых слогов",
    "mean_syllable_len": "Средняя длина слога (букв)",
}
PHON_WINDOW_LEN = 3
SYNTAX_STATS_DESC = {
    "mean_dependency_distance": "Средняя длина зависимости",
    "std_dependency_distance": "Стандартное отклонение длины зависимости",
    "max_dependency_distance": "Максимальная длина зависимости",
    "p_adjacent_dependencies": "Доля смежных связей",
    "tree_depth": "Глубина дерева зависимостей",
    "leaves_per_sent": "Листьев на предложение",
    "subtrees_per_sent": "Поддеревьев на предложение",
    "nodes_per_leaf": "Узлов на лист",
    "verb_valency": "Валентность финитных глаголов",
    "coordination_chains_per_sent": "Сочинительных цепочек на предложение",
    "mean_coordination_chain_len": "Средняя длина сочинительной цепочки",
    "clauses_per_sent": "Клауз на предложение",
    "mean_clause_len": "Средняя длина клаузы (слов)",
    "subordinate_clauses_per_sent": "Придаточных клауз на предложение",
    "p_complex_sents": "Доля предложений с придаточными",
    "modifiers_per_noun": "Модификаторов на именную группу",
    "genitive_chains_per_sent": "Цепочек родительных падежей на предложение",
    "max_genitive_chain_len": "Максимальная длина цепочки родительных падежей",
    "participle_clauses_per_sent": "Причастных оборотов на предложение",
    "mean_participle_clause_len": "Средняя длина причастного оборота (слов)",
    "converb_clauses_per_sent": "Деепричастных оборотов на предложение",
    "mean_converb_clause_len": "Средняя длина деепричастного оборота (слов)",
    "p_passive": "Доля пассивных форм среди глаголов",
    "p_agentless_passive": "Доля безагентного пассива",
    "infinitives_per_sent": "Инфинитивов на предложение",
    "negations_per_sent": "Отрицаний на предложение",
}
CLAUSE_DEPS = frozenset({"ccomp", "advcl", "acl", "acl:relcl", "csubj", "csubj:pass", "parataxis"})
SUBORDINATE_CLAUSE_DEPS = frozenset({"ccomp", "advcl", "acl", "acl:relcl", "csubj", "csubj:pass"})
SUBJECT_DEPS = frozenset({"nsubj", "csubj"})
VALENCY_IGNORED_DEPS = frozenset({"cc", "conj", "parataxis", "punct"})
NOUN_MODIFIER_DEPS = frozenset({"amod", "det", "nmod", "nummod", "acl"})
PASSIVE_DEPS = frozenset({"nsubj:pass", "csubj:pass", "aux:pass"})
NEGATION_PARTICLES = frozenset({"не", "ни"})
STOPWORD_POS = frozenset({"CONJ", "PRCL", "PREP", "NPRO", "INTJ", "PRED"})
STOPWORD_GRAMMEMES = frozenset({"Apro", "Prnt", "Dmns", "Ques"})
NAUSEA_TOP_N = 10
MATTR_WINDOW_LEN = 50
MTLD_TTR_THRESHOLD = 0.72
MTLD_MIN_LEN = 10
HDD_SAMPLE_SIZE = 42
DIVERSITY_LOG_BASE = 10
BRUNET_W_EXPONENT = 0.172
