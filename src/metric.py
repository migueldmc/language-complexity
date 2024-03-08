from abc import ABC, abstractmethod
import algorithm as algo

class Metric(ABC):
    def __init__(self, compress, encoding, degradation_percent, rng, transforms=None):
        self.compress = compress
        self.encoding = encoding
        self.dpercent = degradation_percent
        self.randomob = rng
        self.transforms = transforms

    @abstractmethod
    def _compute(self, text, original_compressed_size):
        pass

    def encode(self, text):
        return text.encode(self.encoding)

    def compute(self, text, original_compressed_size=None):
        if original_compressed_size is None:
            original_compressed_size = len(self.compress(self.encode(text)))
        return self._compute(text, original_compressed_size)
            
class MetricDelVerses(Metric):
    def _compute(self, text, original_compressed_size):
        verses = text.split('\n')
        dtext = remove_random_verses(verses, p=self.dpercent, rng=self.randomob)
        dcompressed = self.compress(dtext.encode(self.encoding))
        return len(dcompressed) / original_compressed_size

class MetricDelWords(Metric):
    def _compute(self, text, original_compressed_size):                 
        dtext = remove_random_words(text, p=self.dpercent, rng=self.randomob)
        dcompressed = self.compress(dtext.encode(self.encoding))
        return len(dcompressed) / original_compressed_size


class MetricDelChars(Metric):
    def _compute(self, text, original_compressed_size):
        dtext = remove_random_chars(text, p=self.dpercent, rng=self.randomob)
        dcompressed = self.compress(dtext.encode(self.encoding))
        return len(dcompressed) / original_compressed_size
        

class MetricRepWords(Metric):
    def __init__(self):
        super().__init__()
        raise NotImplementedError

    def _compute(self, text, original_compressed_size):
        dtext = replace_word_for_index(text, tr=self.tr)
