from collections import Counter
from ruts.constants import COMPLEX_SYL_FACTOR, RU_LETTERS, SPACES, BASIC_STATS_DESC
from ruts.utils import count_syllables, extract_sents, extract_words
from spacy.tokens import Doc

class BasicStats():
    """
    Вычисление основных статистик текста

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_tokenizer (func|Pattern): Токенизатор для предложений (функция или регулярное выражение)
        words_tokenizer (func|Pattern): Токенизатор для слов (функция или регулярное выражение)

    Атрибуты:
        c_chars (dict[int, int]): Распределение слов по количеству символов
        c_syllables (dict[int, int]): Распределение слов по количеству слогов
        n_sents (int): Количество предложений
        n_words (int): Количество слов
        n_unique_words (int): Количество уникальных слов
        n_long_words (int): Количество длинных слов
        n_complex_words (int): Количество сложных слов
        n_simple_words (int): Количество простых слов
        n_monosyllable_words (int): Количество односложных слов
        n_polysyllable_words (int): Количество многосложных слов
        n_chars (int): Количество символов
        n_letters (int): Количество букв
        n_spaces (int): Количество пробелов
        n_syllables (int): Количество слогов

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если анализируемый текст является пустой строкой
    """

    def __init__(self, source, sents_tokenizer=None, words_tokenizer=None):
        if isinstance(source, Doc):
            text = source.text
            sents = source.sents
            words = tuple(word.text for word in source)
        elif isinstance(source, str):
            text = source
            sents = extract_sents(text, tokenizer=sents_tokenizer)
            words = tuple(extract_words(text, tokenizer=words_tokenizer, use_lexemes=False))
        else:
            raise TypeError("Некорректный источник данных")
        if not text:
            raise ValueError("Анализируемый текст пуст")
        
        chars_per_word = tuple(len(word) for word in words)
        syllables_per_word = tuple(count_syllables(word) for word in words)
        self.c_chars = dict(sorted(Counter(chars_per_word).items()))
        self.c_syllables = dict(sorted(Counter(syllables_per_word).items()))
        self.n_sents = sum(1 for sent in sents)
        self.n_words = len(words)
        self.n_unique_words = len({word.lower() for word in words})
        self.n_long_words = sum(1 for cpw in chars_per_word if cpw >= 6)
        self.n_complex_words = sum(1 for spw in syllables_per_word if spw >= COMPLEX_SYL_FACTOR)
        self.n_simple_words = sum(1 for spw in syllables_per_word if COMPLEX_SYL_FACTOR > spw > 0)
        self.n_monosyllable_words = self.c_syllables.get(1, 0)
        self.n_polysyllable_words = self.n_words - self.c_syllables.get(1, 0) - self.c_syllables.get(0, 0)
        self.n_chars = len(text.replace('\n', ''))
        self.n_letters = sum((1 for char in text if char in RU_LETTERS))
        self.n_spaces = sum((1 for char in text if char in SPACES))
        self.n_syllables = sum(syllables_per_word)
        
    def get_stats(self):
        """
        Получение вычисленных статистик текста

        Вывод:
            dict[str, int]: Справочник вычисленных статистик текста
        """
        return {
            'n_sents': self.n_sents,
            'n_words': self.n_words,
            'c_chars': self.c_chars,
            'c_syllables': self.c_syllables,
            'n_unique_words': self.n_unique_words,
            'n_long_words': self.n_long_words,
            'n_complex_words': self.n_complex_words,
            'n_simple_words': self.n_simple_words,
            'n_monosyllable_words': self.n_monosyllable_words,
            'n_polysyllable_words': self.n_polysyllable_words,
            'n_chars': self.n_chars,
            'n_letters': self.n_letters,
            'n_spaces': self.n_spaces,
            'n_syllables': self.n_syllables
        }

    def print_stats(self):
        """Отображение вычисленных статистик текста с описанием на экран"""        
        print(f"{'Статистика':^20}|{'Значение':^10}")
        print("-" * 30)
        for stat, value in BASIC_STATS_DESC.items():
            print(f"{value:20}|{self.get_stats().get(stat):^10}")


if __name__ == "__main__":
    from pprint import pprint
    import re
    text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
    bs = BasicStats(text, words_tokenizer=re.compile(r'[^\w]+'))
    pprint(bs.get_stats())
    bs.print_stats()