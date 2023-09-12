import unittest

import pandas as pd
from IPython.core.interactiveshell import InteractiveShell
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.definitions import TEST_DATABASE_PATH
from nl2pandas.backend.pandas_generator.manager.manager import PandasManager


class TestPandasManager(unittest.TestCase):
    def setUp(self) -> None:
        self.shell = InteractiveShell.instance().get_ipython()
        self.shell.run_cell("import pandas as pd\nimport numpy as np\n"
                            "df = pd.DataFrame(np.arange(12).reshape(3, 4), columns=['id', 'B', 'C', 'A'])",
                            store_history=True
                            )
        self.shell.run_cell("df2 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['index', 'df2_2', 'df2_3', 'df2_4'])",
                            store_history=True
                            )

        self.context = Context(self.shell)

        self.context.update_context(self.shell)
        self.manager = PandasManager(self.context)

    def test_validate_entity_sequence(self):
        programs = [{'training_utterance': 'strip <value> from column <value>',
                     'grounded_action': 'ON COLUMN "(m)" STRIP "B"',
                     'lifted_action': 'ON COLUMN <value0> STRIP <value1>',
                     'general_action': 'ON COLUMN <value> STRIP <value>',
                     'entities': {'<value0>': '(m)', '<value1>': 'B'}, 'probability': '0.638777'},
                    {'training_utterance': 'change the column name <value> to <value>',
                     'grounded_action': 'RENAME "(m)" TO "B"',
                     'lifted_action': 'RENAME <value0> TO <value1>',
                     'general_action': 'RENAME <value> TO <value>',
                     'entities': {'<value0>': '(m)', '<value1>': 'B'},
                     'probability': '0.59650594'}]

        programs = self.manager.validate_entity_sequence(programs)
        self.assertEqual(programs[0]['general_action'], "ON COLUMN <value> STRIP <value>")
        self.assertEqual(programs[0]['entities']['<value0>'], 'B')
        self.assertEqual(programs[0]['entities']['<value1>'], '(m)')
        self.assertEqual(programs[1]['entities']['<value0>'], '(m)')
        self.assertEqual(programs[1]['entities']['<value1>'], 'B')

    def test_get_programs(self):
        programs = self.manager.get_programs("strip '(m)' from column 'A' ")

        self.assertEqual(programs[0]['kwargs'], {'to_strip': '(m)'})

        doc = programs[0]['documentation'].rsplit("\n")[0]

        self.assertEqual(doc, "Remove leading and trailing characters.")
        self.assertEqual(programs[0]['scope_options'], ['subset_col'])

    def test_get_translation(self):
        programs = self.manager.pipeline.get_programs("strip '(m)' from column 'A' ")[:4]
        programs = self.manager.validate_entity_sequence(programs)
        translation = self.manager.get_translation(programs, "strip '(m)' from column 'A' ")

        self.assertEqual(translation[0]['general_pandas_function'], "str.strip")
        self.assertEqual(translation[0]['kwargs'], {'to_strip': '(m)'})  # not yet validated
        self.assertEqual(translation[0]['scope'], {'subset_col': {'value': 'A'}})
        self.assertTrue(translation[0]['probability'] > 90)
        self.assertEqual(translation[0]['grounded_action'], 'ON COLUMN "A" STRIP "(m)"')
        self.assertEqual(translation[0]['nl_utterance'], "strip '(m)' from column 'A' ")

    def test_get_documentation(self):
        doc = self.manager.get_documentation(pd.Series.str.strip)
        self.assertEqual(doc.rsplit("\n")[0], "Remove leading and trailing characters.")

    def test_get_refiner(self):
        programs = self.manager.get_programs("strip '(m)' from column 'A' ")
        refiner = self.manager.get_refiner(programs[0])

        self.assertEqual(refiner.kwargs, {'to_strip': '(m)'})
        self.assertEqual(refiner.parameters['to_strip']['value'], None)
        self.assertEqual(refiner.parameters['to_strip']['selection'], 'text')
        self.assertEqual(refiner.refined_kwargs, {'to_strip': '(m)'})

    def test_set_and_get_past_actions(self):
        file = "./test_past_actions.sqlite3"
        programs = self.manager.get_programs("strip '(m)' from column 'A' ")
        refiner = self.manager.get_refiner(programs[0])

        self.manager.set_past_actions({'to_strip': 'that'}, file=file)
        actions = self.manager.get_past_actions(refiner, file=file)
        self.assertTrue('to_strip' in actions)

    def test_reset_past_actions(self):
        file = TEST_DATABASE_PATH
        programs = self.manager.get_programs("strip '(m)' from column 'A' ")
        refiner = self.manager.get_refiner(programs[0])

        self.manager.reset_past_action_database(file=file)
        actions = self.manager.get_past_actions(refiner, file=file)
        self.assertEqual(actions, {})


if __name__ == '__main__':
    unittest.main()
