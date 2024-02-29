import logging

from gzip import compress as gzip_compress
from bz2 import compress as bz2_compress
from random import Random
from functools import partial
from itertools import product
from pathlib import Path

import pandas as pd

from algorithm import (
    remove_random_verses,
    remove_random_words,
    remove_random_chars,
    build_word_transliterator,
    replace_word_for_index,
    replace_index_for_word,
)

from data.util import sort_values, by_field

# TODO get from command line
PATH = "../dataset/bibles.csv"
DF = sort_values(pd.read_csv(PATH))
ENCODING = "utf-16"
SEED = 42
PERCENT = 10
RUNS = 5

RNG = Random(SEED)
TR = build_word_transliterator('\n'.join(DF['text']), rng=RNG)
logging.warning('Transliterator built')


#TODO: Add option to LCM, 90%, or FULL

# TODO: EACH FUNCTION RECEIVES A DATASET DEAL WITH IT

metric_ids = {
    "del-verses": partial(remove_random_verses, p=PERCENT / 100, rng=RNG),
    "del-words": partial(remove_random_words, p=PERCENT / 100, rng=RNG),
    "del-chars": partial(remove_random_chars, p=PERCENT / 100, rng=RNG),
    "rep-words": partial(replace_word_for_index, tr=TR),
}

compression_algorithms = {
    "gzip": partial(gzip_compress, compresslevel=9),
    "bz2": partial(bz2_compress, compresslevel=9),
}


def compute_complexity(metric_id, compression_algorithm, text, pcomp):
    metric = metric_ids[metric_id]
    compress = compression_algorithms[compression_algorithm]

    bs = metric(text).encode(ENCODING)
    return len(compress(bs)) / pcomp


def build_experiment_name(dirname):
    fname = "complexity_%s_%d_%d_%d" % (ENCODING, SEED, PERCENT, RUNS)
    return dirname + +".csv"


def language_statistics(df):
    results = dict(
        language=[],
        compression_algorithm=[],
        size_bytes=[],
    )
    languages = df["language"].unique()
    for lang, algo in product(languages, compression_algorithms):
        logging.warning('language_statistics %20s %20s' % (lang, algo))
        results["language"].append(lang)
        results["compression_algorithm"].append(algo)
        compress = compression_algorithms[algo]
        bs = "\n".join(df[df["language"] == lang]["text"]).encode(ENCODING)
        results["size_bytes"].append(len(compress(bs)))
    return pd.DataFrame(results)


def experiments(lcomp):
    results = dict(
        metric_id=[],
        language=[],
        compression_algorithm=[],
        complexity=[],
        experiment_run_id=[],
    )

    by_languages = by_field(DF, "language")


    it = product(metric_ids, by_languages, compression_algorithms, range(RUNS))
    for metric_id, language, compression_algorithm, run in it:
        logging.warning('%20s %20s %20s %10d' % (metric_id, language, compression_algorithm, run))
        results["metric_id"].append(metric_id)
        results["language"].append(language)
        results["compression_algorithm"].append(compression_algorithm)
        results["experiment_run_id"].append(run)

        text = by_language[language]
        pcomp = lcomp[(lcomp.language == language) & (lcomp.compression_algorithm == compression_algorithm)]["size_bytes"].item()
        complexity = compute_complexity(metric_id, compression_algorithm, text, pcomp)

        results["complexity"].append(complexity)

    return pd.DataFrame(results)


if __name__ == "__main__":

    lcomp_fname = Path("../results/language_statistics.csv")
    if lcomp_fname.exists():
        lcomp = pd.read_csv(lcomp_fname)
    else:
        lcomp = language_statistics(DF)
        lcomp.to_csv(lcomp_fname, index=False)
    
    results = experiments(lcomp)
    fname = build_experiment_name("../results/language_complexity")
    results.to_csv(fname, index=False)
