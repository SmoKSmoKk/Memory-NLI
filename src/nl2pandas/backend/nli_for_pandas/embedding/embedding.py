from abc import ABC, abstractmethod
from typing import List

from numpy import ndarray


class Embedding(ABC):
    """
    Abstract class for different embeddings, e.g. BERT, GloVe, positional encoding.
    """

    @abstractmethod
    def embed(self, sentences: List[str]) -> ndarray:
        """
        Calculates the embedding for each passed sentence/command.

        :param sentences: the list of commands we want to calculate the embedding for

        :return: the embedding for each sentence
        """
        raise NotImplementedError
