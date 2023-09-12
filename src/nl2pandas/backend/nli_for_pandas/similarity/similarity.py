from abc import ABC, abstractmethod

from numpy import ndarray


class Similarity(ABC):
    """
    Abstract class for different similarity measures.
    """

    @abstractmethod
    def calculate(self, vector1: ndarray, vector2: ndarray) -> float:
        """
        Calculates the similarity between two vectors.

        :param vector1: first vector
        :param vector2: second vector

        :return: similarity as a float.
        """
        raise NotImplementedError
