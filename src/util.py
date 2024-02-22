from operator import methodcaller
from unicodedata import category as cat

from .table import Key, Table
from .code.wals import language_to_wals_code
from .data.loader import ExcelLoader


def all_but_language(lang):
    return language_to_wals_code.keys() - set([lang])


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

    data = {
        k: (v if k.lang == "ANCIENT_GREEK" else remove_versicle_number(v))
        for k, v in table
    }
    table.build(data)


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


def fix_versicle_order(table):
    from subprocess import Popen, PIPE, STDOUT
    from collections import defaultdict
    import re

    e = "[(](\d+)\s*-\s*(\d+)[)]"

    def versicles_out_of_order(table):
        d = list()
        g = dict()
        a = dict()

        for key, val in table():
            for i, match in enumerate(re.finditer(e, val)):
                if i == 0:
                    g[key] = []
                if i > 0:
                    a[(key, nkey)] = val[: match.start(0)]
                    # m = re.match(b, match.group(0))
                chap = re.sub(".\d+", "." + match.group(1), key.chap)
                vers = int(match.group(2))
                nkey = Key(key.book, chap, key.lang, vers)
                d.append((key, nkey))
                g[key].append(nkey)
                a[(key, nkey)] = val[match.start(0) :]

        return d, g, a

    def nodify(key):
        return repr(key).replace(" ", "")

    def encode(d):
        return "\n".join(" ".join(nodify(i) for i in t) for t in d).encode("utf-8")

    def tsort(inp):
        p = Popen(["tsort"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        tsort_stdout, tsort_stderr = p.communicate(input=inp)
        if tsort_stderr:
            raise RuntimeError(tsort_stderr)
        return tsort_stdout

    def decode(b):
        lines = [eval(line) for line in b.decode("utf-8").split("\n") if line]
        return lines

    d, g, a = versicles_out_of_order(table)
    r = decode(tsort(encode(d)))
    # Build new _data
    # return d, g, a, r
    data = {k: v for k, v in table}
    marked = set()
    for key in reversed(r):
        if key not in g:
            if key in data:
                marked.add(key)
            continue

        for nkey in g[key]:
            if nkey in marked:
                data[nkey] = data[nkey] + a[(key, nkey)]
                marked.remove(nkey)
                marked.add(key)
                continue
            data[nkey] = a[(key, nkey)]

    data = {
        k: re.sub(" *" + e + " *", "", v) for k, v in data.items() if k not in marked
    }
    table.build(data)
    return table


def apply_fixes(table):
    print("deleting titles from non greek")
    delete_titles_from_non_greek(table)
    print("incrementing greek verses")
    increment_greek_vers(table)
    print("ensuring versicles are strings")
    ensure_versicles_are_str(table)
    print("removing spaces from start and end")
    remove_spaces_from_start_and_end(table)
    print("ensuring versicles end with punctuation")
    ensure_versicles_end_with_punctuation(table)
    print("removing versicle number in non greek")
    remove_versicle_number_in_non_greek(table)
    print("fixing versicle order")
    fix_versicle_order(table)

    return table


def main():
    pass
