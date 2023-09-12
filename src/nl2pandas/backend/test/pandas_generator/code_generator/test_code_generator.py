import unittest

import pandas as pd
from IPython import InteractiveShell
from nl2pandas.backend.pandas_generator.code_generator.code_generator import (
    CodeGenerator,
)
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner


class TestCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.shell = InteractiveShell.instance()
        self.shell.run_cell("import pandas as pd\nimport numpy as np\n"
                            "df1 = pd.DataFrame(np.arange(12).reshape(3, 4), columns=['id', 'B', 'C', 'D'])",
                            store_history=True
                            )
        self.shell.run_cell("df2 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['index', 'df2_2', 'df2_3', 'df2_4'])",
                            store_history=True
                            )
        self.shell.run_cell("df4 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['index', 'df4_2', 'df4_3', 'df4_4'])\n"
                            "df4 = df4.set_index('index')",
                            store_history=True
                            )

        self.context = Context(self.shell)
        self.context.update_context(self.shell)
        self.refiner = Refiner(self.context)
        self.code_generator = CodeGenerator(self.refiner)

        self.program1 = {
            "general_action": 'SORT VALUES BY <value>',
            "general_pandas_function": "sort_values",
            "class_callable": pd.DataFrame.sort_values,
            "kwargs": {'by': 'id', 'axis': 'index', 'inplace': True},
            "type": "pandas.DataFrame",
            "parameter_specifications": {
                'by': {'dtype': 'DataFrame_axis_opposite'},
                'kind': {'selection': 'dropdown', 'options': ['quicksort', 'mergesort', 'heapsort', 'stable']},
                'na_position': {'selection': 'dropdown', 'options': ['first', 'last']}},
            "scope_options": [],
            "scope": {}
        }

        self.program2 = {
            "general_action": 'ON COLUMN <value> STRIP <value>',
            "general_pandas_function": "str.strip",
            "class_callable": pd.Series.str.strip,
            "kwargs": {'to_strip': '(m)'},
            "type": "pandas.Series",
            "parameter_specifications": {},
            "scope_options": ['subset_col'],
            "scope": {'subset_col': {'value': 'B'}}
        }

        self.program3 = {
            "general_action": "CONVERT <value> TO NUMERIC",
            "general_pandas_function": "to_numeric",
            "class_callable": pd.to_numeric,
            "kwargs": dict(arg='df["date"]'),
            "type": "general_pandas",
            "parameter_specifications": {
                'arg': {'dtype': 'multi_type'},
                'errors': {'selection': 'dropdown', 'options': ['raise', 'coerce', 'ignore']},
            },
            "scope_options": [],
            "scope": {}
        }

    def test_get_columns(self):
        self.context.active_dataframe = 'df1'
        self.refiner.set_refiner(self.program2)
        columns = self.code_generator._get_columns()
        self.assertEqual(columns, '["B"]')

        self.refiner.set_refiner(self.program1)
        columns = self.code_generator._get_columns()
        self.assertEqual(columns, '')

    def test_get_return_df_inplace(self):
        self.refiner.set_refiner(self.program1)

        # inplace true
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, '')

        # inplace false
        self.program1['kwargs']['inplace'] = False
        self.refiner.set_refiner(self.program1)
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, 'df1 = ')

        # inplace false but return df modefied
        self.refiner.return_df = 'blabl'
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, 'blabl = ')

    def test_get_return_df_no_inplace(self):
        self.context.active_dataframe = 'df4'
        self.refiner.set_refiner(self.program2)

        # has scope column
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, 'df1["B"] = ')

        # scope does not change when modified
        self.refiner.return_df = 'blabla'
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, 'blabla = ')

        # no return df
        self.refiner.return_df = ''
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, '')

        # general method
        self.refiner.set_refiner(self.program3)
        return_df = self.code_generator._get_return_df(self.code_generator._get_columns())
        self.assertEqual(return_df, 'result = ')

    def test_get_dataframe_code_string(self):
        self.refiner.set_refiner(self.program1)

        string = self.code_generator._get_dataframe_code_str('sort_values', "by='id', axis='index', inplace=True")
        expected = "df1.sort_values(by='id', axis='index', inplace=True)"
        self.assertEqual(string, expected)

        self.program1['kwargs']['inplace'] = False
        self.refiner.set_refiner(self.program1)
        string = self.code_generator._get_dataframe_code_str('sort_values', "by='id', axis='index'")
        expected = "df1 = df1.sort_values(by='id', axis='index')"
        self.assertEqual(string, expected)

    def test__get_series_code_str(self):
        kwargs = "to_strip='(m)'"
        self.refiner.set_refiner(self.program2)

        string = self.code_generator._get_dataframe_code_str('str.strip', "to_strip='(m)'")
        expected = f'df1["B"] = df1["B"].str.strip({kwargs})'
        self.assertEqual(string, expected)

        self.refiner.return_df = ''
        string = self.code_generator._get_dataframe_code_str('str.strip', "to_strip='(m)'")
        expected = f'df1["B"].str.strip({kwargs})'
        self.assertEqual(string, expected)

        self.refiner.return_df = 'jrös'
        string = self.code_generator._get_dataframe_code_str('str.strip', "to_strip='(m)'")
        expected = f'jrös = df1["B"].str.strip({kwargs})'
        self.assertEqual(string, expected)

    def test_get_general_pandas_code_str(self):
        kwargs = 'arg=df["date"]'
        self.refiner.set_refiner(self.program3)
        string = self.code_generator._get_general_pandas_code_str('to_numeric', 'arg=df["date"]')
        expected = f'result = pd.to_numeric({kwargs})'
        self.assertEqual(string, expected)

        self.refiner.return_df = ''
        string = self.code_generator._get_general_pandas_code_str('to_numeric', 'arg=df["date"]')
        expected = f'pd.to_numeric({kwargs})'
        self.assertEqual(string, expected)

    def test_get_function_string(self):
        self.refiner.set_refiner(self.program1)

        code = self.code_generator.get_function_string(**{'by': 'id', 'axis': 'index', 'inplace': True})
        expected = "df1.sort_values(by='id', axis='index', inplace=True)"
        self.assertEqual(code, expected)

        kwargs = "to_strip='(m)'"
        self.refiner.set_refiner(self.program2)
        code = self.code_generator.get_function_string(**{'to_strip': '(m)'})
        expected = f'df1["B"] = df1["B"].str.strip({kwargs})'
        self.assertEqual(code, expected)

        kwargs = 'arg=df["date"]'
        self.refiner.set_refiner(self.program3)
        code = self.code_generator.get_function_string(**dict(arg='df["date"]'))
        expected = f'result = pd.to_numeric({kwargs})'
        self.assertEqual(code, expected)


if __name__ == '__main__':
    unittest.main()
