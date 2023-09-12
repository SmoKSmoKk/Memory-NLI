import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple

from nl2pandas.backend.pandas_generator.code_generator.code_generator import (
    CodeGenerator,
)
from nl2pandas.backend.pandas_generator.context.context import Context


class Refiner:
    """
    This class manages the parameters, context and scope of a single Pandas method.
    :param context: an instance of the Context class
    """
    def __init__(self, context: Context):

        self.context: Context = context
        self.code_generator = CodeGenerator(refiner=self)
        self.parameters: Dict[str, Dict[str, Any]] = {}
        self._refined_kwargs: Dict[str, Any] = {}
        self.kwargs: Dict = {}
        self._axis: str = ''
        self.df_dependencies: List = []
        self.scope: Dict[str, Dict[str, Any]] = {}
        self.executable_function: str = ''
        self.program_info: Dict[str, Any] = {}
        self.return_df: str = ''
        self.multi_type_input_fields: List = []

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, value: str):
        if value != self.axis:
            self._axis = value
            self.update_df_dependencies()

    @property
    def refined_kwargs(self):
        return self._refined_kwargs

    @refined_kwargs.setter
    def refined_kwargs(self, new_kwargs: Dict[str, Any]):
        self._refined_kwargs = new_kwargs
        self.refine_kwargs()

    def set_refiner(self, program: Dict) -> None:
        """
        Sets up the parameters of the Refiner class for a specific pandas function

        :param program: the dictionary with pandas info as given by the Translator class
        """
        # get the parameters options for the given pandas function
        self.parameters = self.get_function_parameters(
            pandas_func=program['class_callable'],
            param_specs=program['parameter_specifications']
        )

        self.df_dependencies = [
            param for param in self.parameters
            if self.parameters[param]['dtype']
            in ["DataFrame_axis", "DataFrame_axis_opposite", "DataFrame_columns", "DataFrame_index"]
        ]

        self.multi_type_input_fields = [
            param for param in self.parameters if self.parameters[param]['dtype'] == 'multi_type'
        ]

        # update the scope options
        scope = self.get_scope_options(
            scope_options=program['scope_options'],
            scope=program['scope']
        )

        if program['type'] == "general_pandas":
            self.return_df = 'result'
        else:
            self.return_df = self.context.active_dataframe

        self.scope = scope
        self.kwargs = program['kwargs']

        # set pandas info dictionary
        to_remove = ('kwargs', 'parameter_specifications', 'parameters', 'pandas_function',
                     'refined_kwargs', 'scope_options', 'scope', 'probability')

        new_program = program.copy()
        for item in to_remove:
            new_program.pop(item, None)

        self.program_info = new_program

        # create refinable kwargs list with either the user set value or the default value
        refined_kwargs = {}

        for param in self.parameters:
            refined_kwargs[param] = self.parameters[param]['value']

        for param in self.kwargs:
            refined_kwargs[param] = self.kwargs[param]

        self.refined_kwargs = refined_kwargs

        # validate active df and update if necessary
        for param in self.df_dependencies:
            if param in self.kwargs:
                self.context.validate_active_df(self.kwargs[param])

        # set axis
        if 'axis' in self.parameters:
            self.axis = self.refined_kwargs['axis']

        # set context refiner
        self.context.set_refiner(self)

        if scope != {}:
            for param in scope:
                self.context.validate_active_df(scope[param]['value'])

        # print('\nafter setup: ',
        #       '\n parameters: ', self.parameters,
        #       '\n refined kwargs: ', self._refined_kwargs,
        #       '\n kwargs: ', self.kwargs,
        #       '\n axis: ', self._axis,
        #       '\n df_dependencies: ', self.df_dependencies,
        #       '\n scope: ', self.scope,
        #       '\n executable function: ', self.executable_function,
        #       '\n return df: ', self.return_df
        #       )

    def update_df_dependencies(self) -> None:
        """
        Updates the parameters that are depended on the axis and dataframe instance. This is called
        whenever the axis or active dataframe changes.
        """

        for param in self.df_dependencies:
            columns = self.context.active_df_columns.copy()
            indices = self.context.active_df_indices.copy()

            if self.parameters[param]['dtype'] == "DataFrame_columns":
                self.parameters[param]['options'] = columns
            elif self.parameters[param]['dtype'] == "DataFrame_index":
                self.parameters[param]['options'] = indices

            elif self.parameters[param]['dtype'] == "DataFrame_axis":
                self.parameters[param]['options'] = columns \
                    if self.axis == 'columns' else indices
            elif self.parameters[param]['dtype'] == "DataFrame_axis_opposite":
                self.parameters[param]['options'] = indices \
                    if self.axis == 'columns' else columns

            if isinstance(self.refined_kwargs[param], List):
                if not all([item in self.parameters[param]['options'] for item in self.refined_kwargs[param]]):
                    ref_kwargs = self.refined_kwargs.copy()
                    try:
                        ref_kwargs[param] = self.parameters[param]['options'][0]  # set to first option by default
                        self.refined_kwargs = ref_kwargs
                    except IndexError:
                        print("No DataFrame context found. Are there existing DataFrames in the Code?")
            else:
                if str(self.refined_kwargs[param]) not in str(self.parameters[param]['options']):
                    ref_kwargs = self.refined_kwargs.copy()
                    # ref_kwargs[param] = self.parameters[param]['value']  # set to default None
                    try:
                        ref_kwargs[param] = self.parameters[param]['options'][0]  # set to first option by default
                        self.refined_kwargs = ref_kwargs
                    except IndexError:
                        print("No DataFrame context found. Are there existing DataFrames in the Code?")

        if 'axis' in self.refined_kwargs:
            self.refined_kwargs['axis'] = self.axis

        if 'subset_col' in self.scope:
            self.scope['subset_col']['options'] = self.context.active_df_columns

        # update return dataframe if it is still default
        if self.return_df in self.context.dataframes:
            self.return_df = self.context.active_dataframe

        self.executable_function = self.code_generator.get_function_string(**self.kwargs)

    def get_param_options(self, parameters: Dict[str, Dict[str, Optional[Any]]]) -> Dict[str, Dict[str, Optional[Any]]]:  # noqa: C901
        """
        Loosely determines the parameter options based on data type and adds them to the dictionary

        :param parameters: a nested dictionary holding the parameters and their additional info

        :return: a dictionary with available parameters and their options.

        Example:
            {
            'axis': {'value': 0, 'type': 'axis', 'options': [0, 1], 'selection': 'dropdown'},
            'inplace': {'value': False, 'type': 'bool', 'options': ['True', 'False'], 'selection': 'dropdown'},
            'errors': {'value': 'raise', 'type': 'str', 'options': None, 'selection': 'text'}
            }
        """
        for param in parameters:

            if param == 'axis':
                parameters[param]['value'] = 'index'
                parameters[param]['options'] = ["columns", "index"]
                parameters[param]['selection'] = 'dropdown'
                parameters[param]['dtype'] = 'axis'

            elif isinstance(parameters[param]['value'], bool) or parameters[param]['dtype'] == 'bool':
                if parameters[param]['options'] is None:
                    parameters[param]['options'] = ["True", "False"]
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'dropdown'

            elif parameters[param]['dtype'] == 'DataFrame_axis':
                if parameters[param]['options'] is None:
                    parameters[param]['options'] = self.context.active_df_columns
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'dropdown'

            elif parameters[param]['dtype'] == 'DataFrame_axis_opposite':
                if parameters[param]['options'] is None:
                    parameters[param]['options'] = self.context.active_df_columns
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'dropdown'

            elif parameters[param]['dtype'] == 'DataFrame_columns':
                if parameters[param]['options'] is None:
                    parameters[param]['options'] = self.context.active_df_columns
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'dropdown'

            elif parameters[param]['dtype'] == 'DataFrame_index':
                if parameters[param]['options'] is None:
                    parameters[param]['options'] = self.context.active_df_indices
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'dropdown'

            elif parameters[param]['dtype'] == 'number':
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'number'

            elif param in ['args', 'kwargs'] or "<class 'inspect._empty'>" in str(parameters[param]['value']):
                parameters[param]['value'] = ''
                parameters[param]['selection'] = 'text'

            else:
                if parameters[param]['selection'] is None:
                    parameters[param]['selection'] = 'text'

        return parameters

    def get_function_parameters(self, pandas_func: Callable, param_specs: Dict) -> Dict[str, Dict[str, Any]]:
        """
        Uses the inspect feature to create a dictionary of available parameters for a
        pandas function and sets the values to either the default value or those given by the user.

        :param pandas_func: a pandas function to inspect
        :param param_specs: a dictionary of parameter options specific to a function

        :return: dictionary of available parameters with either their default values
        or the values set by the user
        """
        parameters = {}
        signature = inspect.signature(pandas_func)

        for param in signature.parameters:
            parameters[param] = {
                "value": signature.parameters[param].default,
                "dtype": signature.parameters[param].annotation,
                "options": None,
                "selection": None
            }

        parameters.pop('self', None)

        # set any specified parameter options
        for param in param_specs:
            for value in param_specs[param]:
                if value in parameters[param]:
                    parameters[param][value] = param_specs[param][value]

        # get options and selection types
        parameters = self.get_param_options(parameters)

        return parameters

    def get_scope_options(self, scope_options: List, scope: Dict) -> Dict[str, Dict[str, str]]:
        """
        Completes the parameters of scope options given the available scope of a function

        :param scope_options: List of allowed scope options for the function
        :param scope: Dict with previously set scope values
        :return: Dictionary with scope parameter
        """
        for param in scope_options:
            if param == 'subset_col':
                if param in scope:
                    scope[param]['value'] = scope[param]['value'] if 'value' in scope[param] else None
                    scope[param]['selection'] = scope[param]['selection'] \
                        if 'selection' in scope[param] else 'dropdown'
                else:
                    scope[param] = {}
                    scope[param]['value'] = None
                    scope[param]['selection'] = 'dropdown'
                scope[param]['dtype'] = 'DataFrame_columns'
                scope[param]['options'] = self.context.active_df_columns

            else:
                # set empty
                scope[param]['value'] = None
                scope[param]['dtype'] = None
                scope[param]['options'] = None
                scope[param]['selection'] = None

        return scope

    def get_scope_parameters(self) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Splits the parameters into scope dependent and non-scope dependent parameters

        :return: a dictionary with scope dependent and a dictionary with scope independent parameters
        """

        scope_parameters = {}
        non_scope_parameters = self.parameters.copy()

        for param in self.parameters:
            if non_scope_parameters[param]['dtype'] in ['DataFrame_axis', 'DataFrame_axis_opposite', 'axis']:
                scope_parameters[param] = non_scope_parameters.pop(param)

        return non_scope_parameters, scope_parameters

    def refine_kwargs(self) -> None:
        """
        Creates the keyword argument list from the refined keyword argument list

        """
        new_kwargs = {}
        for param in self.refined_kwargs:

            # don't add default values
            if self.refined_kwargs[param] != self.parameters[param]['value']:
                new_kwargs[param] = self.refined_kwargs[param]

        self.kwargs = new_kwargs
        self.executable_function = self.code_generator.get_function_string(**self.kwargs)
