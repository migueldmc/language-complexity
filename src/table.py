from collections import defaultdict

# from dataclasses import dataclass, asdict
from itertools import product
from typing import NamedTuple
from .data.loader import ExcelLoader


# @dataclass(frozen=True, order=True)
class Key(NamedTuple):
    book: str
    chap: str
    lang: str
    vers: str

    def asdict(self):
        return {k: v for k, v in zip(["book", "chap", "lang", "vers"], self)}


class Table:
    # TODO:
    # Make this datastructure functional
    # So calling methods produces another table
    def __init__(self, loader: ExcelLoader, languages: dict[str, str]):
        self.loader = loader
        self.langs = languages

    def build(self, data=None):
        _data = data or self._build()
        self._build_query_fields(_data)

    def __repr__(self):
        return f"Table({self.loader!r}, {self.langs!r})"

    def _build(self):
        book_srcs, chapter_srcs = self.loader.load()
        _data = dict()
        for books, chapters in zip(book_srcs, chapter_srcs):
            structures = self._build_structures(books, chapters)
            _data |= self._build_data(*structures)

        return _data

    def _build_structures(self, books, chapters):
        _books = [book.name.replace(".xlsx", "") for book in books]
        _book2chaps = {b: c for (b, c) in zip(_books, chapters)}
        _chap2langs = {
            chap: lang
            for book, chapters in _book2chaps.items()
            for chap, lang in chapters.items()
        }

        return _books, _book2chaps, _chap2langs

    def _build_query_fields(self, data):

        # TODO: Use functional dependencies to improve search
        self._data = data
        self._books = set()
        self._chaps = set()
        self._langs = set()
        self._verss = set()
        self.b2c = defaultdict(set)
        self.cl2v = defaultdict(set)
        for key in data.keys():
            self._books.add(key.book)
            self._chaps.add(key.chap)
            self._langs.add(key.lang)
            self._verss.add(key.vers)
            self.b2c[key.book].add(key.chap)
            self.cl2v[(key.chap, key.lang)].add(key.vers)

    def _build_data(self, books, book2chaps, chap2langs):
        _data = dict()
        for book in books:
            for chap in book2chaps[book]:
                for lang, verses in chap2langs[chap].items():
                    if lang not in self.langs.keys():
                        continue
                    for idx, vers in verses.items():
                        key = Key(book=book, chap=chap, lang=lang, vers=idx)
                        if vers != " " and vers:
                            _data[key] = vers
        return _data

    def __call__(self, **kwargs):
        return self.iterfix(**kwargs)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._fastiteration()

    def _fastiteration(self):
        for k, v in self._data.items():
            yield k, v

    def _slowiteration(self, **kwargs):
        args = set(["book", "chap", "lang", "vers"])
        if not (kwargs.keys() & args) and (kwargs.keys()):
            raise ValueError(f"{list(kwargs.keys() - args)!r} not in {args!r}")

        default = dict(
            book=self._books, chap=self._chaps, lang=self._langs, vers=self._verss
        )
        inp = kwargs.keys()
        var = args - inp

        for entry in inp:
            val = kwargs[entry]
            if isinstance(val, (str, int)):
                kwargs[entry] = [val]

        for varying in product(*[default[v] for v in var]):
            for fixed in product(*[kwargs[v] for v in inp]):
                keyargs = dict()
                for vatt, v in zip(var, varying):
                    keyargs[vatt] = v
                for fatt, f in zip(inp, fixed):
                    keyargs[fatt] = f

                key = Key(**keyargs)
                val = self._data.get(key, None)
                if val:
                    yield key, val

    def iterfix(self, **kwargs):
        return self._slowiteration(**kwargs) if kwargs else self._fastiteration()

    def rm(self, **kwargs):
        rmlist = set([key for key, _ in self.iterfix(**kwargs)])

        _data = dict()
        for k, v in self._data.items():
            if k not in rmlist:
                _data[k] = v

        self._build_query_fields(_data)
        return rmlist, self

    def filter(self, func, **kwargs):
        # TODO: Check if there is a faster iteration method
        rmlist = set([key for key, val in self.iterfix(**kwargs) if func(val)])
        _data = dict()

        for k, v in self._data.items():
            if k not in rmlist:
                _data[k] = v

        self._build_query_fields(_data)
        return rmlist, self

    def map(self, func, **kwargs):
        for key, val in self.iterfix(**kwargs):
            yield key, func(val)

    def remap(self, func, **kwargs):
        _keysvals = [(key, val) for key, val in self.iterfix(**kwargs)]
        _new_data = dict()
        for key, val in _keysvals:
            _new_data[func(key)] = val

        _old_keys = set([key for key, _ in _keysvals])
        _to_be_rm = _old_keys - _new_data.keys()

        _exclude_keys = _to_be_rm | _new_data.keys()
        # Build another dictionary and them update
        for key, val in self._data.items():
            if key not in _exclude_keys:
                _new_data[key] = val

        # self._data.update(_new_data)
        self._build_query_fields(_new_data)

    def apply(self, func, **kwargs):
        newentries = [(key, func(val)) for key, val in self.iterfix(**kwargs)]
        for key, nval in newentries:
            self._data[key] = nval

    def fetch_language_books(self, language, books):
        books = set(books)
        chaps = {
            (k.chap, k.vers): v
            for k, v in self._data.items()
            if k.book in books and k.lang == language
        }
        return chaps
