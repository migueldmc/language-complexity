import argparse
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


def compute_complexity(metric, compression_algorithm, text, pcomp, encoding):
    bs = metric(text).encode(encoding)
    return len(compression_algorithm(bs)) / pcomp


def build_experiment_name(path, encoding, seed, percent, runs, basefilename):
    fname = "complexity_%s_%d_%d_%d_%s" % (encoding, seed, percent, runs, basefilename)
    return Path(path) / fname


def language_statistics(df, encoding, compression_algorithms):
    results = dict(
        language=[],
        compression_algorithm=[],
        size_bytes=[],
    )
    languages = df["language"].unique()
    for lang, algo in product(languages, compression_algorithms):
        logging.warning("language_statistics %20s %20s" % (lang, algo))
        results["language"].append(lang)
        results["compression_algorithm"].append(algo)
        compress = compression_algorithms[algo]
        bs = "\n".join(df[df["language"] == lang]["text"]).encode(encoding)
        results["size_bytes"].append(len(compress(bs)))
    return pd.DataFrame(results)


def experiments(df, lcomp, metric_ids, compression_algorithms, encoding, runs):
    results = dict(
        metric_id=[],
        language=[],
        compression_algorithm=[],
        complexity=[],
        experiment_run_id=[],
    )

    by_languages = by_field(df, "language")

    it = product(metric_ids, by_languages, compression_algorithms, range(runs))
    for metric_id, language, compression_algorithm, run in it:
        logging.warning(
            "%20s %20s %20s %10d" % (metric_id, language, compression_algorithm, run)
        )
        results["metric_id"].append(metric_id)
        results["language"].append(language)
        results["compression_algorithm"].append(compression_algorithm)
        results["experiment_run_id"].append(run)

        text = by_languages[language]
        pcomp = lcomp[
            (lcomp.language == language)
            & (lcomp.compression_algorithm == compression_algorithm)
        ]["size_bytes"].item()
        complexity = compute_complexity(
            metric_ids[metric_id],
            compression_algorithms[compression_algorithm],
            text,
            pcomp,
            encoding,
        )

        results["complexity"].append(complexity)

    return pd.DataFrame(results)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        type=Path,
        help="Should be a csv file with the following columns: book, chapter, language, verse_number, text",
    )
    parser.add_argument("encoding", choices=["utf-8", "utf-16", "utf-32", "ascii"])
    parser.add_argument(
        "percent",
        type=int,
        default=20,
        help="Degradation amount. In word deletion, for example, percent=20 means that 20% of the words will be deleted.",
    )
    parser.add_argument(
        "runs", type=int, default=5, help="How many times repeat each experiment"
    )
    parser.add_argument(
        "seed", type=int, default=42, help="Random seed used for the experiments"
    )
    parser.add_argument("output", type=Path, help="Where to save the results")
    args = parser.parse_args()
    return args


def main(args):
    rng = Random(args.seed)
    df = sort_values(pd.read_csv(args.filename))
    logging.warning("Creating Transliterator")
    tr = build_word_transliterator("\n".join(df["text"]), rng=rng)

    def df_to_str(df):
        return "\n".join(df.text)

    # TODO: Fix return
    # Every function should return a string
    def del_verses(df):
        verses = list(df.text)
        return remove_random_verses(verses, p=args.percent / 100, rng=rng)

    def del_words(df):
        text = df_to_str(df)
        return remove_random_words(text, p=args.percent / 100, rng=rng)

    def del_chars(df):
        text = df_to_str(df)
        return remove_random_chars(text, p=args.percent / 100, rng=rng)

    def rep_words(df):
        text = df_to_str(df)
        return replace_word_for_index(text, tr=tr)

    metric_ids = {
        "del-verses": del_verses,
        "del-words": del_words,
        "del-chars": del_chars,
        "rep-words": rep_words,
    }

    compression_algorithms = {
        "gzip": partial(gzip_compress, compresslevel=9),
        "bz2": partial(bz2_compress, compresslevel=9),
    }

    logging.warning("Computing language statistics")
    lcomp_fname = Path(args.output / "language_stats.csv")
    lcomp = (
        pd.read_csv(lcomp_fname)
        if lcomp_fname.exists()
        else language_statistics(df, args.encoding, compression_algorithms)
    )
    lcomp.to_csv(lcomp_fname, index=False)

    logging.warning("Computing experiments")
    results = experiments(
        df, lcomp, metric_ids, compression_algorithms, args.encoding, args.runs
    )
    fname = build_experiment_name(
        args.output,
        args.encoding,
        args.seed,
        args.percent,
        args.runs,
        args.filename.name,
    )
    results.to_csv(fname, index=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
