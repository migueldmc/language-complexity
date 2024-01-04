from nltk.tokenize import word_tokenize
from unicodedata import category as cat

def is_punct(text):
    return text and (cat(text[0]).startswith('P'))
    
def tokens(text):
    return word_tokenize(text)

def types(tokens):
    return set(tokens)
