from typing import Callable

from idom import component, html
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner

from nl2pandas.jupyter_interface.components.controls import button, checkbox
from nl2pandas.jupyter_interface.components.display import text_box
from nl2pandas.jupyter_interface.styles.styles import (headline_style,
                                                       plain_button_style,
                                                       text_box_style)


@component
def inspection_view(
        on_change_program: Callable,
        on_apply: Callable,
        on_refine: Callable,
        on_check_nl: Callable,
        on_check_dsl: Callable,
        program: Refiner,
        validator: Callable,
):
    """
    Creates the GUI layout of the inspection view, where the pandas function
    is shown and can either be added or refined and changed

    :param on_change_program: the event handler for selecting a new program
    :param on_apply: the event handler for applying the pandas function to the existing code
    :param on_refine: the event handler for refining the pandas code
    :param on_check_nl: the checkbox event handler for adding the natural language as a comment
    :param on_check_dsl: the checkbox event handler for adding the dsl action as a comment
    :param program: the selected dsl action
    :param validator: the context validation function for detecting any errors

    :return: the html of the selection view GUI consisting of idom elements
    """
    button_change_program = button(
        handle_click=on_change_program,
        label="change program",
        icon="fa fa-undo",
        style=plain_button_style()
    )

    # run selected function to detect any errors
    success, warning = validator(program.executable_function)

    button_apply = button(
        handle_click=on_apply,
        label="Add code line" if success else "Add code anyway",
        is_disabled=False,
        style=plain_button_style(
            border="2px solid #0060df",
            background_color="white",  # #3ca1c3
            width="8cm",
            color="#0060df",
            box_shadow="None",
        )
    )

    button_refine = button(handle_click=on_refine, label="refine")
    checkbox_nl = checkbox(
        handle_change=on_check_nl,
        label="Add natural language prompt as comment",
        default_checked=True
    )
    checkbox_dsl = checkbox(handle_change=on_check_dsl, label="Add program name as comment", default_checked=False)

    selected_program_element = text_box(
        text=program.program_info['grounded_action'],
        style=text_box_style(min_width='8cm')
    )

    pandas_code_element = text_box(
        text=program.executable_function,
        style=text_box_style(font_family="monospace, monaco, curier", min_width='8cm')
    )

    return html.div(
        html.h4({"style": headline_style()}, "Selected Program: "),
        html.div({
            "style": {
                "display": "flex",
                "flex-direction": "row",
                "align-items": "center",
            }
        },
            selected_program_element,
            button_change_program,
        ),

        html.h4({"style": headline_style()}, "Pandas Function: "),
        html.div({
            "style": {
                "display": "flex",
                "flex-direction": "row",
                "align-items": "center",
            }
        },
            pandas_code_element,
            button_refine
        ),

        html.h4({"style": headline_style()}, "Add Comment:"),
        html.div(
            checkbox_nl,
            checkbox_dsl
        ),
        html.p({'style': {'color': 'red'}}, 'Warning: ' + str(warning) if warning is not None else ''),
        button_apply,
    )
