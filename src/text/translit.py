import re
from collections import Counter

fst = int("0x13000", 0)
lst = int("0x1342e", 0) + 1
hmp = [chr(i) for i in range(fst, lst)]


def transliterate(text, table):
    ret = "".join([table[t] for t in text])
    return ret


class Transliterator:
    def __init__(self, cnt):
        self.cnt = cnt
        self.encode_table, self.decode_table = self._build_encode_decode_tables(cnt)

    def _build_encode_decode_tables(self, cnt):
        byfreq = sorted([(c, n) for c, n in cnt.items()], key=lambda x: x[1])
        encode_table = {c: hmp[i] for i, (c, n) in enumerate(byfreq)}
        decode_table = {h: c for c, h in encode_table.items()}
        return encode_table, decode_table

    def encode(self, tokens):
        ret = [transliterate(s, self.encode_table) for s in tokens]
        return ret

    def decode(self, tokens):
        ret = [transliterate(s, self.decode_table) for s in tokens]
        return ret

    def __repr__(self):
        return f"Transliterator({self.cnt!r})"
