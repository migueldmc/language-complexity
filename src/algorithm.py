from functools import partial
from operator import ne
from random import Random

from metric.util import apply_at_indexes, replace_at_indexes, map_at_indexes
from text.tokenizer import tokens

def remove_empty(seq):
    return filter(partial(ne, ''), seq)

def remove_random_verses(verses, p=0.2, seed=42):
    rng = Random(seed)
    n = len(verses)
    indexes = rng.sample(range(n), k=int(p*n))

    return list(remove_empty(replace_at_indexes(verses, indexes, '')))

def remove_random_words(text, p=0.2, seed=42):
    rng = Random(seed)
    words = tokens(text)
    n = len(words)
    indexes = rng.sample(range(n), k=int(p*n))

    return ' '.join(remove_empty(replace_at_indexes(words, indexes, '')))

#TODO: Avoiod removing spaces
def remove_random_chars(text, p=0.2, seed=42):
    rng = Random(seed)
    n = len(text)
    # change range for the list of the indices that aren't spaces
    indexes = rng.sample(range(n), k=int(p*n))

    return ''.join(remove_empty(replace_at_indexes(text, indexes, '')))

def remove_morphology(text):
    words = tokens(text)

    encode_table = None
    decode_table = None
    
    tr = Transliterator()
