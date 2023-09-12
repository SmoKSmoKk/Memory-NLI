from typing import Callable, Dict, List

import idom
from idom import component, html, use_state

from nl2pandas.jupyter_interface.components.controls import button
from nl2pandas.jupyter_interface.components.selection import accordion_options
from nl2pandas.jupyter_interface.styles.styles import (blue_button_style, hover_style,
                                                       text_box_style)


@component
def unsure_view(
        action_utterance: Dict[str, List],
        on_select: Callable,
):
    show, set_show = use_state(False)
    grounded_action, set_grounded_action = use_state([key for key in action_utterance.keys()])
    search_options, set_search_options = use_state([key for key in action_utterance.keys()])

    # get style for the dropdown element and search field
    search_style = text_box_style(
        background_color='',
        box_shadow='',
        min_width='7.5cm',
        margin_left='5px',
    )

    def on_search(event):
        value = event['target']['value']
        value = value.lower()
        new_options = grounded_action.copy()

        # search utterances and actions
        for param in grounded_action:
            if value not in param.lower():
                in_utterances = False
                for utterance in action_utterance[param]:
                    if value in utterance.lower():
                        in_utterances = True

                if not in_utterances:
                    new_options.remove(param)

        set_search_options(new_options)

    input_html = html.input({
        'onKeyUp': on_search,
        'style': search_style,
        'type': 'text',
        'placeholder': 'search',
    }),

    options_html = html.div(
        {'style': {'margin-top': '10px'}},
        [html.div(
            {'class': "hover_class"},
            idom.html.style(hover_style()),
            accordion_options(
                label=label,
                search_options=search_options,
                child_buttons=action_utterance[label],
                on_select=on_select,
            )

        ) for label in grounded_action]
    ),

    section = html.div(
        input_html,
        options_html,
    )

    def on_click_show(event):
        set_show(not show)

    message = html.div(
        html.h3("No Match Found"),
        html.div(
            {'style': {'margin-top': '20px'}},
            html.h4("Try one of the following:"),
            html.ul(
                html.li("Check that values such as column names are written in quotation marks"),
                html.li("Rephrase the prompt"),
                html.li("Check the available methods to see if the function is implemented."),
                html.li("Select an example sentence and edit the placeholder in the notebook cell"),
            )),
        html.div(
            {'style': {'margin': '20px'}},
            button(
                handle_click=on_click_show,
                label=f"{'Hide' if show else 'Show'} available methods",
                icon=f"{'fa fa-angle-up' if show else 'fa fa-angle-down'}",
                style=blue_button_style(),
            ),
            html.div(
                {'style': {
                    'display': 'block' if show else 'none',
                    'background-color': '#edf1ff',
                    'height': '9cm',
                    'overflow': 'auto',
                    'width': '8cm',
                    'box-shadow': '0 6px 12px rgba(0, 0, 0, 0.175)',
                }},
                section,
            )
        )
    )
    return message
