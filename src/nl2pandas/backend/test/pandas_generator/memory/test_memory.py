import unittest

from nl2pandas.backend.pandas_generator.definitions import TEST_DATABASE_PATH
from nl2pandas.backend.pandas_generator.memory.memory import Database


class TestMemory(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database(file=TEST_DATABASE_PATH)

    def test_save(self):
        self.db.save({'potato': 'soup', 'tomato': 'ketchup'})

        self.assertTrue(self.db.load('potato') is not None)

    def test_load(self):
        self.db.save({'potato': 'soup', 'tomato': 'ketchup'})
        value = self.db.load('potato')
        self.assertEqual(value, 'soup')

    def test_delete(self):
        self.db.save({'potato': 'soup', 'tomato': 'ketchup'})
        self.db.delete('tomato')
        self.assertIsNone(self.db.load('tomato'))

    # def test_reset(self):
    #     self.db.save({'potato': 'soup', 'tomato': 'ketchup'})
    #     self.db.reset()
    #     self.assertIsNone(self.db.load('potato'))
    #     self.assertIsNone(self.db.load('tomato'))


if __name__ == '__main__':
    unittest.main()
