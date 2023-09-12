import unittest

import pandas as pd
from IPython.core.interactiveshell import InteractiveShell
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner


class TestRefiner(unittest.TestCase):
    def setUp(self) -> None:
        self.shell = InteractiveShell.instance().get_ipython()
        self.shell.run_cell("import pandas as pd\nimport numpy as np\n"
                            "df = pd.DataFrame(np.arange(12).reshape(3, 4), columns=['id', 'B', 'C', 'D'])",
                            store_history=True
                            )
        self.shell.run_cell("df2 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['index', 'df2_2', 'df2_3', 'df2_4'])",
                            store_history=True
                            )

        self.context = Context(self.shell)

        self.context.update_context(self.shell)

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

    def test_set_program(self):

        refined_kwargs = {'by': 'id', 'axis': 'index', 'ascending': True,
                          'inplace': True, 'kind': 'quicksort', 'na_position': 'last',
                          'ignore_index': False, 'key': None
                          }
        kwargs = {'by': 'id', 'inplace': True}

        self.refiner.set_refiner(self.program1)

        self.assertEqual(self.refiner.parameters['kind']['options'], ['quicksort', 'mergesort', 'heapsort', 'stable'])
        self.assertEqual(self.refiner.parameters['by']['dtype'], 'DataFrame_axis_opposite')
        self.assertEqual(self.refiner.refined_kwargs, refined_kwargs)
        self.assertEqual(self.refiner.kwargs, kwargs)
        self.assertEqual(self.refiner.axis, 'index')
        self.assertEqual(self.refiner.df_dependencies, ['by'])
        self.assertEqual(self.refiner.scope, {})
        self.assertEqual(self.refiner.executable_function, "df.sort_values(by='id', inplace=True)")
        self.assertEqual(self.context.active_dataframe, 'df')

    def test_update(self):
        self.shell.run_cell("df3 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['df3_1', 'df3_2', 'df3_3', 'df4_4'])",
                            store_history=True
                            )

        self.refiner.set_refiner(self.program1)

        self.context.update_context(self.shell)
        self.context.active_dataframe = 'df3'

        self.assertEqual([val for val in self.refiner.parameters['by']['options']],
                         ['df3_1', 'df3_2', 'df3_3', 'df4_4', 'None'])

    def test_update_df_dependencies(self):

        self.refiner.set_refiner(self.program1)

        self.assertEqual([val for val in self.refiner.parameters['by']['options']],
                         ['id', 'B', 'C', 'D', 'None'])

        self.shell.run_cell("df3 = pd.DataFrame(np.arange(12).reshape(3, 4), "
                            "columns=['df3_1', 'df3_2', 'df3_3', 'df4_4'])",
                            store_history=True
                            )
        self.context.update_context(self.shell)
        self.refiner.axis = 'index'

        self.context.active_dataframe = 'df3'

        self.assertEqual([val for val in self.refiner.parameters['by']['options']],
                         ['df3_1', 'df3_2', 'df3_3', 'df4_4', 'None'])

        self.refiner.axis = 'columns'

        self.assertEqual([val for val in self.refiner.parameters['by']['options']], [0, 1, 2, 'None'])

        self.program2['scope']["subset_col"]['value'] = 'df3_1'
        self.refiner.set_refiner(self.program2)

        self.assertEqual([val for val in self.refiner.scope['subset_col']['options']],
                         ['df3_1', 'df3_2', 'df3_3', 'df4_4', 'None'])

    def test_get_param_options(self):
        self.refiner.set_refiner(self.program1)

        parameters = dict(
            by=dict(value='B', dtype='DataFrame_axis_opposite', options=None, selection=None),
            inplace=dict(value=True, dtype='bool', options=None, selection=None)
        )

        new_parameters = self.refiner.get_param_options(parameters)

        self.assertEqual(new_parameters['by']['value'], 'B')
        self.assertEqual([val for val in new_parameters['by']['options']], ['id', 'B', 'C', 'D', 'None'])
        self.assertEqual(new_parameters['by']['selection'], 'dropdown')
        self.assertEqual(new_parameters['inplace']['dtype'], 'bool')
        self.assertEqual([val for val in new_parameters['inplace']['options']], ['True', 'False'])
        self.assertEqual(new_parameters['inplace']['selection'], 'dropdown')

    def test_get_function_parameters(self):
        self.refiner.set_refiner(self.program1)
        param_specs = {
            'by': {'dtype': 'DataFrame_axis_opposite'},
            'kind': {'selection': 'dropdown', 'options': ['quicksort', 'mergesort', 'heapsort', 'stable']},
            'na_position': {'selection': 'dropdown', 'options': ['first', 'last']}
        }

        parameters = self.refiner.get_function_parameters(pd.DataFrame.sort_values, param_specs)

        self.assertEqual([key for key in parameters['by'].keys()], ['value', 'dtype', 'options', 'selection'])
        self.assertEqual(parameters['by']['dtype'], 'DataFrame_axis_opposite')
        self.assertEqual([val for val in parameters['kind']['options']],
                         ['quicksort', 'mergesort', 'heapsort', 'stable'])

    def test_get_scope_options(self):
        self.refiner.set_refiner(self.program2)
        scope_options = ['subset_col']
        scope = {'subset_col': {'value': 'B'}}

        scope = self.refiner.get_scope_options(scope_options, scope)
        self.assertEqual([key for key in scope['subset_col'].keys()],
                         ['value', 'selection', 'dtype', 'options'])
        self.assertEqual([val for val in scope['subset_col']['options']],
                         [val for val in self.context.active_df_columns])
        self.assertEqual(scope['subset_col']['dtype'], 'DataFrame_columns')

        no_scope = self.refiner.get_scope_options([], {})

        self.assertEqual(no_scope, {})

    def test_get_scope_parameters(self):
        self.refiner.set_refiner(self.program1)
        param, scope_param = self.refiner.get_scope_parameters()

        self.assertIn('axis', scope_param.keys())
        self.assertNotIn('axis', param.keys())

    def test_refine_code(self):
        self.refiner.set_refiner(self.program1)

        new_kwargs = self.refiner.refined_kwargs
        new_kwargs['kind'] = 'heapsort'

        self.refiner.refined_kwargs = new_kwargs
        self.assertIn('kind', self.refiner.kwargs.keys())
        self.assertEqual(self.refiner.kwargs['kind'], 'heapsort')

    def test_get_function_string(self):
        self.refiner.set_refiner(self.program1)

        function = "df.sort_values(by='id', inplace=True)"
        kwargs = {'by': 'id', 'axis': 'index', 'inplace': True}

        self.refiner.code_generator.get_function_string(**kwargs)

        self.assertEqual(self.refiner.executable_function, function)

        kwargs['kind'] = 'heapsort'
        kwargs['inplace'] = False

        self.refiner.code_generator.get_function_string(**kwargs)


if __name__ == '__main__':
    unittest.main()
