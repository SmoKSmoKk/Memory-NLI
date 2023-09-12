

class CodeGenerator:
    """
    This class generates code lines for Pandas methods of type pandas, pandas.DataFrame and pandas.Series.
    """
    def __init__(self, refiner):
        self.refiner = refiner

    def _get_columns(self) -> str:
        """
        Creates the columns list as a string
        :return: str of the column names in a list
        """
        columns = ''

        for param in self.refiner.scope:
            if self.refiner.scope[param]['value'] is not None:
                if isinstance(self.refiner.scope[param]['value'], list):
                    columns = str(self.refiner.scope[param]['value'])
                else:
                    columns = '["' + self.refiner.scope[param]['value'] + '"]'
        return columns

    def _get_return_df(self, columns: str) -> str:
        """
        Creates the variable in which the return instance is saved. This depends on whether the inplace parameter is
        set. Series functions generally should have the dataframe column as a return variable.

        :param columns: string of columns list that should be added to the return instance
        :returns: string of the return variable with the equal sign e.g, "dataframe['column'] = "
        """
        return_df = ''

        if self.refiner.return_df == '':
            return ''

        if 'inplace' not in self.refiner.refined_kwargs.keys():
            if self.refiner.return_df in self.refiner.context.dataframes:
                return_df = self.refiner.return_df + columns + ' = '
            else:
                return_df = self.refiner.return_df + ' = '
        else:
            if self.refiner.refined_kwargs['inplace'] is False:
                if self.refiner.return_df in self.refiner.context.dataframes:
                    return_df = self.refiner.return_df + columns + ' = '
                else:
                    return_df = self.refiner.return_df + ' = '

        return return_df

    def _get_dataframe_code_str(self, pandas_func: str, kwargs_str: str) -> str:
        """
        Generates the pandas code string for class pandas.DataFrame

        :param pandas_func: string of the general pandas function, e.g. "drop"
        :param kwargs_str: string of the keyword arguments of the function string, e.g. "labels='col1', inplace=True"
        :return: the code line as a string
        """
        columns = self._get_columns()
        return_df = self._get_return_df(columns=columns)

        func_str = f"{return_df}{self.refiner.context.active_dataframe}{columns}.{pandas_func}({kwargs_str})"

        return func_str

    def _get_series_code_str(self, pandas_func: str, kwargs_str: str) -> str:
        """
        Generates the pandas code string for class pandas.Series.str

        :param pandas_func: string of the general pandas function, e.g. "drop"
        :param kwargs_str: string of the keyword arguments of the function string, e.g. "labels='col1', inplace=True"
        :return: the code line as a string
        """
        columns = self._get_columns()
        return_df = self._get_return_df(columns=columns)

        func_str = f"{return_df}{self.refiner.context.active_dataframe}{columns}.{pandas_func}({kwargs_str})"

        return func_str

    def _get_general_pandas_code_str(self, pandas_func: str, kwargs_str: str) -> str:
        """
        Generates the pandas code string for general pandas methods

        :param pandas_func: string of the general pandas function, e.g. "drop"
        :param kwargs_str: string of the keyword arguments of the function string, e.g. "labels='col1', inplace=True"
        :return: the code line as a string
        """
        columns = self._get_columns()
        return_df = self._get_return_df(columns=columns)

        func_str = f"{return_df}pd.{pandas_func}({kwargs_str})"

        return func_str

    def get_function_string(self, **kwargs) -> str:
        """
        Takes a dictionary of keyword arguments and generates the pandas code based on the function type

        :param kwargs: a dictionary of keyword arguments
        :return: a string of keyword arguments in the format key=value
        """
        general_pandas_func = self.refiner.program_info['general_pandas_function']
        kwargs_string = ", ".join(f"{key}={value}"
                                  if key in self.refiner.multi_type_input_fields
                                  else f"{value}" if key in ['kwargs']
                                  else f"{value}" if key in ['args']
                                  else f"{key}={value!r}" for key, value in kwargs.items())

        if self.refiner.program_info['type'] == "pandas.DataFrame":
            return self._get_dataframe_code_str(pandas_func=general_pandas_func, kwargs_str=kwargs_string)

        elif self.refiner.program_info['type'] == "pandas.Series":
            return self._get_series_code_str(pandas_func=general_pandas_func, kwargs_str=kwargs_string)

        elif self.refiner.program_info['type'] == "general_pandas":
            return self._get_general_pandas_code_str(pandas_func=general_pandas_func, kwargs_str=kwargs_string)

        else:
            return "unknown type"
