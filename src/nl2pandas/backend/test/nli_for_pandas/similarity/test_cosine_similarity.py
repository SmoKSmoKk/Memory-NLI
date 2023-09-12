import unittest

import numpy as np
from nl2pandas.backend.nli_for_pandas.similarity.cosine_similarity import (
    CosineSimilarity,
)


class TestCosineSimilarity(unittest.TestCase):
    def setUp(self):
        self.cosine_similarity = CosineSimilarity()

    def test_calculate(self):
        vec1 = np.array([1, 1])
        vec2 = np.array([1, -1])
        assert np.isclose(self.cosine_similarity.calculate(vec1, vec2), 0)
        assert np.isclose(self.cosine_similarity.calculate(vec1, vec1), 1)


if __name__ == '__main__':
    unittest.main()
