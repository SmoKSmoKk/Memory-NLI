import os
import unittest

from nl2pandas.backend.nli_for_pandas.data.data import Data, get_full_path


class MyTestCase(unittest.TestCase):
    def test_data_init_file(self):
        data = Data(file="./data/atomic_actions.csv")
        self.assertEqual("delete row <number>", data.utterances[0])
        self.assertEqual("DELETE ROW <number>", data.actions[0])

    def test_data_init_string(self):
        data = Data(
            csv_string="""
test,TEST"""
        )
        self.assertEqual("test", data.utterances[0])
        self.assertEqual("TEST", data.actions[0])

    def test_data_save_to(self):
        Data(
            csv_string="""
test,TEST"""
        ).save_to("./data/test_actions.csv")
        data = Data(file="./data/test_actions.csv")
        self.assertEqual("test", data.utterances[0])
        self.assertEqual("TEST", data.actions[0])

    def tearDown(self):
        if os.path.exists(get_full_path("./data/test_actions.csv")):
            os.remove(get_full_path("./data/test_actions.csv"))
