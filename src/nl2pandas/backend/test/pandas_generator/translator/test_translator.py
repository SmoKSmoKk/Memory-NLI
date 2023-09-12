import unittest

import pandas as pd
from IPython.core.interactiveshell import InteractiveShell
from nl2pandas.backend.pandas_generator.translator.translator import Translator


class TestTranslator(unittest.TestCase):
    def setUp(self) -> None:
        self.shell = InteractiveShell.instance()
        self.translator = Translator()

    def test_get_pandas_func(self):
        dsl_action = 'ON COLUMN <value> REPLACE <value> WITH <value>'
        entities = {'<value0>': 'col1', '<value1>': ',', '<value2>': '.'}

        expected = {
            "general_pandas_function": "str.replace",
            "class_callable": pd.Series.str.replace,
            "kwargs": {'pat': ',', 'repl': '.'},
            "type": "pandas.Series",
            "parameter_specifications": {
                    'n': {'dtype': 'number'},
                    'regex': {'dtype': 'bool'},
                    'case': {'dtype': 'bool'},
                    'flags': {'dtype': 'number'}
            },
            "scope_options": ['subset_col'],
            "scope": {'subset_col': {'value': 'col1'}}
        }

        program = self.translator.get_pandas_func(dsl_action, entities)

        self.assertEqual(program, expected)


if __name__ == '__main__':
    unittest.main()
