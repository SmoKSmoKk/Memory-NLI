from typing import List

from nl2pandas.backend.nli_for_pandas.embedding.embedding import Embedding
from numpy import ndarray
from sentence_transformers import SentenceTransformer


class BERT(Embedding):
    """
    This class uses BERT as a base for calculating the sentence embedding.
    It can be used to find similar sentences.
    """

    def __init__(self, bert_model="paraphrase-TinyBERT-L6-v2"):  # paraphrase-albert-small-v2
        """
        :param bert_model: different BERT models possible, e.g. paraphrase-distilroberta-base-v1,
        bert-base-nli-mean-tokens, stsb-roberta-large, stsb-roberta-base, ...
        """
        self.model = SentenceTransformer(bert_model)

    def embed(self, sentences: List[str]) -> ndarray:
        """
        Calculates the embedding for each passed sentence/command.

        :param sentences: the list of commands we want to calculate the embedding for
        :return: the embedding for each sentence
        """
        embeddings = self.model.encode(sentences)
        return embeddings
