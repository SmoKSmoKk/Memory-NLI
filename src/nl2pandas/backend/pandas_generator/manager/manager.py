import inspect
import operator
from typing import Any, Callable, Dict, List, SupportsFloat, Union, cast

from nl2pandas.backend.nli_for_pandas.entity_abstraction.combiner import Combiner
from nl2pandas.backend.nli_for_pandas.pipeline import Pipeline
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.definitions import (  # noqa: E402
    CLASSIFIER_PATH,
    DATABASE_PATH,
)
from nl2pandas.backend.pandas_generator.memory.memory import Database
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner
from nl2pandas.backend.pandas_generator.translator.translator import Translator


class PandasManager:
    """
    This class acts as an entry point to the pandas_generator backend. From here, one can access the
    semantic parser, and the translation and code generation process.

    :param context: an instance of Context class with the IPython environment
    """
    def __init__(self, context: Context):
        self.context = context
        self.pandas_translator = Translator()
        self.pipeline = Pipeline()
        self.pipeline.load_classifier(CLASSIFIER_PATH)
        self.combiner = Combiner()

    def validate_entity_sequence(self,
                                 programs: List[Dict]) -> List[Dict]:
        """
        Checks if the pandas function requires a column parameter, and validates that the given column
        name matches a column name of the active dataframe.

        :param programs: the programs suggested by the nl pipeline
        :return: the validated programs
        """
        for program in programs:

            if "ON COLUMN" in program['general_action']:

                # first entity is the column name
                entities: Dict = {'numbers': [],
                                  'values': [],
                                  'number_lists': [],
                                  'string_lists': [],
                                  'conditions': []
                                  }

                is_column_name, df = self.context.is_column_name(program['entities']['<value0>'])
                if not is_column_name:
                    for param in program['entities']:
                        is_column_name, df = self.context.is_column_name(program['entities'][param])
                        if param.startswith('<value'):
                            if is_column_name:
                                entities['values'].insert(0, program['entities'][param])
                            else:
                                entities['values'].append(program['entities'][param])
                        elif param.startswith('<string_list'):
                            entities['string_lists'].append(program['entities'][param])
                        elif param.startswith('<number_list'):
                            entities['number_lists'].append(program['entities'][param])
                        elif param.startswith('<number'):
                            entities['numbers'].append(program['entities'][param])
                        elif param.startswith('<conditions'):
                            entities['conditions'].append(program['entities'][param])

                    grounded_action, lifted_action, ordered_entities = self.combiner.recombine(
                        action=program['general_action'],
                        entities=entities
                    )
                    program['grounded_action'] = grounded_action
                    program['lifted_action'] = lifted_action
                    program['entities'] = ordered_entities
        return programs

    def get_documentation(self, pandas_func: Callable) -> str:
        """
        Returns the documentation of a given callable object.
        :param pandas_func: the Pandas function to document

        :return: string containing the documentation
        """
        doc = inspect.getdoc(pandas_func)

        if doc is None:
            doc = 'missing documentation'

        return doc

    def get_translation(
            self,
            programs: List[Dict[str, Union[str, SupportsFloat, Dict[str, Union[str, float, List]]]]],
            utterance: str
    ) -> List[Dict[str, Any]]:
        """
        Matches the general action of the given program to the Pandas method in the Translator.

        :param programs: a list of dictionaries holding the program info as returned by the NLI pipeline. Requires the
        keys 'general_action' and 'entities'
        :param utterance: the natural language utterance
        """

        programs_info = []

        for program in programs:
            # get the corresponding pandas functions
            assert isinstance(program['general_action'], str)
            assert isinstance(program['entities'], dict)
            pandas_translation = self.pandas_translator.get_pandas_func(
                dsl_action=program['general_action'],
                entities=program['entities']
            )

            # add additional info
            probability = cast(float, program['probability'])
            pandas_translation['probability'] = round(float(probability)*100, 2)

            pandas_translation['grounded_action'] = program['grounded_action']
            pandas_translation['nl_utterance'] = utterance

            pandas_translation['documentation'] = self.get_documentation(pandas_translation['class_callable'])

            programs_info.append(pandas_translation)

        return programs_info

    def get_programs(self, utterance: str) -> List[Dict]:
        """
        Utilizes the natural language interface pipeline to retrieve the dsl programs

        :param utterance: the natural language utterance
        :return: a list of dictionary holding relevant pandas and dsl information for the dsl programs
        """
        # get programs
        programs = self.pipeline.get_programs(utterance)[:4]

        try:
            list(map(operator.itemgetter('grounded_action'), programs)).index('NOT_SURE')
            return [{'grounded_action': 'NOT_SURE'}]
        except ValueError:
            pass

        # validate column entity sequence
        programs = self.validate_entity_sequence(programs)
        # get matching pandas method
        programs_info = self.get_translation(programs=programs, utterance=utterance)

        return programs_info

    def get_refiner(self, selected_program: Dict) -> Refiner:
        """
        Sets up the refiner instance for a specific pandas function

        :param selected_program: the dictionary holding the dsl and general pandas
        info of the selected program

        :return: the refiner instance
        """
        pandas_refiner = Refiner(self.context)

        pandas_refiner.set_refiner(selected_program)

        return pandas_refiner

    def get_past_actions(self, refiner: Refiner, file: str = DATABASE_PATH) -> Dict:
        """
        loads the database with past actions and filters out non relevant suggestions

        :param refiner: the active refiner instance
        :param file: path to database

        :return: dictionary of past actions relevant to the current pandas method
        """
        db = Database(file=file)

        # get past actions of parameters existing in the current selected pandas function
        past_actions = {}
        for param in refiner.refined_kwargs:
            action = db.load(param)
            if action and action != refiner.refined_kwargs[param]:
                past_actions[param] = action

        for param in refiner.scope:
            action = db.load(param)
            if action and action != refiner.scope[param]:
                past_actions[param] = action

        # check if dataframe dependent parameters present
        for param in past_actions.copy():
            if param in refiner.df_dependencies:
                is_column, dfs = self.context.is_column_name(past_actions[param])
                is_index, dfs = self.context.is_index(past_actions[param])
                if not is_index and not is_column:
                    past_actions.pop(param)

        return past_actions

    def set_past_actions(self, actions: Dict, file: str = DATABASE_PATH) -> None:
        """
        saves the parameter values set during the refining process.

        :param actions: the dictionary of parameter and value pairs to save
        :param file: path to the database
        """
        db = Database(file=file)

        db.save(actions)

    def reset_past_action_database(self, file: str = DATABASE_PATH) -> None:
        """
        Resets the database

        :param file: path to the database
        """

        db = Database(file=file)
        db.reset()
