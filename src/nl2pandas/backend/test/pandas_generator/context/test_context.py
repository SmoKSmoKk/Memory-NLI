import unittest

import IPython
import pandas as pd
import pytest
from IPython.core.interactiveshell import InteractiveShell
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner


class TestContext(unittest.TestCase):
    def setUp(self) -> None:
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
        self.refiner = Refiner(self.context)

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

    def test_update_context(self):
        # test context on one cell
        self.assertEqual(self.context.active_dataframe, '')

        self.context.update_context(self.shell)
        self.assertEqual(self.context.active_dataframe, 'df4')

        # add new dataframe and update context
        self.shell.run_cell("df3 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['index', 'df3_2', 'df3_3', 'df3_4'])",
                            store_history=True
                            )
        self.assertEqual([key for key in self.context.dataframes.keys()], ['df1', 'df2', 'df4'])
        self.assertEqual(self.context._active_dataframe, 'df4')

        self.context.update_context(self.shell)

        self.assertEqual([key for key in self.context.dataframes.keys()], ['df1', 'df2', 'df3', 'df4'])
        self.assertEqual(self.context.active_dataframe, 'df3')
        self.assertEqual([column for column in self.context.active_df_columns],
                         ['index', 'df3_2', 'df3_3', 'df3_4', 'None'])

        # test active df setter
        self.context.active_dataframe = 'df1'
        self.assertEqual(self.context.active_dataframe, 'df1')
        self.assertEqual([key for key in self.context.active_df_columns], ['id', 'B', 'C', 'D', 'None'])
        self.assertEqual([key for key in self.context.active_df_indices], [0, 1, 2, 'None'])

    def test_set_refinement(self):
        refiner = Refiner(self.context)
        self.context.set_refiner(refiner)
        self.assertEqual(self.context.refiner, refiner)

    def test_is_column_name(self):
        self.context.update_context(self.shell)
        result, df = self.context.is_column_name('df2_2')

        self.assertEqual(result, True)
        self.assertEqual(df, ['df2'])

        result, df = self.context.is_column_name('fhkaö')

        self.assertEqual(result, False)
        self.assertEqual(df, [])

    def test_is_index(self):
        self.context.update_context(self.shell)
        result, df = self.context.is_index(0)

        self.assertEqual(result, True)
        self.assertEqual(df, ['df1', 'df2', 'df4'])

        result, df = self.context.is_index('fhkaö')

        self.assertEqual(result, False)
        self.assertEqual(df, [])

        result, df = self.context.is_index(8)

        self.assertEqual(result, True)
        self.assertEqual(df, ['df4'])

    def test_validate_active_df_change_df(self):
        self.context.update_context(self.shell)
        self.context.active_dataframe = 'df1'

        self.context.validate_active_df('df2_2')
        self.assertEqual(self.context.active_dataframe, 'df2')

    def test_validate_active_df_no_change(self):
        self.context.update_context(self.shell)
        self.context.active_dataframe = 'df1'

        self.context.validate_active_df('nlsdanl')
        self.assertEqual(self.context.active_dataframe, 'df1')

        self.context.validate_active_df('B')
        self.assertEqual(self.context.active_dataframe, 'df1')

    def test_validate_active_df_list_change(self):
        self.context.update_context(self.shell)
        self.context.active_dataframe = 'df1'

        self.context.validate_active_df(['df2_2', 'df2_3'])
        self.assertEqual(self.context.active_dataframe, 'df2')

        self.context.validate_active_df([0, 4])
        self.assertEqual(self.context.active_dataframe, 'df4')

    def test_validate_active_df_list_no_change(self):
        self.context.update_context(self.shell)
        self.context.active_dataframe = 'df1'

        self.context.validate_active_df(['B', 'C'])
        self.assertEqual(self.context.active_dataframe, 'df1')

        self.context.validate_active_df(['fjöla', 'äselgä'])
        self.assertEqual(self.context.active_dataframe, 'df1')

        self.context.validate_active_df([1, 2])
        self.assertEqual(self.context.active_dataframe, 'df1')

        self.context.validate_active_df([99, 33])
        self.assertEqual(self.context.active_dataframe, 'df1')

    def test_get_cell_df(self):

        new_shell = IPython.InteractiveShell().get_ipython()

        new_shell.run_cell(
            "import pandas as pd\nimport numpy as np\ndf8 = pd.DataFrame(np.arange(12).reshape(3, 4), "
            "columns=['id', 'B', 'C', 'D'])", store_history=True
        )

        new_shell.run_cell(
            "df2 = pd.DataFrame(np.arange(12).reshape(3, 4), "
            "columns=['index', 'df2_2', 'df2_3', 'df2_4'])",
            store_history=True
        )

        new_shell.run_cell("val = 'B'", store_history=True)
        new_context = Context(new_shell)
        new_context.update_context(new_shell)
        dfs = ['df2', 'df8']
        cells = ['_i1', '_i2', '_i3']
        cell_df = {'_i1': ['df8'], '_i2': ['df2']}
        df_cells = new_context.get_cell_df(dfs, cells)
        self.assertEqual(df_cells, cell_df)

    @pytest.mark.xfail()
    def test_validate_function(self):
        self.context.update_context(self.shell)

        success, warning = self.context.validate_function("df1 = df1.drop(axis='columns')")
        self.assertEqual(success, False)
        self.assertTrue(type(warning), ValueError)
        self.assertEqual(str(warning), "Need to specify at least one of 'labels', 'index' or 'columns'")

        success, warning = self.context.validate_function("df1 = df1.drop(labels='B', axis='columns')")
        self.assertEqual(success, True)
        self.assertEqual(warning, None)


if __name__ == '__main__':
    unittest.main()
