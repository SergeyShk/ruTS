import pymorphy2
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from ruts.constants import PUNCTUATION, RU_VOWELS
from typing import Pattern

def extract_sents(text, tokenizer=None):
    """
    Извлечение предложений из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (func|Pattern): Токенизатор или регулярное выражение

    Вывод:
        sents (gen[str]): Генератор извлеченных предложений
    """
    if not tokenizer:
        sents = sent_tokenize(text)
    elif isinstance(tokenizer, Pattern):
        sents = re.split(tokenizer, text)
    else:
        sents = tokenizer(text)

    for sent in sents:
        yield sent        

def extract_words(
    text,
    tokenizer=None,
    filter_punct=True,
    filter_nums=False,
    use_lexemes=False
):
    """
    Извлечение слов из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (func|Pattern): Токенизатор или регулярное выражение
        filter_punct (bool): Фильтрация знаков препинания
        filter_nums (bool): Фильтрация чисел
        use_lexemes (bool): Использовать леммы слов

    Вывод:
        words (gen[str]): Генератор извлеченных слов
    """
    if not tokenizer:
        words = (word for word in word_tokenize(text))
    elif isinstance(tokenizer, Pattern):
        words = (word for word in re.split(tokenizer, text))
    else:
        words = (word for word in tokenizer(text))
    if filter_punct:
        words = (word for word in words if word not in PUNCTUATION)
    if filter_nums:
        words = (word for word in words if not word.isnumeric())
    if use_lexemes:
        morph = pymorphy2.MorphAnalyzer()
        words = (morph.parse(word)[0].normal_form for word in words)
    
    for word in words:
        yield word

def count_syllables(word):
    """
    Вычисление количества слогов в слове

    Аргументы:
        word (str): Строка слова

    Вывод:
        int: Количество слогов
    """    
    return sum((1 for char in word if char in RU_VOWELS))


if __name__ == "__main__":
    text = """
    Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений словарного состава языка или какого-либо его сегмента;
    тематический, или идеографический способ упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями является выход
    в сферу лексических значений, установление связей не только между значениями и выражающими их словами, а также между самими значениями (регистрация различных
    семантических отношений внутри словаря).
    """
    import re
    from nltk.tokenize import wordpunct_tokenize
    pattern = re.compile(r'[^\w]+')
    print(list(extract_words(text, tokenizer=pattern)))
    print(list(extract_words(text)))
    print(list(extract_words(text, tokenizer=wordpunct_tokenize)))