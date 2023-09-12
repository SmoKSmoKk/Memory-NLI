import re
from typing import Dict, List, Tuple

"""
This file was modefied by Sonasha Auer Wilkins to fit the Pandas domain
"""
# removed comma, originally r"(\"([^\v,;\'\"]+?)\"|\'([^\v,;\'\"]+?)\')"

quote_regex = r"(\"([^\v;\"]+?)\"|\'([^\v;\']+?)\')"

value_regex = rf"{quote_regex}(?!,)"

string_list_regex = rf"({quote_regex})(, {quote_regex})+"

digit_regex = r"(([-+]?[.]?\b\d+[/.]?\d*)\b)"

number_regex = rf"{digit_regex}(?!,)"

number_list_regex = rf"({digit_regex})(, {digit_regex})+"

condition_regex = (
    r"([<>=!]+[ ]?(\"([^\v,;\'\"]+?)\""
    r"|\'([^\v,;\'\"]+?)\')+)"
    r"|(?!(<number>|<value>|<string_list>|<number_list>|<condition>|><condition>))"
    r"([<>=!]+"
    r"(?<!<number>)(?<!<value>)(?<!<string_list>)(?<!<number_list>)(?<!<condition>)"
    r"[ ]?[^\s]+)"
)


class EntityAbstraction:
    def __init__(self):
        """
        This class provides the means to replace entities such as numbers, conditions, names or values
        from the input utterances.
        """
        self.value_matcher = re.compile(value_regex)
        self.string_list_matcher = re.compile(string_list_regex)
        self.number_matcher = re.compile(number_regex)
        self.number_list_matcher = re.compile(number_list_regex)
        self.condition_matcher = re.compile(condition_regex)

    def lift_values(self, utterance: str) -> Tuple[str, List[str]]:
        """
        Lifts quote entities from input utterance e.g. for search in quotes: search for "test"

        :param utterance: natural language utterance to be lifted

        :return: tuple of lifted utterance and list of value entities
        """
        entities = []

        matched_quotes = self.value_matcher.finditer(utterance)
        for q in matched_quotes:
            value = q.group().strip("'").strip('"')  # remove " & ' quotation marks
            entities.append(value)
            utterance = utterance.replace(q.group(), "<value>")

        return utterance, entities

    def lift_string_lists(self, utterance: str) -> Tuple[str, List[str]]:
        """
        Lifts lists of string from input utterance, e.g. for multiple column titles

        :param utterance: natural language utterance to be lifted

        :return: tuple of lifted utterance and list oft string-list entities
        """
        entities = []

        matched_lists = self.string_list_matcher.finditer(utterance)
        for match in matched_lists:
            string_list = match.group()
            entities.append(string_list)
            utterance = utterance.replace(match.group(), "<string_list>")

        return utterance, entities

    def lift_numbers(self, utterance: str) -> Tuple[str, List[str]]:
        """
        Lifts number entities from input utterance

        :param utterance: natural language utterance to be lifted

        :return: tuple of lifted utterance and list of number entities
        """

        entities = []

        matched_numbers = self.number_matcher.finditer(utterance)
        for match in matched_numbers:
            number = match.group()
            entities.append(number)
        utterance = re.sub(number_regex, "<number>", utterance)

        return utterance, entities

    def lift_number_lists(self, utterance: str) -> Tuple[str, List[str]]:
        """
       Lifts lists of numbers from input utterance

       :param utterance: natural language utterance to be lifted

       :return: tuple of lifted utterance and list of number entities
       """

        entities = []

        matched_lists = self.number_list_matcher.finditer(utterance)
        for match in matched_lists:
            number_list = match.group()
            entities.append(number_list)
            utterance = utterance.replace(match.group(), "<number_list>")

        return utterance, entities

    def lift_conditions(self, utterance: str) -> Tuple[str, List[str]]:
        """
        Lifts condition entities from the input utterance

        :param utterance: natural language utterance to be lifted

        :return: tuple of lifted utterance and list of condition entities
        """
        entities = []
        # ignore = ['><condition>', '<condition>', ]
        matched_conditions = self.condition_matcher.finditer(utterance)
        for match in matched_conditions:
            condition = match.group()
            entities.append(condition)
            utterance = utterance.replace(match.group(), "<condition>")

        return utterance, entities

    def lift_entities(self, utterance: str) -> Tuple[str, Dict[str, List]]:
        """
        Lifts/abstracts entities from utterance and returns the lifted utterance as well as a list of abstracted
        entities.

        :param utterance: natural language utterance to be lifted

        :return: Tuple of lifted utterance and dictionary containing the entities
        """
        lifted_utterance = utterance
        lifted_utterance, condition_entities = self.lift_conditions(lifted_utterance)
        lifted_utterance, list_of_string_entities = self.lift_string_lists(
            lifted_utterance
        )
        lifted_utterance, list_of_number_entities = self.lift_number_lists(lifted_utterance)
        lifted_utterance, value_entities = self.lift_values(lifted_utterance)
        lifted_utterance, number_entities = self.lift_numbers(lifted_utterance)

        entity_dict = {
            "numbers": number_entities,
            "values": value_entities,
            "number_lists": list_of_number_entities,
            "string_lists": list_of_string_entities,
            "conditions": condition_entities,
        }

        return lifted_utterance, entity_dict

    def replace_entities(self, action: str, entities: Dict[str, List]) -> str:
        """
        Replaces the passed entities in a given action string.

        :param action: action string
        :param entities: dict of entities containing a list of "ranges" and "values" entities

        :return: action string with replaced entities
        """
        for elem in entities["numbers"]:
            action = action.replace(elem, "<number>")
        for elem in entities["values"]:
            action = action.replace(f'"{elem}"', "<value>")
        for elem in entities["number_lists"]:
            action = action.replace(elem, "<number_list>")
        for elem in entities["string_lists"]:
            action = action.replace(elem, "<string_list>")
        for elem in entities["conditions"]:
            action = action.replace(elem, "<condition>")

        return action
