from typing import Callable, Dict, List, Collection

import idom.html
from idom import component, event, html, use_effect, use_state

from nl2pandas.jupyter_interface.components.controls import button
from nl2pandas.jupyter_interface.styles.styles import (dropdown_style, hover_style,
                                                       plain_button_style,
                                                       selection_style, text_box_style)


def type_check(selected, options):
    for value in options:
        if selected == str(value):
            if isinstance(value, int):
                selected = int(selected)
            if isinstance(value, float):
                selected = float(selected)
    return selected


@component
def selection(
        on_change: Callable,
        data: List,
        identifier: str = '',
        selected: str = '',
        style: Dict = None,
        name: str = '',
):
    """
    Selection component with dropdown list.
    :return: selection component
    """
    options = [html.option({"value": i, "selected": True if str(i) == str(selected) else False}, i) for i in data]

    if style is None:
        style = selection_style()

    def on_select(event):
        event['target']['value'] = type_check(selected=event['target']['value'], options=data)
        on_change(event, identifier)

    return html.select(
        {
            "onChange": lambda event: on_select(event),
            "id": identifier,
            "style": style,
            'name': name,
        },
        options
    )


@component
def multi_selection(
        on_change: Callable,
        data: List,
        selected: List,
        identifier: str = '',
        style: Dict = None
):
    """
    Selection element with multi select possibilities.

    :param on_change: the event handler for when an option is selected
    :param data: the options to chose from
    :param selected: the initially selected values
    :param identifier: selection element id
    :param style: a css style dictionary

    :return: a dropdown multiselect html element
    """
    selected_list, set_selected_list = use_state(selected)

    display_selection, set_display_selection = use_state(', '.join(map(str, selected_list.copy())))
    show, set_show = use_state('none')

    use_effect(set_selected_list(selected), dependencies=[selected])
    # dropdown icon
    icon: Dict[str, Collection[str]] = {}

    if show == 'block':
        icon = {"class": "fa fa-angle-up", "style": {"margin": "4px", 'float': 'right'}}
    elif show == 'none':
        icon = {"class": "fa fa-angle-down", "style": {"margin": "4px", 'float': 'right'}}

    # get style for opening button
    if style is None:
        style = plain_button_style(
            margin_bottom='0px',
            margin_left='5px',
            min_width='6cm',
            text_align='left'
        )

    # get style for the dropdown element
    drop_style = dropdown_style()
    drop_style['display'] = show

    def on_select(event):
        """
        Adds or removes a clicked element from the list of selected elements.
        If None is clicked, all elements are removed.

        :param event: the click event
        """
        # avoid mutability rendering problems through copying.
        new_selected = selected_list.copy()

        name = event['target']['value']
        name = type_check(selected=name, options=data)

        # handle selected element
        if 'None' in new_selected:
            new_selected.remove('None')

        if None in new_selected:
            new_selected.remove(None)

        if name == 'None':
            new_selected = ['None']

        elif name in new_selected:
            new_selected.remove(name)

        else:
            new_selected.append(name)

        if not new_selected:
            new_selected = ['None']

        if len(new_selected) == 1:
            event['target']['value'] = new_selected[0]
        else:
            event['target']['value'] = new_selected

        # handle state events
        on_change(event, identifier)
        set_selected_list(new_selected)
        set_display_selection(', '.join(map(str, new_selected.copy())))

    def on_click(event):
        if show == 'none':
            set_show('block')
        else:
            set_show('none')

    def close_dropdown(event):
        set_show('none')

    # html element with dropdown
    multi_select = html.div(

        {'onBlur': close_dropdown},

        html.button({
            'onClick': on_click,
            'style': style,
            'name': 'multi_select ' + display_selection,
        },
            html.div(icon),
            f"{', '.join(map(str, selected_list.copy()))}",
        ),

        html.div(
            {'style': drop_style},

            [html.div(
                html.button({
                    'name': label,
                    'value': label,
                    'onMouseDown': event(lambda event: None, prevent_default=True, stop_propagation=True),
                    'onClick': on_select,
                    'style': {
                        'width': '100%',
                        'border': 'none',
                        'text-align': 'left',
                        'background-color': '#1f2227' if label in selected_list else '#1a1d21',
                        'color': 'white'
                    }}, label
                )
            ) for label in data]
        )
    )

    return multi_select


@component
def suggestions(
        past_actions: Dict,
        on_select_suggestion: Callable,
        visible_actions: List,
):
    def on_select_past_action(event):
        key = event['target']['value']
        on_select_suggestion(key, past_actions[key])

    suggestions_html = html.div(
        html.div(
            {'style': {
                'border-radius': '2px',
                'margin-right': '5px',
                'border-bottom': '1px solid #eeeeee'
            }},
            [html.div(
                {'class': "hover_class"},
                idom.html.style(hover_style()),
                html.button({
                    'name': 'suggestions_' + key,
                    'value': key,
                    'onMouseDown': event(lambda event: None, prevent_default=True, stop_propagation=True),
                    'onClick': on_select_past_action,
                    'class': 'hover_class',
                    'style': {
                        'display': 'block' if key in visible_actions else 'none',
                        'width': '100%',
                        "border": "none",
                        'text-align': 'left',
                        'line-height': '2',
                        'margin_bottom': '1px',
                        'background-color': 'inherit',
                    }},
                    key + " = " + str(value)
                )
            ) for key, value in past_actions.items()],
        ),
    )
    return suggestions_html


@component
def search_field(
        on_option_select: Callable,
        options: Dict,
        reset: Callable = None,
        past_actions: Dict = {},
        on_select_suggestion: Callable = None,
):
    search_options, set_search_options = use_state([key for key in options.keys()])
    search_actions, set_search_actions = use_state([key for key in past_actions.keys()])

    selected, set_selected = use_state(None)
    show, set_show = use_state('none')

    # get style for the dropdown element and search field
    search_style = text_box_style(
        background_color='',
        box_shadow='',
        min_width='4.5cm',
        margin_left='5px',
        margin_bottom='0px',
        margin_top='0px',
    )

    # close dropdown on selection
    def on_select_index(event):
        name = event['target']['value']
        if name:
            category = options[name]
            on_option_select(name, category)

        set_selected(event['target']['value'])

    def on_search(event):
        value = event['target']['value']

        value = value.lower()
        new_options = [key for key in options.keys()]
        new_actions = [key for key in past_actions.keys()]

        # search parameters
        for param in options.keys():
            if value and value not in param.lower():
                new_options.remove(param)

        # search suggestions
        for param in past_actions.keys():
            if value and value not in param.lower():
                new_actions.remove(param)

        set_search_options(new_options.copy())
        set_search_actions(new_actions.copy())

    def on_reset(event):
        reset()
        set_selected(None)
        set_search_actions([key for key in past_actions.keys()])
        set_search_options([key for key in options.keys()])

    def on_click(event):
        if show == 'none':
            set_show('block')

    def close_dropdown(event):
        set_show('none')

    index_html = html.div(
        {'name': 'dropdown_div',
         'style': {
             'display': show,
             'margin': '0px 5px 5px 5px',
             'box-shadow': '0 6px 12px rgba(0, 0, 0, 0.175)',
             'position': 'absolute',
             'z-index': '99',
             'background-color': 'white',
             'width': '4.5cm',
             'max-height': '10cm',
             'overflow': 'auto',
         }},
        suggestions(
            past_actions=past_actions,
            on_select_suggestion=on_select_suggestion,
            # show_suggestions=show_suggestions,
            visible_actions=search_actions,
        ),

        html.div(
            {'style': {
                'margin-top': '10px',
            }},
            [html.div(
                {'class': "hover_class"},
                idom.html.style(hover_style()),
                html.button({
                    'name': label,
                    'value': label,
                    'onMouseDown': event(lambda event: None, prevent_default=True, stop_propagation=True),
                    'onClick': on_select_index,
                    'style': {
                        'display': 'block' if label in search_options else 'none',
                        'width': '100%',
                        'border': 'none',
                        'text-align': 'left',
                        'background-color': 'inherit',
                        'color': 'black',
                        'line-height': '2',
                    }}, label
                )
            ) for label in options.keys()]
        ),
    )
    search = html.div(
        {'name': 'parent', 'onBlur': close_dropdown},

        html.div(
            {'name': 'search_and_reset', 'style': {
                "position": "relative",
                "display": "inline-block"}
             },
            html.input({
                'onClick': on_click,
                'onKeyUp': on_search,
                'style': search_style,
                'type': 'text',
                'placeholder': 'search',
                'value': selected
            }),
            button(
                icon="fa fa-times",
                handle_click=on_reset,
                icon_margin='',
                title='reset view',
                style=plain_button_style(
                    border='none',
                    min_width='',
                    background_color='inherit',
                    padding='none',
                    margin_right='7px',
                    margin_bottom='0px',
                    margin_top='5px',
                    color='rgb(113, 113, 113)',
                    position='absolute',
                    right='0')
            )
        ),
        index_html,
    )
    return search


@component
def accordion_options(
        label: str,
        search_options: List,
        child_buttons: List,
        on_select: Callable,
):
    show_utterance, set_show_utterance = use_state(False)

    def on_click(event):
        set_show_utterance(not show_utterance)

    return html.div(
        html.button({
            'name': label,
            'value': label,
            'onMouseDown': event(lambda event: None, prevent_default=True, stop_propagation=True),
            'onClick': lambda event: on_click(event),
            'style': {
                'display': 'block' if label in search_options else 'none',
                'width': '100%',
                'border': 'none',
                'text-align': 'left',
                'background-color': 'inherit',
                'color': 'black',
                'line-height': '2',
            }}, label
        ),
        html.div(
            {'style': {
                # 'height': '2cm',
                'background-color': '#f8f8f8',
                'display': 'block' if show_utterance else 'none',
            }},
            [html.div(
                {'class': "hover_class"},
                idom.html.style(hover_style()),
                html.button({
                    'name': utterance_label,
                    'value': utterance_label,
                    'onMouseDown': event(lambda event: None, prevent_default=True, stop_propagation=True),
                    'onClick': on_select,
                    'style': {
                        'width': '100%',
                        'border': 'none',
                        'text-align': 'left',
                        'background-color': 'inherit',
                        'color': 'black',
                        'line-height': '2',
                    }}, utterance_label
                ),
            ) for utterance_label in child_buttons]
        )
    )
