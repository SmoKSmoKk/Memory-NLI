import collections
from typing import Dict, List, Tuple, Union


class Combiner:
    """
    This class recombines a lifted action with the corresponding entities (ranges, quotes).
    """

    def __init__(self):
        self.entity_types = ["number", "value", "number_list", "string_list", "condition"]

    def recombine(
            self, action: str, entities: Dict[str, List[str]]
    ) -> Tuple[str, str, Dict[str, Union[str, float, List]]]:
        """
        Recombines the passed action with the correct entities.

        :param action: lifted action string, e.g. read <number>
        :param entities: list of lifted entities

        :return: grounded action string
        """

        # count number of replaced entities in lifted action
        num_lifted = sum(
            [action.count(f"<{entity_type}>") for entity_type in self.entity_types]
        )
        # count number of entities in entity set
        num_entities = sum(
            [len(entities[f"{entity_type}s"]) for entity_type in self.entity_types]
        )

        action_entities = [entity_type for entity_type in self.entity_types if f"<{entity_type}>" in action]
        entity_entities = [entity_type for entity_type in self.entity_types if len(entities[f"{entity_type}s"]) != 0]

        # check whether number of entities fits lifted placeholders
        # (modified by Sonasha Auer Wilkins)
        # check instead if the entities contained in both the actions and entities are the same
        if num_lifted == num_entities and collections.Counter(action_entities) == collections.Counter(entity_entities):

            grounded_action = action
            lifted_action = action
            ordered_entities: Dict[str, Union[str, float, List]] = {}

            for (
                    entity_type
            ) in self.entity_types:  # replace entities for the different entity types
                for i, entity in enumerate(entities[f"{entity_type}s"]):
                    # add quotation marks if entity type equals value
                    qm = ""
                    if entity_type == "value":
                        qm = '"'

                    grounded_action = grounded_action.replace(
                        f"<{entity_type}>",
                        qm + entity + qm,
                        1,  # only replace first occurrence
                    )
                    lifted_action = lifted_action.replace(
                        f"<{entity_type}>", f"<{entity_type}{i}>", 1
                    )

                    # added by Sonasha Auer Wilkins
                    if entity_type == "number":
                        num: float
                        try:
                            num = int(entity)
                        except ValueError:
                            num = float(entity)
                        ordered_entities[f"<{entity_type}{i}>"] = num

                    elif entity_type == "number_list":
                        num_list: List
                        try:
                            num_list = [int(val) for val in entity.split(',')]
                        except ValueError:
                            num_list = [float(val) for val in entity.split(',')]
                        ordered_entities[f"<{entity_type}{i}>"] = num_list

                    elif entity_type == "string_list":
                        string_list: List
                        entity = entity.replace("'", '"')  # convert to double quote
                        entity = entity.replace('"', '')  # remove double quotes
                        string_list = [val for val in entity.split(', ')]
                        ordered_entities[f"<{entity_type}{i}>"] = string_list
                    else:
                        ordered_entities[f"<{entity_type}{i}>"] = entity

            return grounded_action, lifted_action, ordered_entities
        else:
            raise Exception("Number of entities does not match lifted placeholders.")
