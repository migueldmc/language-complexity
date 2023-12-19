from collections import defaultdict
from dataclasses import dataclass, asdict
from itertools import product
from pathlib import Path

import pandas as pd


class ExcelLoader:
    def __init__(self, *path):
        _path = []
        _srcs = []
        _data = []
        for p in path:
            p = Path(p)
            s, d = self._load(p)
            _path.append(p)
            _srcs.append(s)
            _data.append(d)

        self.path = tuple(_path)
        self.srcs = tuple(_srcs)
        self.data = tuple(_data)

    def __repr__(self):
        return f"ExcelLoader({self.path!r})"

    def _load(self, path):
        dirfiles = (
            [path] if path.is_file() else [e for e in path.iterdir() if e.is_file()]
        )
        excels = [
            {k: v.to_dict() for k, v in pd.read_excel(e, None).items()}
            for e in dirfiles
        ]
        return dirfiles, excels

    def load(self):
        if hasattr(self, "data"):
            return self.srcs, self.data


# class Key(NamedTuple):
@dataclass(frozen=True, order=True)
class Key:
    book: str
    chap: str
    lang: str
    vers: str

    def asdict(self):
        return asdict(self)


class Table:
    def __init__(self, loader: ExcelLoader, languages: dict[str, str]):
        self.loader = loader
        self.langs = languages
        self._build()

    def __repr__(self):
        return f"Table({self.loader!r}, {self.langs!r})"

    def _build(self):
        book_srcs, chapter_srcs = self.loader.load()
        _data = defaultdict(str)
        for books, chapters in zip(book_srcs, chapter_srcs):
            structures = self._build_structures(books, chapters)
            _data |= self._build_data(*structures)

        self._build_query_fields(_data)

    def _build_structures(self, books, chapters):
        _books = [book.name.replace(".xlsx", "") for book in books]
        _book2chaps = {b: c for (b, c) in zip(_books, chapters)}
        _chap2langs = {
            chap: lang
            for book, chapters in _book2chaps.items()
            for chap, lang in chapters.items()
        }
        # _chap2langs = {c : v.to_dict() for b, chs in self._book2chaps.items() for c, v in chs.items()}
        return _books, _book2chaps, _chap2langs

    def _build_query_fields(self, data):

        # TODO: Use functional dependencies to improve search
        self._data = data
        self._books = set()
        self._chaps = set()
        self._langs = set()
        self._verss = set()
        for key in data.keys():
            self._books.add(key.book)
            self._chaps.add(key.chap)
            self._langs.add(key.lang)
            self._verss.add(key.vers)

    def _build_data(self, books, book2chaps, chap2langs):
        _data = defaultdict(str)
        for book in books:
            for chap in book2chaps[book]:
                for lang, verses in chap2langs[chap].items():
                    for idx, vers in verses.items():
                        key = Key(book=book, chap=chap, lang=lang, vers=idx)
                        if vers != " " and vers:
                            _data[key] = vers
        return _data

    def __call__(self, **kwargs):
        return self.iterfix(**kwargs)

    def iterfix(self, **kwargs):
        args = set(["book", "chap", "lang", "vers"])
        if not (kwargs.keys() & args):
            raise ValueError(f"iterfix args should be in {args!r}")

        default = dict(
            book=self._books, chap=self._chaps, lang=self._langs, vers=self._verss
        )
        inp = kwargs.keys()
        var = args - inp

        for entry in inp:
            val = kwargs[entry]
            try:
                kwargs[entry] = list(val)
            except TypeError:
                kwargs[entry] = [kwargs[entry]]

        for varying in product(*[default[v] for v in var]):
            for fixed in product(*[kwargs[v] for v in inp]):
                keyargs = dict()
                for vatt, v in zip(var, varying):
                    keyargs[vatt] = v
                for fatt, f in zip(inp, fixed):
                    keyargs[fatt] = f

                key = Key(**keyargs)
                val = self._data[key]
                if val:
                    yield key, val

    def rm(self, **kwargs):
        rmlist = [key for key, _ in self.iterfix(**kwargs)]
        for key in rmlist:
            del self._data[key]

    def map(self, func, **kwargs):
        for key, val in self.iterfix(**kwargs):
            yield key, func(val)

    def remap(self, func, **kwargs):
        _keysvals = [(key, val) for key, val in self.iterfix(**kwargs)]
        _new_data = {func(key): val for key, val in _keysvals}
        _old_keys = set([key for key, _ in _keysvals])
        _to_be_rm = _old_keys - _new_data.keys()

        for key in _to_be_rm:
            del self._data[key]
        self._data.update(_new_data)
        self._build_query_fields(self._data)

    def apply(self, func, **kwargs):
        newentries = [(key, func(val)) for key, val in self.iterfix(**kwargs)]
        for key, nval in newentries:
            self._data[key] = nval
