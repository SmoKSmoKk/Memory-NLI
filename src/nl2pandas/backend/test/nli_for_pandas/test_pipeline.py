import os
import shutil
import unittest

from nl2pandas.backend.nli_for_pandas.pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def test_add_utterance_no_lifting(self):
        self.pipeline.add_utterance("drop first row", "DELETE ROW 0")
        self.assertIn("drop first row", self.pipeline.data.utterances)
        self.assertIn("DELETE ROW <number>", self.pipeline.data.actions)

    def test_add_utterance_with_lifting(self):
        self.pipeline.add_utterance('drop row 0 and column "red pandas"', 'DELETE ROW 0;DELETE COLUMN "red pandas"')
        self.assertIn("drop row <number> and column <value>", self.pipeline.data.utterances)
        self.assertIn("DELETE ROW <number>;DELETE COLUMN <value>", self.pipeline.data.actions)

    def test_add_utterance_with_partial_lifting(self):
        self.pipeline.add_utterance('drop first row and column "red pandas"', 'DELETE ROW 0;DELETE COLUMN "red pandas"')
        self.assertIn("drop first row and column <value>", self.pipeline.data.utterances)
        self.assertIn("DELETE ROW 0;DELETE COLUMN <value>", self.pipeline.data.actions)

    def test_train(self):
        history = self.pipeline.train_classifier(epochs=10)
        self.assertIsNotNone(history)

    def test_get_probabilities(self):
        results = self.pipeline.get_probabilities("delete column <value>")
        self.assertIsNotNone(results)

    def test_get_program_not_sure(self):
        self.pipeline.train_classifier(epochs=20)
        programs = self.pipeline.get_programs("?")
        self.assertEqual(
            [
                {
                    "entities": {},
                    "general_action": "NOT_SURE",
                    "grounded_action": "NOT_SURE",
                    "lifted_action": "NOT_SURE",
                }
            ],
            programs,
        )

    def test_get_program_delete(self):
        self.pipeline.train_classifier(epochs=50)
        programs = self.pipeline.get_programs("delete column 'red pandas'")
        programs[0][
            "probability"
        ] = "0.0"  # dirty workaround, because exact probability is unknown
        self.assertIn(
            {
                "training_utterance": "delete column <value>",
                "grounded_action": 'DELETE COLUMN "red pandas"',
                "lifted_action": "DELETE COLUMN <value0>",
                "general_action": "DELETE COLUMN <value>",
                "entities": {"<value0>": 'red pandas'},
                "probability": "0.0",
            },
            programs,
        )

    def test_determine_and_set_certainty_threshold(self):
        threshold = self.pipeline.determine_and_set_certainty_threshold()
        self.assertEqual(self.pipeline.certainty_threshold, threshold)

    def test_save_classifier(self):
        self.pipeline.save_classifier("./models/test_classifier.model")
        assert os.path.exists("models/test_classifier.model")

    def test_load_classifier(self):
        self.pipeline.save_classifier(name="./models/test_classifier.model")
        model = self.pipeline.load_classifier(name="./models/test_classifier.model")
        self.assertIsNotNone(model)

    def tearDown(self) -> None:
        if os.path.isdir("models/test_classifier.model"):
            shutil.rmtree("models/test_classifier.model")
