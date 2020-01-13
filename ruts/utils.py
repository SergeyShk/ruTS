from ruts.constants import RU_VOWELS

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
    text = "самооборона"
    print(count_syllables(text))
