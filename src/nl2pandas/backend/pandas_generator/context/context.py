import base64
from typing import Any, Dict, List, Optional, Tuple, Union

import IPython
from IPython.display import Javascript, display
from IPython.utils import io
from nl2pandas.backend.pandas_generator.definitions import DATABASE_PATH  # noqa: E402
from nl2pandas.backend.pandas_generator.memory.memory import Database


class Context:
    def __init__(self, ipython):
        """
        This class manages the current context of the active jupyter notebook session
        """
        self.ipython = ipython
        self.dataframes: Dict[str, Dict[str, List[Any]]] = {}
        self.current_cell: str = ""
        self.current_cell_id: int = 0
        self._active_dataframe: str = ""
        self.active_df_columns: List[Any] = []
        self.active_df_indices: List[Any] = []
        self.cells: List = []

        self.refiner = None  # activate evaluation_code_generator of dataframe dependent parameters

    @property
    def active_dataframe(self):
        return self._active_dataframe

    @active_dataframe.setter
    def active_dataframe(self, new_df):
        self.update_active_dataframe(new_df)

        if self.refiner:
            self.refiner.update_df_dependencies()

    def update_active_dataframe(self, active_dataframe: str):
        """
        Sets the active dataframe and updates the refiner.

        :param active_dataframe:
        """
        self._active_dataframe = active_dataframe
        self.active_df_columns = [col for col in self.dataframes[self.active_dataframe]['columns']] + ["None"]
        self.active_df_indices = [idx for idx in self.dataframes[self.active_dataframe]['indices']] + ["None"]

        if self.refiner:
            self.refiner.update_df_dependencies()

    def set_refiner(self, refiner):
        """
        Sets the refiner instance for active dataframe updating purposes

        :param refiner: the refiner instance
        """
        self.refiner = refiner

    def is_column_name(self, value: Union[str, List]) -> Tuple[bool, List]:
        """
        Returns True if the given string is a dataframe column name, or if all entries in a list of strings are
        dataframe column names.

        :param value: dataframe column name

        :return: True and the corresponding dataframes or False and an empty list
        """
        valid_dfs: List = []
        for df in self.dataframes:

            if isinstance(value, List):
                if all([item in self.dataframes[df]['columns'] for item in value]):
                    valid_dfs.append(df)

            elif value in self.dataframes[df]['columns']:
                valid_dfs.append(df)

        if valid_dfs:
            return True, valid_dfs
        else:
            return False, valid_dfs

    def is_index(self, value: Union[str, int, float, List]) -> Tuple[bool, List]:
        """
        Returns True if the given string is a dataframe index name, or if all entries in a list of strings
        are dataframe index names

        :param value: dataframe index name

        :return: True and the corresponding dataframes or False and an empty list
        """
        valid_dfs: List = []
        for df in self.dataframes:
            if isinstance(value, List):
                if all([item in self.dataframes[df]['indices'] for item in value]):
                    valid_dfs.append(df)

            elif value in self.dataframes[df]['indices']:
                valid_dfs.append(df)

        if valid_dfs:
            return True, valid_dfs
        else:
            return False, valid_dfs

    def validate_active_df(self, df_label: Union[str, List]):
        """
        Given a dataframe label (column or index name or names), it is verified that the label exists
        in the active dataframe. If not, the active dataframe is changed to one that includes the label.

        :param df_label: str containing a dataframe label or list containing multiple labels
        """
        is_column_name, valid_column_df = self.is_column_name(df_label)
        is_index_name, valid_index_df = self.is_index(df_label)

        # assert isinstance(valid_column_df, List)
        if is_index_name:
            if self.active_dataframe not in valid_index_df:
                self.active_dataframe = valid_index_df[0]

        if is_column_name:
            if self.active_dataframe not in valid_column_df:
                self.active_dataframe = valid_column_df[0]

    def update_context(self, ipython):
        """
        update the context based on the current ipython instance. This method must be called after initializing
        the Context class instance, otherwise the attributes will remain empty.

        :param ipython: the ipython shell instance from the Jupyter notebook
        """
        self.ipython = ipython

        # get dataframes
        dfs = ipython.run_line_magic('who_ls', 'DataFrame')
        self.dataframes = {
            i: {'columns': ipython.user_ns[i].columns, 'indices': ipython.user_ns[i].index.tolist()} for i in dfs
        }

        # get active cell
        cells = [k for k, v in self.ipython.user_ns.items() if k.startswith('_i')]
        if cells:
            try:
                # drop unwanted cells
                cells.remove('_ih')
                cells.remove('_i')
                cells.remove('_ii')
                cells.remove('_iii')

                self.cells = cells
                self.current_cell_id = cells[-1]
                self.current_cell = str(self.ipython.user_ns[cells[-1]])

            except ValueError:
                pass
        else:
            self.current_cell_id = 0
            self.current_cell = ''

        # if active dataframe emtpy, set as default to last referenced dataframe
        cell_df = self.get_cell_df(df_list=dfs, cell_list=cells)

        db = Database(file=DATABASE_PATH)
        saved_df = db.load('active_dataframe')

        if saved_df is not None and saved_df in self.dataframes:
            self.active_dataframe = saved_df

        elif cell_df is not None:
            try:
                last_ref = list(cell_df.keys())[-1]
                self.active_dataframe = cell_df[last_ref][0]
            except IndexError:
                pass

    def get_cell_df(self, df_list: List[str], cell_list: List[str]) -> Dict[str, List[str]]:
        """
        Traverses through the cell content of the Jupyter notebook looking for references to the dataframes

        :param df_list: list of existing dataframe names
        :param cell_list: list of existing cells by execution id. Example: _i1

        :return: dictionary with cell id's as keys and a list of dataframes that exist in this cell as value.
        """
        df_cells: Dict[str, List[str]] = dict()

        for cell in cell_list:
            for df in df_list:
                # does not exclude commented out dataframe references
                if (
                    self.ipython.user_ns[cell].rfind(df+' ') != -1
                    or self.ipython.user_ns[cell].rfind(df+'.') != -1
                    or self.ipython.user_ns[cell].rfind(df+'[') != -1
                    or self.ipython.user_ns[cell].rfind(df+'\n') != -1
                    or self.ipython.user_ns[cell].rfind(df+'=') != -1
                ):
                    if cell not in df_cells.keys():
                        df_cells[cell] = [df]
                    else:
                        df_cells[cell].append(df)

        return df_cells

    def write_cell(self, code: str, execute: bool = True):
        """
        Overwrites the current active IPython notebook cell with the updated code

        :param code: the content to add to write to the cell. Contains the code containing the previous cell content,
        the nl prompt as a comment and the newly added pandas function
        :param execute: determines whether to execute the cell after replacing the content
        """
        encoded_code = (base64.b64encode(str.encode(code))).decode()
        ex = "cell.execute()" if execute else ""
        display(Javascript("""
                // find cell element
                var output_area = this;
                var element = output_area.element.parents('.cell');
                var idx = Jupyter.notebook.get_cell_elements().index(element);
                // get the cell object
                var cell = Jupyter.notebook.get_cell(idx);
                cell.set_text(atob("{0}"));
                // execute cell
                {1};
            """.format(encoded_code, ex)))

    def validate_function(self, function: str) -> Tuple[bool, Optional[Exception]]:
        """
        Run executable pandas code in user namespace and catch and return any exceptions.
        Important: copying the user namespace to a new kernel was not possible, therefore this method
        saves the dataframes before running the pandas code, then loads the dataframes again to restore the previous
        state. Upon loading, the dataframe variables are removed from the storage so that they do not persist into
        following Jupyter notebook sessions. This might cause conflicts if a user is utilizing the storage magic to save
        their kernel session!

        :return: A boolean indicating the execution status and the exception message
        """
        temp_ipython = IPython.InteractiveShell.instance()
        temp_ipython.push(self.ipython.user_ns)

        # save current dataframes state to restore after validation
        if self.dataframes:
            dfs = "%s" % " ".join([key for key in self.dataframes])

            with io.capture_output():
                temp_ipython.run_line_magic('store', dfs)

            try:
                with io.capture_output():
                    temp_ipython.ex(function)
                    temp_ipython.run_line_magic('store', '-r ' + dfs)
                    temp_ipython.run_line_magic('store', '-d ' + dfs)  # removes the stored value from storage entirely!
                return True, None

            except Exception as exception:
                temp_ipython.run_line_magic('store', '-r ' + dfs)
                temp_ipython.run_line_magic('store', '-d ' + dfs)
                return False, exception
        else:
            try:
                with io.capture_output():
                    temp_ipython.ex(function)
                return True, None

            except Exception as exception:
                return False, exception
