from abc import ABC, abstractmethod

from degrader import AbstractDegrader
from compressor import Compressor


class Metric(ABC):
    def __init__(self, degrader: AbstractDegrader, compressor: Compressor):
        assert isinstance(degrader, AbstractDegrader)
        assert isinstance(compressor, Compressor)
        self.degrader = degrader
        self.compressor = compressor

    @abstractmethod
    def compute(self, text: str) -> float:
        pass


class TransversalDegradation(Metric):
    def compute(self, text: str) -> float:
        dtext = self.degrader.degrade(text)
        D = len(self.compressor.compress(dtext))
        O = len(self.compressor.compress(text))
        m = D / O
        return m


class LexicalSubstitution(Metric):
    def compute(self, text: str) -> float:
        dtext = self.degrader.degrade(text)
        R = len(self.compressor.compress(text))
        C = len(self.compressor.compress(dtext))
        m = R / C
        return m


class DegradeCompress(Metric):
    def compute(self, text: str) -> float:
        dtext = self.degrader.degrade(text)
        dctext = self.compressor.compress(dtext)
        m = len(dctext)
        return m
