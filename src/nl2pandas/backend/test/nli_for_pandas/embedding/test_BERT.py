import unittest

import numpy as np
from nl2pandas.backend.nli_for_pandas.embedding.BERT import BERT


class TestBERTEmbedding(unittest.TestCase):
    def setUp(self):
        self.bert = BERT()

    def test_embed(self):
        sentences = ["test"]
        embeddings = self.bert.embed(sentences)

        assert embeddings is not None
        assert embeddings[0] is not None
        assert len(embeddings[0]) == 768
        assert np.isclose(-0.001961784, np.mean(embeddings[0]))  # -0.005733443
