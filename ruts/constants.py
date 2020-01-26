import string
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).parent.parent.resolve() / "ruts_data"
RU_VOWELS = ['а', 'е', 'и', 'у', 'о', 'я', 'ё', 'э', 'ю', 'ы']
RU_VOWELS += list(map(str.upper, RU_VOWELS))
RU_CONSONANTS_LOW = ['к', 'п', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ']
RU_CONSONANTS_LOW += list(map(str.upper, RU_CONSONANTS_LOW))
RU_CONSONANTS_HIGH = ['б', 'в', 'г', 'д', 'ж', 'з']
RU_CONSONANTS_HIGH += list(map(str.upper, RU_CONSONANTS_HIGH))
RU_CONSONANTS_SONOR = ['л', 'м', 'н', 'р']
RU_CONSONANTS_SONOR += list(map(str.upper, RU_CONSONANTS_SONOR))
RU_CONSONANTS_YET = ['й', 'Й']
RU_CONSONANTS = RU_CONSONANTS_HIGH + RU_CONSONANTS_LOW + RU_CONSONANTS_SONOR + RU_CONSONANTS_YET
RU_MARKS = ['ь', 'ъ', 'Ь', 'Ъ']
RU_LETTERS = RU_CONSONANTS + RU_MARKS + RU_VOWELS
PUNCTUATIONS = string.punctuation + '—«»“”'
SPACES = [' ', '\t']
COMPLEX_SYL_FACTOR = 4
BASIC_STATS_DESC = {
    'n_sents': 'Предложения',
    'n_words': 'Слова',
    'n_unique_words': 'Уникальные слова',
    'n_long_words': 'Длинные слова',
    'n_complex_words': 'Сложные слова',
    'n_simple_words': 'Простые слова',
    'n_monosyllable_words': 'Односложные слова',
    'n_polysyllable_words': 'Многосложные слова',
    'n_chars': 'Символы',
    'n_letters': 'Буквы',
    'n_spaces': 'Пробелы',
    'n_syllables': 'Слоги',
    'n_punctuations': 'Знаки препинания'
}
READABILITY_STATS_DESC = {
    'flesch_kincaid_grade': 'Тест Флеша-Кинкайда',
    'flesch_reading_easy': 'Индекс удобочитаемости Флеша',
    'coleman_liau_index': 'Индекс Колман-Лиау',
    'smog_index': 'Индекс SMOG',
    'automated_readability_index': 'Автоматический индекс удобочитаемости',
    'lix': 'Индекс удобочитаемости LIX'
}
MORPHOLOGY_STATS_DESC = {
    'pos': {
        'name': 'Часть речи',
        'values': {
            'NOUN': 'Имя существительное',
            'ADJF': 'Имя прилагательное (полное)',
            'ADJS': 'Имя прилагательное (краткое)',
            'COMP': 'Компаратив',
            'VERB': 'Глагол (личная форма)',
            'INFN': 'Глагол (инфинитив)',
            'PRTF': 'Причастие (полное)',
            'PRTS': 'Причастие (краткое)',
            'GRND': 'Деепричастие',
            'NUMR': 'Числительное',
            'ADVB': 'Наречие',
            'NPRO': 'Местоимение-существительное',
            'PRED': 'Предикатив',
            'PREP': 'Предлог',
            'CONJ': 'Союз',
            'PRCL': 'Частица',
            'INTJ': 'Междометие'
        }
    },
    'animacy': {
        'name': 'Одушевленность',
        'values': {
            'anim': 'Одушевлённое',
            'inan': 'Неодушевлённое'
        }
    },
    'aspect': {
        'name': 'Вид',
        'values': {
            'perf': 'Совершенный',
            'impf': 'Несовершенный'
        }
    },
    'case': {
        'name': 'Падеж',
        'values': {
            'nomn': 'Именительный',
            'gent': 'Родительный',
            'datv': 'Дательный',
            'accs': 'Винительный',
            'ablt': 'Творительный',
            'loct': 'Предложный',
            'voct': 'Звательный',
            'gen1': 'Первый родительный',
            'gen2': 'Второй родительный (частичный)',
            'acc2': 'Второй винительный',
            'loc1': 'Первый предложный',
            'loc2': 'Второй предложный (местный)'
        }
    },
    'gender': {
        'name': 'Род',
        'values': {
            'masc': 'Мужской',
            'femn': 'Женский',
            'neut': 'Средний',
            'ms-f': 'Общий'
        }
    },
    'involvement': {
        'name': 'Совместность',
        'values': {
            'incl': 'Говорящий включён в действие',
            'excl': 'Говорящий не включён в действие'
        }
    },
    'mood': {
        'name': 'Наклонение',
        'values': {
            'indc': 'Изъявительное',
            'impr': 'Повелительное'
        }
    },
    'number': {
        'name': 'Число',
        'values': {
            'sing': 'Единственное',
            'plur': 'Множественное'
        }
    },
    'person': {
        'name': 'Лицо',
        'values': {
            '1per': '1',
            '2per': '2',
            '3per': '3'
        }
    },
    'tense': {
        'name': 'Время',
        'values': {
            'pres': 'Настоящее',
            'past': 'Прошедшее',
            'futr': 'Будущее'
        }
    },
    'transitivity': {
        'name': 'Переходность',
        'values': {
            'tran': 'Переходный',
            'intr': 'Непереходный'
        }
    },
    'voice': {
        'name': 'Залог',
        'values': {
            'actv': 'Действительный',
            'pssv': 'Страдательный'
        }
    }
}