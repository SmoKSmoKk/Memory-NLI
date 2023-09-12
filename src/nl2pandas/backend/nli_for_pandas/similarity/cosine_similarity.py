import numpy as np
from nl2pandas.backend.nli_for_pandas.similarity.similarity import Similarity
from numpy import ndarray


class CosineSimilarity(Similarity):
    """
    This class contains a function for calculating the cosine similarity.
    """

    def calculate(self, vector1: ndarray, vector2: ndarray) -> float:
        """
        Calculates the cosine similarity between two vectors (tensors).

        :param vector1: first vector
        :param vector2: second vector

        :return: cosine similarity as a float.
        """
        return np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
