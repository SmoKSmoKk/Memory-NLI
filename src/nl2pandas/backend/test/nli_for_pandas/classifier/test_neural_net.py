import unittest

import numpy as np
from nl2pandas.backend.nli_for_pandas.classifier.neural_net import NeuralNet


class TestNeuralNet(unittest.TestCase):
    def setUp(self):
        self.neural_net = NeuralNet()
        self.input = np.array([0])
        self.target = np.array([1])

    def test_train(self):
        history = self.neural_net.train(self.input, self.target, epochs=1)
        self.assertIsNotNone(history)

    def test_predict(self):
        prediction = self.neural_net.predict([1])
        self.assertTrue(0 <= prediction <= 1)
