from operator import methodcaller
from unicodedata import category as cat

from .table import Key, Table
from .code.wals import language_to_wals_code
from .data.loader import ExcelLoader


def all_but_language(lang):
    return language_to_wals_code.keys() - lang


def delete_titles_from_non_greek(table):
    table.rm(lang=all_but_language("ANCIENT_GREEK"), vers=0)


def increment_greek_vers(table):
    def increment_vers(key):
        kd = key.asdict()
        kd["vers"] += 1
        return Key(**kd)

    table.remap(increment_vers, lang=["ANCIENT_GREEK"])


def remove_versicle_number_in_non_greek(table):
    # MAKE IT FASTER
    def remove_versicle_number(vers):
        return " ".join(vers.split()[1:])

    table.apply(remove_versicle_number, lang=all_but_language("ANCIENT_GREEK"))


def remove_spaces_from_start_and_end(table):
    table.apply(lambda x: x.strip())


def ensure_versicles_end_with_punctuation(table):
    def put_punctuation_at_end(vers):
        vers += "" if cat(vers[-1]).startswith("P") else "."
        return vers

    table.apply(put_punctuation_at_end)
    # return table.map(put_punctuation_at_end)


def ensure_versicles_are_str(table):
    table.filter(lambda x: not isinstance(x, str))


def nchapter_nverse(table, lang):
    ch = 0
    vr = 0
    for cl, v in table.cl2v.items():
        if cl[1] == lang:
            ch += 1
            vr += len(v)
    return ch, vr


def main():
    pass
