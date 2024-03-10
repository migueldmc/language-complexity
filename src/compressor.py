import gzip
import bz2

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Compressor:
    def __init__(self, name, encoding, function, **fkwargs):
        self.name = name
        self.encoding = encoding
        self.function = function
        self.fkwargs = fkwargs

    def compress(self, text: str) -> bytes:
        return self.function(text.encode(self.encoding), **self.fkwargs)
