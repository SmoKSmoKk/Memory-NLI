from typing import Any, Callable, Dict, List

from idom import html

from nl2pandas.jupyter_interface.components.display import text_box
from nl2pandas.jupyter_interface.components.selection import multi_selection, selection
from nl2pandas.jupyter_interface.styles.styles import text_box_style


def get_scope_selection(
        scope_parameters: Dict[str, Dict[str, Any]],
        scope: Dict[str, Dict[str, Any]],
        on_set_scope_parameters: Callable,
        on_set_scope: Callable,
        kwargs: Dict[str, Any],
        visible_parameters: List

):
    scope_html = []
    additional_scope_html = []
    if scope_parameters == {} and scope == {}:
        pass
    else:
        for param in scope_parameters:
            scope_param_selection = None

            if scope_parameters[param]['selection'] == 'dropdown':
                scope_param_selection = selection(
                    on_change=on_set_scope_parameters,
                    data=scope_parameters[param]['options'],
                    identifier=param,
                    selected=kwargs[param] if kwargs[param] is not None else 'None',
                )

            elif scope_parameters[param]['selection'] == 'dropdown_multi':
                selected = [kwargs[param]] if not isinstance(kwargs[param], list) else kwargs[param]
                scope_param_selection = multi_selection(
                    on_change=on_set_scope_parameters,
                    data=scope_parameters[param]['options'],
                    identifier=param,
                    selected=selected if selected is not [None] else ['None']
                )

            param_text = text_box(text=param, style=text_box_style(width="5cm"))

            element = html.div({
                'id': param,
                "style": {
                    "display": "flex",
                    "flex-direction": "row",
                    "align-items": "center",
                }},
                param_text,
                scope_param_selection
            )
            if param in visible_parameters:
                scope_html.append(element)
            else:
                additional_scope_html.append(element)

        for element in scope:
            # need other options?
            if scope[element]['selection'] == 'dropdown':

                scope_selection = selection(
                    on_change=on_set_scope,
                    data=scope[element]['options'],
                    identifier=element,
                    selected=scope[element]['value'] if scope[element]['value'] is not None else 'None'
                )

                text = 'apply to columns' if element == 'subset_col' else 'apply to rows'
                param_text = text_box(text=text, style=text_box_style(width="5cm"))

                scope_element = html.div({
                    'id': element,
                    "style": {
                        "display": "flex",
                        "flex-direction": "row",
                        "align-items": "center",
                    }},
                    param_text,
                    scope_selection
                )

                if scope[element]['value'] is not None:
                    scope_html.append(scope_element)
                else:
                    additional_scope_html.append(scope_element)

    return scope_html, additional_scope_html
