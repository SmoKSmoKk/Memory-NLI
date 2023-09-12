import unittest

from nl2pandas.backend.nli_for_pandas.entity_abstraction.entity_abstraction import (
    EntityAbstraction,
)


class TestEntityAbstraction(unittest.TestCase):
    def setUp(self) -> None:
        self.abstraction = EntityAbstraction()

    def test_lift_values(self):
        input_utterance = """search for 'quote' and "this quote as well" """
        expected_utterance = """search for <value> and <value> """
        expected_entities = ["quote", "this quote as well"]

        lifted_utterance, entities = self.abstraction.lift_values(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_multiple_values(self):
        input_utterance = """search for 'value1' and 'value2'"""
        expected_utterance = """search for <value> and <value>"""
        expected_entities = ["value1", "value2"]

        lifted_utterance, entities = self.abstraction.lift_values(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_string_lists(self):
        input_utterance = 'set column titles "longitude", "latitude", "population"'
        expected_utterance = "set column titles <string_list>"
        expected_entities = ['"longitude", "latitude", "population"']

        lifted_utterance, entities = self.abstraction.lift_string_lists(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_numbers(self):
        input_utterance = "delete row 0 and replace -1 with -0.99"
        expected_utterance = "delete row <number> and replace <number> with <number>"
        expected_entities = ["0", "-1", "-0.99"]

        lifted_utterance, entities = self.abstraction.lift_numbers(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_numbers_list(self):
        input_utterance = "delete rows 0, 1, 33, 4"
        expected_utterance = "delete rows <number_list>"
        expected_entities = ['0, 1, 33, 4']

        lifted_utterance, entities = self.abstraction.lift_number_lists(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_conditions(self):
        input_utterance = """Filter rows where "population" < 5000000 and ID != 7721"""
        expected_utterance = """Filter rows where "population" <condition> and ID <condition>"""
        expected_entities = ["< 5000000", "!= 7721"]

        lifted_utterance, entities = self.abstraction.lift_conditions(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_entities(self):
        input_utterance = (
            "Drop column 'this' and 'that' and set column titles to 'title1', 'title2', 'title3' "
            "filter out row 0, 1, 2 and find all columns with 'value' <= 1.65 and replace nans with 0.0"
        )
        expected_utterance = (
            "Drop column <value> and <value> and set column titles to <string_list> "
            "filter out row <number_list> and find all columns with <value> <condition> and replace nans with <number>"
        )
        expected_entities = {
            "numbers": ["0.0"],
            "values": ["this", "that", "value"],
            "number_lists": ['0, 1, 2'],
            "string_lists": ["'title1', 'title2', 'title3'"],
            "conditions": ["<= 1.65"],
        }

        lifted_utterance, entities = self.abstraction.lift_entities(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_lift_entities_complex(self):
        input_utterance = (
            'set column titles to "this", "that";filter for "date">2020-03-01 drop rows 0. '

        )
        expected_utterance = (
            'set column titles to <string_list>;filter for <value><condition> drop rows <number>. '
        )
        expected_entities = {
            "numbers": ["0"],
            "values": ["date"],
            "number_lists": [],
            "string_lists": ['"this", "that"'],
            "conditions": [">2020-03-01"],
        }

        lifted_utterance, entities = self.abstraction.lift_entities(input_utterance)
        self.assertEqual(expected_utterance, lifted_utterance)
        self.assertEqual(expected_entities, entities)

    def test_replace_entities(self):
        input_action = 'DELETE COLUMNS "column1", "column2";SELECT ROWS 0, 1, 2, 3; DELETE ROWS WHERE "column3" == 0'
        input_entities = {
            "numbers": [],
            "values": ["column3"],
            "number_lists": ['0, 1, 2, 3'],
            "string_lists": ['"column1", "column2"'],
            "conditions": ["== 0"],
        }
        expected_lifted_action = (
            'DELETE COLUMNS <string_list>;SELECT ROWS <number_list>; DELETE ROWS WHERE <value> <condition>'
        )
        lifted_action = self.abstraction.replace_entities(input_action, input_entities)
        self.assertEqual(expected_lifted_action, lifted_action)
