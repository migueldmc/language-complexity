from abc import ABC, abstractmethod
from unicodedata import category as cat

from algorithm import Sampler, Shuffler, remove_join
from text.tokenizer import tokens, lines
from text.translit import Transliterator as Tr


class AbstractDegrader(ABC):
    @abstractmethod
    def degrade(self, text: str) -> str:
        pass


class RandomVerseRemover(AbstractDegrader, Sampler):
    def degrade(self, text: str) -> str:
        verses = lines(text)
        indexes = self.randomize(verses)
        degraded = remove_join(verses, set(indexes), "\n")
        return degraded


class RandomWordRemover(AbstractDegrader, Sampler):
    def degrade(self, text: str) -> str:
        words = tokens(text)
        indexes = self.randomize(words)
        degraded = remove_join(words, set(indexes), " ")
        return degraded


class RandomCharRemover(AbstractDegrader, Sampler):
    def degrade(self, text: str) -> str:
        notspaces = [i for i, c in enumerate(text) if not cat(c).startswith("Z")]
        indexes = self.randomize(notspaces)
        degraded = remove_join(text, set(indexes), "")
        return degraded


class RandomWordToIndex(AbstractDegrader, Shuffler):
    def degrade(self, text: str) -> str:
        words = tokens(text)
        tr = Tr.from_list(self.randomize(words))
        degraded = " ".join(
            map(lambda t: t[0] % t[1], zip([f"%010d"] * len(words), tr.encode(words)))
        )
        return degraded


class DoNothing(AbstractDegrader):
    def degrade(self, text: str) -> str:
        return text
