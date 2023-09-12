from typing import Any, Callable, Dict, List

from idom import html

from nl2pandas.jupyter_interface.components.display import text_box
from nl2pandas.jupyter_interface.components.input import user_input
from nl2pandas.jupyter_interface.components.selection import multi_selection, selection
from nl2pandas.jupyter_interface.styles.styles import text_box_style


def get_parameter_selection(
        parameters: Dict[str, Dict[str, Any]],
        on_set_parameter: Callable,
        kwargs: Dict[str, Any],
        visible_parameters: List

):
    param_options_html = []
    additional_options_html = []
    param_input = None
    for param in parameters:
        if parameters[param]['selection'] == 'dropdown':
            param_input = selection(
                on_change=on_set_parameter,
                data=parameters[param]['options'],
                identifier=param,
                selected=kwargs[param]
            )

        elif parameters[param]['selection'] == 'dropdown_multi':
            selected = [kwargs[param]] if not isinstance(kwargs[param], list) else kwargs[param]
            param_input = multi_selection(
                on_change=on_set_parameter,
                data=parameters[param]['options'],
                identifier=param,
                selected=selected if selected is not [None] else ['None']
            )

        elif parameters[param]['selection'] in ['text', 'number']:
            param_input = user_input(
                input_type=parameters[param]['selection'],
                on_change=on_set_parameter,
                initial_val=str(kwargs[param]) if kwargs[param] is not None else 'None',
                identifier=param,
            )

        param_text = text_box(text=param, style=text_box_style(width="5cm"))

        element = html.div({
            "style": {
                "display": "flex",
                "flex-direction": "row",
                "align-items": "center",
            }},
            param_text,
            param_input
        )

        if param in visible_parameters:
            param_options_html.append(element)
        else:
            additional_options_html.append(element)

    return param_options_html, additional_options_html
