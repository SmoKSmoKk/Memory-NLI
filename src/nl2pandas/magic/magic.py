from typing import Dict, List

import idom_jupyter
import ipywidgets as widgets
from idom import component, html, use_state
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.display import clear_output, display
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.manager.manager import PandasManager
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner

from nl2pandas.jupyter_interface.styles.styles import headline_style
from nl2pandas.jupyter_interface.views.inspection_view.inspection_view import \
    inspection_view
from nl2pandas.jupyter_interface.views.refinement_view.refinement_view import \
    refinement_view
from nl2pandas.jupyter_interface.views.selection_view.selection_view import \
    selection_view
from nl2pandas.jupyter_interface.views.unsure_view.unsure_view import unsure_view


@magics_class
class PandasNli(Magics):

    def __init__(self, shell):
        super(PandasNli, self).__init__(shell)
        self.context = Context(self.shell)
        self.pandas_manager = PandasManager(self.context)
        self.value: str = ""

    @component
    def ui_flow(self, action_info: List[Dict], unsure: bool = False):  # noqa: C901
        """
        the dialog flow of the natural language interface

        :param action_info: List of dictionaries containing the pandas info
        :param unsure: boolean, True if the results of the NLI pipeline was NOT_SURE

        structure example:
            {
            "general_action": "DELETE COLUMN <value>",
            "pandas_function": "df.drop(labels='A', axis=1)",
            "parameters": (self, labels=None, axis: 'Axis' = 0, index=None, columns=None, level: 'Level | None' = None,
                            inplace: 'bool' = False, errors: 'str' = 'raise'),
            "kwargs": {"labels":"A", "axis":1},
            "description": "Drop specified labels from rows or columns.",
            "grounded_action": "DELETE COLUMN 'A'",
            "probability": "78",
            "nl_utterance": "remove the column 'A'"
            }

        :return: the active view of the dialog flow
        """
        current_page, set_current_page = use_state("unsure_view" if unsure else "selection_view")

        # selection view state components
        suggested_programs, set_suggested_programs = use_state(action_info)
        selected_program, set_selected_program = use_state(Refiner(self.context))

        # inspection view state components
        value_checkbox_nl, set_value_checkbox_nl = use_state(True)
        value_checkbox_dsl, set_value_checkbox_dsl = use_state(False)

        view = html.div()

        def handle_unsure_method_selection(event):
            new_content = "%nl2pandas {}\n".format(event['target']['value'])

            content = self.context.current_cell.replace(
                '%nl2pandas {}'.format(action_info[0]['nl_utterance']), new_content,
            )
            self.context.write_cell(code=content, execute=False)

            clear_output()

        def handle_selection(event):
            program = {}

            for p in suggested_programs:
                if p['grounded_action'] == event["target"]["value"]:
                    program = p

            pandas_info = self.pandas_manager.get_refiner(program.copy())
            set_selected_program(pandas_info)
            set_current_page("inspection_view")

        def handle_change_program(event):
            set_current_page('selection_view')

        def handle_apply(event):
            new_content = ""

            if value_checkbox_nl:
                new_content = new_content + "# %nl2pandas {}\n".format(selected_program.program_info['nl_utterance'])

            if value_checkbox_dsl:
                new_content = new_content + f"# {selected_program.program_info['grounded_action']}\n"

            new_content = new_content + selected_program.executable_function

            content = self.context.current_cell.replace(
                '%nl2pandas {}'.format(selected_program.program_info['nl_utterance']), new_content
            )

            self.context.write_cell(code=content, execute=True)

        def handle_refine(event):
            set_current_page("refinement_view")

        def handle_change_nl(event):
            set_value_checkbox_nl(not value_checkbox_nl)

        def handle_change_dsl(event):
            set_value_checkbox_dsl(not value_checkbox_dsl)

        def on_apply_refinement(event, kwargs, scope, memory):
            # convert string values to correct python type
            for param in kwargs:
                if kwargs[param] == "True" or kwargs[param] == 'true':  # sets to Javascript true
                    kwargs[param] = True
                elif kwargs[param] == "False" or kwargs[param] == 'false':  # sets to Javascript false
                    kwargs[param] = False
                elif kwargs[param] == 'None':
                    kwargs[param] = None
                elif kwargs[param] == '':
                    kwargs[param] = selected_program.parameters[param]['value']  # some default values are not pretty

            selected_program.refined_kwargs = kwargs
            selected_program.scope = scope
            self.pandas_manager.set_past_actions(memory)

            set_current_page("inspection_view")

        # set current page view
        if current_page == "unsure_view":
            view = unsure_view(
                action_utterance=self.pandas_manager.pipeline.data.action_utterance_pairs,
                on_select=handle_unsure_method_selection,
            )

        if current_page == "selection_view":
            view = selection_view(
                on_change=handle_selection,
                data=suggested_programs,
            )

        elif current_page == "inspection_view":
            view = inspection_view(
                on_change_program=handle_change_program,
                on_apply=handle_apply,
                on_refine=handle_refine,
                on_check_nl=handle_change_nl,
                on_check_dsl=handle_change_dsl,
                program=selected_program,
                validator=self.context.validate_function
            )

        elif current_page == "refinement_view":
            memory = self.pandas_manager.get_past_actions(selected_program)
            view = refinement_view(
                context=self.context,
                on_apply_refinement=on_apply_refinement,
                selected_program=selected_program,
                dataframes=[df for df in self.context.dataframes.keys()],
                active_df=self.context.active_dataframe,
                past_actions=memory
            )

        elif current_page == "empty":
            return html.div()

        return html.div(
            {"style": {"overflow": "auto", "min-height": '12cm'}},
            html.h4({"style": headline_style(opacity="0.7", text_align="center")}, 'NLI Pandas'),
            view
        )

    @line_magic
    def nl2pandas(self, line):
        """
        Line magic to activate the nl2pandas interface.

        By calling %nl2pandas followed by a natural language prompt, the interface will suggest actions and generate
        refinable Pandas code. DataFrame specific entities such as values, column and index names must be encased in
        quotation marks.

        Requirements:
        - Pandas must be installed with < Import pandas as pd >
        - If calling an action other than read_csv, a DataFrame must already exist in the notebook

        :param line: the natural language utterance
        """
        self.context.update_context(self.shell)

        action_info = self.pandas_manager.get_programs(line)
        unsure = False
        if action_info[0]['grounded_action'] == 'NOT_SURE':
            action_info[0]['nl_utterance'] = line
            unsure = True

        out = widgets.Output()

        with out:

            out.clear_output()

            display(
                widgets.VBox(
                    [
                        idom_jupyter.LayoutWidget(self.ui_flow(action_info=action_info, unsure=unsure))
                    ]
                )
            )

        display(out)


def load_ipython_extension(ipython):
    """
    Function which registers the magic extension when starting the IPython server for jupyter notebook
    :param ipython: the active IPython shell
    """
    ipython.register_magics(PandasNli)
