import string

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