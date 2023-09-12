import json
from typing import Any, Dict, List, Set, Union

import pandas as pd


class Translator:
    def __init__(self):
        """
        This class matches a given DSL to a Pandas method, and provides all the necessary information needed to
        generate pandas code and refine the method
        """

    def get_pandas_func(self, dsl_action: str, entities: Dict[str, Union[str, float, List]]) -> Dict[str, Any]:  # noqa: C901
        """
        Finds the pandas function corresponding to the given DSL action.
        Methods can be added by specifying the return dictionary:
            - general_action: the general DSL action
            - general_pandas_function: the name of the pandas function
            - class_callable: the callable Pandas method object
            - kwargs: the set key words of the function call
            - type: the type of the Pandas method. One of
                * pd.DataFrame
                * pd.Series
                * general_action
            - parameter_specifications: any special cases the refiner should mind during setup. Specifications for each
              parameter can be one of
                * 'dtype': the type of input
                    - DataFrame_axis if label is dependent on columns or index
                    - DataFrame_axis_opposite if label should be set to the opposite of the current axis
                    - DataFrame_columns if label is only dependent on columns
                    - DataFrame_index if label is only dependent on index
                * 'value': the value to set as a default
                * 'options': a list of options to select from
                * 'selection': type of selection this parameter should have in the refinement view. Default is set to
                  text, dropdown is automatically selected for boolean parameters that are not None by default. Options
                  include one of
                    - 'dropdown'
                    - 'dropdown_multi'
            - scope_options: the scope options for this method. One of
                - 'subset_col'
                - 'subset_index'
            - scope: the scope values that are set. The values have the same options as specified in the
              parameter_specifications. The keys can be one of:
                - 'subset_col'
                - 'subset_index'

        :param dsl_action: the DSL action
        :param entities: a dictionary of parameter keywords with their values set to the given entities
        :return: Dictionary with the pandas function, the string expression of the pandas function,
          a dictionary of all parameter options with their values and the set kwargs.

        structure example:
        {
            |  "general_action": 'DELETE COLUMN <value>',
            |  "general_pandas_function": "drop",
            |  "class_callable": pd.DataFrame.drop,
            |  "kwargs": {'labels':entities['<value0>'], axis: "columns"},
            |  "type": "pandas.DataFrame",
            |  "parameter_specifications": {
                    'labels': {'dtype': 'DataFrame_axis'},
                    'level': {'dtype': 'number'},
                    'axis': {'value': 'columns'}
                },
            |  "scope_options": [],
            |  "scope": {},
        }
        """
        kwargs: Dict[str, Any]

        if dsl_action == "CONVERT <value> TO DATETIME":
            kwargs = dict(arg=entities['<value0>'])
            return {
                "general_action": dsl_action,
                "general_pandas_function": "to_datetime",
                "class_callable": pd.to_datetime,
                "kwargs": kwargs,
                "type": "general_pandas",
                "parameter_specifications": {
                    'arg': {'dtype': 'multi_type'},
                    'errors': {'selection': 'dropdown', 'options': ['raise', 'coerce', 'ignore']},
                    'utc': {'dtype': 'bool'},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == "CONVERT <value> TO NUMERIC":
            kwargs = dict(arg=entities['<value0>'])
            return {
                "general_action": dsl_action,
                "general_pandas_function": "to_numeric",
                "class_callable": pd.to_numeric,
                "kwargs": kwargs,
                "type": "general_pandas",
                "parameter_specifications": {
                    'arg': {'dtype': 'multi_type'},
                    'errors': {'selection': 'dropdown', 'options': ['raise', 'coerce', 'ignore']},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == "READ <value> AS CSV":
            kwargs = dict(filepath_or_buffer=entities['<value0>'])
            return {
                "general_action": dsl_action,
                "general_pandas_function": "read_csv",
                "class_callable": pd.read_csv,
                "kwargs": kwargs,
                "type": "general_pandas",
                "parameter_specifications": {
                    # 'filepath_or_buffer': {'dtype': 'multi_type'},
                    'header': {'dtype': 'int'},
                    'index_col': {'dtype': 'multi_type'},
                    'usecols': {'dtype': 'multi_type'},
                    'dtype': {'dtype': 'multi_type'},
                    'engine': {'selection': 'dropdown', 'options': ['c', 'python', 'pyarrow']},
                    'skiprows': {'dtype': 'multi_type'},
                    'na_values': {'dtype': 'multi_type'},
                    'parse_dates': {'dtype': 'multi_type'},
                    'compression': {'dtype': 'multi_type'},
                    'quoting': {'dtype': 'multi_type'},
                    'dialect': {'dtype': 'multi_type'},
                    'on_bad_lines': {'selection': 'dropdown', 'options': ['error', 'warn', 'skip']},
                    'prefix': {'dtype': 'text', 'value': ''},
                    'sep': {'dtype': 'text', 'value': ','},
                    'names': {'dtype': 'multy_type', 'value': ''},

                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == "SHOW INFORMATION":

            return {
                "general_pandas_function": "info",
                "class_callable": pd.DataFrame.info,
                "kwargs": {},
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'verbose': {'dtype': 'bool'},
                    'memory_usage': {'dtype': 'bool'},
                    'show_counts': {'dtype': 'bool'}},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == "DESCRIBE DATAFRAME":
            return {
                "general_pandas_function": "describe",
                "class_callable": pd.DataFrame.describe,
                "kwargs": {},
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ["SHOW FIRST <number> ROWS", "SHOW FIRST ROWS"]:
            if entities:
                kwargs = dict(n=entities['<number0>'])
            else:
                kwargs = {}
            return {
                "general_pandas_function": "head",
                "class_callable": pd.DataFrame.head,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'n': {'dtype': 'number'},
                },
                "scope_options": ['subset_col'],
                "scope": {}
            }

        elif dsl_action == "SHOW MISSING VALUES":
            return {
                "general_pandas_function": "isnull",
                "class_callable": pd.DataFrame.isnull,
                "kwargs": {},
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ["DROP MISSING VALUES", "DROP MISSING VALUES FROM <value>"]:
            kwargs = dict()
            if entities:
                kwargs = dict(subset=entities['<value0>'])
            return {
                "general_pandas_function": "dropna",
                "class_callable": pd.DataFrame.dropna,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'how': {'selection': 'dropdown', 'options': ['any', 'all']},
                    'thresh': {'dtype': 'number'},
                    'subset': {'dtype': 'DataFrame_axis_opposite', 'selection': 'dropdown_multi'},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['FILL MISSING VALUES WITH <value>', 'FILLL MISSING VALUES WITH <number>']:
            try:
                kwargs = dict(value=entities['<value0>'])
            except KeyError:
                kwargs = dict(value=entities['<number0>'])

            return {
                "general_pandas_function": "fillna",
                "class_callable": pd.DataFrame.fillna,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'method': {'selection': 'dropdown', 'options': ['backfill', 'bfill', 'pad', 'ffill', None]},
                    'limit': {'dtype': 'number'},
                    'downcast': {'dtype': 'multi_type'}
                },
                "scope_options": ['subset_col'],
                "scope": {}
            }

        elif dsl_action in 'DROP DUPLICATE VALUES':
            return {
                "general_pandas_function": "drop_duplicates",
                "class_callable": pd.DataFrame.drop_duplicates,
                "kwargs": {},
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'subset': {'dtype': 'DataFrame_axis', 'selection': 'dropdown_multi'},
                    'keep': {'selection': 'dropdown', 'options': ['first', 'last', False]},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['CHANGE DATATYPE TO <value>', 'ON COLUMN <value> CHANGE DATATYPE TO <value>']:

            if len(entities) == 2:
                kwargs = dict(dtype=entities['<value1>'])
                scope = dict(subset_col={'value': entities['<value0>']})
            else:
                kwargs = dict(dtype=entities['<value0>'])
                scope = dict()

            return {
                "general_pandas_function": "astype",
                "class_callable": pd.DataFrame.astype,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'errors': {'selection': 'dropdown', 'options': ['raise', 'ignore']},
                },
                "scope_options": ['subset_col'],
                "scope": scope
            }

        elif dsl_action in ['ROUND TO <number> DECIMAL POINTS', 'ON COLUMN <value> ROUND TO <number> DECIMAL POINTS']:
            kwargs = dict(decimals=entities['<number0>'])
            scope = dict()

            if len(entities) == 2:
                kwargs = dict(decimals=entities['<number0>'])
                scope = dict(subset_col={'value': entities['<value0>']})

            return {
                "general_pandas_function": "round",
                "class_callable": pd.DataFrame.round,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": ['subset_col'],
                "scope": scope
            }

        elif dsl_action in ['RENAME <value> TO <value>', 'RENAME COLUMNS TO <value>']:
            mapper: Union[Dict, Set]
            if len(entities) == 2:
                mapper = {entities['<value0>']: entities['<value1>']}
            else:
                try:
                    assert isinstance(entities['<value0>'], str)
                    string_dict = entities['<value0>'].replace("'", '"')
                    mapper = json.loads(string_dict)
                except Exception:
                    mapper = {entities['<value0>']}

            kwargs = dict(mapper=mapper, axis="columns")

            return {
                "general_pandas_function": "rename",
                "class_callable": pd.DataFrame.rename,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {'mapper': {'dtype': 'multi_type'}, 'level': {'dtype': 'number'}},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['MELT DATAFRAME', 'MELT DATAFRAME WITH <string_list> AS COLUMNS']:
            kwargs = dict()
            if entities:
                kwargs = dict(id_vars=entities['<string_list0>'])

            return {
                "general_pandas_function": "melt",
                "class_callable": pd.DataFrame.melt,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'id_vars': {'dtype': 'DataFrame_columns', 'selection': 'dropdown_multi'},
                    'value_vars': {'dtype': 'DataFrame_columns', 'selection': 'dropdown_multi'},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['FILTER FOR COLUMN <value>', 'FILTER FOR COLUMN <string_list>']:
            try:
                kwargs = dict(items=[entities['<value0>']], axis='columns')
            except KeyError:
                kwargs = dict(items=entities['<string_list0>'], axis='columns')
            return {
                "general_pandas_function": "filter",
                "class_callable": pd.DataFrame.filter,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'items': {'dtype': 'DataFrame_axis', 'selection': 'dropdown_multi'},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == 'SET INDEX TO <value>':
            kwargs = dict(keys=entities['<value0>'])
            return {
                "general_pandas_function": "set_index",
                "class_callable": pd.DataFrame.set_index,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'keys': {'dtype': 'DataFrame_axis'},
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == 'RESET INDEX':

            return {
                "general_pandas_function": "reset_index",
                "class_callable": pd.DataFrame.reset_index,
                "kwargs": {},
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == 'SORT VALUES BY <value>':
            kwargs = dict(by=entities['<value0>'], axis="index", inplace=True)

            return {
                "general_pandas_function": "sort_values",
                "class_callable": pd.DataFrame.sort_values,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'by': {'dtype': 'DataFrame_axis_opposite', 'selection': 'dropdown_multi'},
                    'kind': {'selection': 'dropdown', 'options': ['quicksort', 'mergesort', 'heapsort', 'stable']},
                    'na_position': {'selection': 'dropdown', 'options': ['first', 'last']}},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['ASSIGN NEW COLUMN', 'ASSIGN NEW COLUMN AS <value>']:
            kwargs = dict()
            if entities:
                kwargs = dict(kwargs=entities['<value0>'])

            return {
                "general_pandas_function": "assign",
                "class_callable": pd.DataFrame.assign,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['GROUP BY COLUMN <value>', 'GROUP BY COLUMN <string_list>']:
            try:
                kwargs = dict(by=entities['<value0>'], axis='columns')
            except KeyError:
                kwargs = dict(by=entities['<string_list0>'], axis="columns")

            return {
                "general_pandas_function": "groupby",
                "class_callable": pd.DataFrame.groupby,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'by': {'dtype': 'DataFrame_axis', 'selection': 'dropdown_multi'},
                    'level': {'dtype': 'number'},
                    'squeeze': {'dtype': 'bool', 'value': False},  # incorrect in signature
                },
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action == 'AGGREGATE USING <value>':
            kwargs = dict(func=entities['<value0>'])

            return {
                "general_pandas_function": "agg",
                "class_callable": pd.DataFrame.agg,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": ['subset_col'],
                "scope": {}
            }

        elif dsl_action in ['SAVE TO CSV', 'SAVE TO CSV AS <value>']:
            if entities:
                kwargs = dict(path_or_buf=entities['<value0>'])
            else:
                kwargs = dict()

            return {
                "general_pandas_function": "to_csv",
                "class_callable": pd.DataFrame.to_csv,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {},
                "scope_options": [],
                "scope": {}
            }

        elif dsl_action in ['DELETE COLUMN <value>', 'DELETE COLUMN', 'DELETE COLUMN <string_list>']:
            if entities:
                try:
                    kwargs = dict(labels=entities['<value0>'], axis='columns')
                except KeyError:
                    kwargs = dict(labels=entities['<string_list0>'], axis='columns')
            else:
                kwargs = dict(axis='columns')

            return {
                "general_pandas_function": "drop",
                "class_callable": pd.DataFrame.drop,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {
                    'labels': {'dtype': 'DataFrame_axis', 'selection': 'dropdown_multi'},
                    'index': {'dtype': 'DataFrame_axis'},
                    'columns': {'dtype': 'DataFrame_columns'},
                    'level': {'dtype': 'number'},
                },
                "scope_options": [],
                "scope": {},
            }

        elif dsl_action in ['DELETE ROW <number>', 'DELETE ROWS <number_list>', 'DELETE ROWS']:

            if '<number0>' in entities:
                kwargs = dict(labels=entities['<number0>'], axis="index")
            elif '<number_list0>' in entities:
                kwargs = dict(labels=entities['<number_list0>'], axis="index")
            else:
                kwargs = dict()

            return {
                "general_pandas_function": "drop",
                "class_callable": pd.DataFrame.drop,
                "kwargs": kwargs,
                "type": "pandas.DataFrame",
                "parameter_specifications": {'labels': {'dtype': 'DataFrame_axis', 'selection': 'dropdown_multi'},
                                             'level': {'dtype': 'number'}},
                "scope_options": [],
                "scope": {}

            }

        elif dsl_action == 'ON COLUMN <value> STRIP <value>':
            scope = {'subset_col': {'value': entities['<value0>']}}
            kwargs = dict(to_strip=entities['<value1>'])

            return {
                "general_pandas_function": "str.strip",
                "class_callable": pd.Series.str.strip,
                "kwargs": kwargs,
                "type": "pandas.Series",
                "parameter_specifications": {},
                "scope_options": ['subset_col'],
                "scope": scope
            }

        elif dsl_action in ["ON COLUMN <value> SPLIT ON <value>", "SPLIT ON COLUMN <value>"]:
            kwargs = dict()
            scope = {'subset_col': {'value': entities['<value0>']}}

            if len(entities) == 2:
                kwargs = dict(pat=entities['<value1>'])

            return {
                "general_pandas_function": "str.split",
                "class_callable": pd.Series.str.split,
                "kwargs": kwargs,
                "type": "pandas.Series",
                "parameter_specifications": {
                    'n': {'dtype': 'number'},
                    'regex': {'dtype': 'bool'}
                },
                "scope_options": ['subset_col'],
                "scope": scope
            }

        elif dsl_action in ['ON COLUMN <value> REPLACE <value> WITH <value>', 'REPLACE VALUES']:
            kwargs = dict()
            scope = dict()
            if entities:
                kwargs = dict(pat=entities['<value1>'], repl=entities['<value2>'])
                scope = {'subset_col': {'value': entities['<value0>']}}

            return {
                "general_pandas_function": "str.replace",
                "class_callable": pd.Series.str.replace,
                "kwargs": kwargs,
                "type": "pandas.Series",
                "parameter_specifications": {
                    'n': {'dtype': 'number'},
                    'regex': {'dtype': 'bool'},
                    'case': {'dtype': 'bool'},
                    'flags': {'dtype': 'number'}
                },
                "scope_options": ['subset_col'],
                "scope": scope
            }

        elif dsl_action == "ON COLUMN <value> JOIN ON <value>":
            kwargs = dict(sep=entities['<value1>'])
            scope = {'subset_col': {'value': entities['<value0>']}}

            return {
                "general_pandas_function": "str.join",
                "class_callable": pd.Series.str.join,
                "kwargs": kwargs,
                "type": "pandas.Series",
                "parameter_specifications": {},
                "scope_options": ['subset_col'],
                "scope": scope
            }

        elif dsl_action in ["ON COLUMN <value> EXTRACT <value>", "EXTRACT VALUES"]:
            kwargs = dict()
            scope = dict()
            if entities:
                kwargs = dict(pat=entities['<value1>'])
                scope = {'subset_col': {'value': entities['<value0>']}}

            return {
                "general_pandas_function": "str.extract",
                "class_callable": pd.Series.str.extract,
                "kwargs": kwargs,
                "type": "pandas.Series",
                "parameter_specifications": {},
                "scope_options": ['subset_col'],
                "scope": scope
            }
        elif dsl_action == "GET UNIQUE VALUES FROM <value>":
            scope = {'subset_col': {'value': entities['<value0>']}}

            return {
                "general_pandas_function": "unique",
                "class_callable": pd.Series.unique,
                "kwargs": {},
                "type": "pandas.Series",
                "parameter_specifications": {},
                "scope_options": ['subset_col'],
                "scope": scope
            }

        else:
            return {
                "general_pandas_function": "not implemented",
                "class_callable": None,
                "parameters": "not implemented",
                "kwargs": 'not implemented',
                "description": 'not implemented',
                "scope_options": [],
                "scope": {}
            }
