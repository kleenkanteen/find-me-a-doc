<<<<<<< HEAD
import re

def remove_dots_and_commas(text: str):
    text = text.lower()
    punctuation_pattern = r'[.,]'

    text_without_punctuation = re.sub(punctuation_pattern, '', text)

    return text_without_punctuation
=======
>>>>>>> master
