import unittest

from nl2pandas.backend.nli_for_pandas.entity_abstraction.combiner import Combiner


class TestCombiner(unittest.TestCase):
    def setUp(self) -> None:
        self.combiner = Combiner()

    def test_recombine_number(self):
        action = "DELETE ROW <number>"
        entities = {
            "numbers": ["0"],
            "values": [],
            "number_lists": [],
            "string_lists": [],
            "conditions": [],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual("DELETE ROW 0", grounded_action)
        self.assertEqual("DELETE ROW <number0>", lifted_action)
        self.assertIn("<number0>", ordered_entities)
        self.assertEqual(0, ordered_entities.get("<number0>"))

    def test_recombine_value(self):
        action = "SORT VALUES BY <value>"
        entities = {
            "numbers": [],
            "values": ["column name"],
            "number_lists": [],
            "string_lists": [],
            "conditions": [],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual('SORT VALUES BY "column name"', grounded_action)
        self.assertEqual("SORT VALUES BY <value0>", lifted_action)
        self.assertIn("<value0>", ordered_entities)
        self.assertEqual("column name", ordered_entities.get("<value0>"))

    def test_recombine_number_list(self):
        action = "REMOVE ROWS <number_list>"
        entities = {
            "numbers": [],
            "values": [],
            "number_lists": ['1, 2, 3, 4'],
            "string_lists": [],
            "conditions": [],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual("REMOVE ROWS 1, 2, 3, 4", grounded_action)
        self.assertEqual("REMOVE ROWS <number_list0>", lifted_action)
        self.assertIn("<number_list0>", ordered_entities)
        self.assertEqual([1, 2, 3, 4], ordered_entities.get("<number_list0>"))

    def test_recombine_string_list(self):
        action = "SET COLUMN NAMES <string_list>"
        entities = {
            "numbers": [],
            "values": [],
            "number_lists": [],
            "string_lists": ["'test1', 'test2'"],
            "conditions": [],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual("SET COLUMN NAMES 'test1', 'test2'", grounded_action)
        self.assertEqual("SET COLUMN NAMES <string_list0>", lifted_action)
        self.assertIn("<string_list0>", ordered_entities)
        self.assertEqual(['test1', 'test2'], ordered_entities.get("<string_list0>"))

    def test_recombine_condition_and_value(self):
        action = "SELECT ROWS WHERE <value> <condition>"
        entities = {
            "numbers": [],
            "values": ["ID"],
            "number_lists": [],
            "string_lists": [],
            "conditions": ["!= 1660"],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual('SELECT ROWS WHERE "ID" != 1660', grounded_action)
        self.assertEqual("SELECT ROWS WHERE <value0> <condition0>", lifted_action)
        self.assertIn("<condition0>", ordered_entities)
        self.assertIn("<value0>", ordered_entities)
        self.assertEqual("!= 1660", ordered_entities.get("<condition0>"))
        self.assertEqual("ID", ordered_entities.get("<value0>"))

    def test_recombine_number_and_value(self):
        action = "SELECT ROW <number> and SELECT COLUMN <value>"
        entities = {
            "numbers": ["5"],
            "values": ["ID"],
            "number_lists": [],
            "string_lists": [],
            "conditions": [],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual('SELECT ROW 5 and SELECT COLUMN "ID"', grounded_action)
        self.assertEqual("SELECT ROW <number0> and SELECT COLUMN <value0>", lifted_action)
        self.assertIn("<number0>", ordered_entities)
        self.assertEqual(5, ordered_entities.get("<number0>"))
        self.assertIn("<value0>", ordered_entities)
        self.assertEqual("ID", ordered_entities.get("<value0>"))

    def test_recombine_multiple(self):
        action = "RENAME <value> TO <value> "
        entities = {
            "numbers": [],
            "values": ["name", "state"],
            "number_lists": [],
            "string_lists": [],
            "conditions": [],
        }

        grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
            action, entities
        )
        self.assertEqual("""RENAME "name" TO "state" """, grounded_action)
        self.assertEqual("RENAME <value0> TO <value1> ", lifted_action)
        self.assertIn("<value0>", ordered_entities)
        self.assertEqual("name", ordered_entities.get("<value0>"))
        self.assertIn("<value1>", ordered_entities)
        self.assertEqual("state", ordered_entities.get("<value1>"))
