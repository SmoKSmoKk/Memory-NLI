from typing import Callable, Dict, List

from idom import component, html, use_state
from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner

from nl2pandas.jupyter_interface.components.controls import button
from nl2pandas.jupyter_interface.components.selection import search_field
from nl2pandas.jupyter_interface.styles.styles import blue_button_style, headline_style
from nl2pandas.jupyter_interface.views.refinement_view.df_selection import \
    get_dataframe_options
from nl2pandas.jupyter_interface.views.refinement_view.parameter_selection import \
    get_parameter_selection
from nl2pandas.jupyter_interface.views.refinement_view.scope_selection import \
    get_scope_selection


@component
def refinement_view(  # noqa: C901
        context: Context,
        on_apply_refinement: Callable,
        selected_program: Refiner,
        dataframes: List,
        active_df: str,
        past_actions: Dict,
):
    """
    Creates the GUI layout of the refinement view, where parameters can be edited,
    removed or added.

    :param context: the IPython context
    :param on_apply_refinement: the event handler for applying the parameters
    :param selected_program: the dictionary holding information about the selected program
    :param dataframes: a list of dataframes existing in the jupyter notebook
    :param active_df: the last used dataframe
    :param past_actions: Dictionary of past refinement actions

    :return: the html layout of the refinement view
    """
    # state parameters
    kwargs, set_kwargs = use_state(selected_program.refined_kwargs.copy())
    memory, set_memory = use_state(past_actions)

    df_instance, set_df_instance = use_state(active_df)

    df_display, set_df_display = use_state('block')
    scope_display, set_scope_display = use_state('block')
    param_display, set_param_display = use_state('block')

    show_more_param, set_show_more_param = use_state(False)
    show_more_scope, set_show_more_scope = use_state(False)
    show_docs, set_show_docs = use_state(False)
    show_suggestions, set_show_suggestions = use_state(True)

    parameters, scope_parameters = selected_program.get_scope_parameters()
    scope_parameters, set_scope_parameters = use_state(scope_parameters)
    scope, set_scope = use_state(selected_program.scope)

    search_options: Dict[str, str] = {}
    for key in parameters:
        search_options[key] = 'parameter'

    for key in scope_parameters:
        search_options[key] = 'scope'

    search_options['change DataFrame'] = 'df'
    search_options['change return instance'] = 'df'

    if 'subset_col' in scope:
        search_options['apply to colums'] = 'scope'
    if 'subset_row' in scope:
        search_options['apply to rows'] = 'scope'

    visible_parameters, set_visible_parameters = use_state([param for param in selected_program.kwargs.copy()])

    def on_set_scope_parameters(event, name):
        """
        Adds the changed scope parameter value to the keyword argument list

        :param event: the click event data
        :param name: the name of the parameters . Example: 'labels', 'axis'

        """

        # handle None:
        if event['target']['value'] == 'None':
            event['target']['value'] = None

        # new kwargs dict for update
        new_kwargs = kwargs.copy()

        if name == 'axis':
            selected_program.axis = event['target']['value']

            new_parameters, new_scope_parameters = selected_program.get_scope_parameters()
            set_scope_parameters(new_scope_parameters.copy())

            # set dependent scope kwarg values:
            for param in selected_program.df_dependencies:
                if param in kwargs:
                    new_kwargs[param] = selected_program.refined_kwargs[param]

        new_kwargs[name] = event['target']['value']

        set_kwargs(new_kwargs)
        set_memory({**memory, name: event['target']['value']})

    def on_set_scope(event, name):
        """
        Adds the changed scope values to the scope list

        :param event: the click event
        :param name: the name of the scope (either subset_col or subset_row)

        """
        value = event['target']['value']
        if value == "None":
            value = None
        scope_copy = scope.copy()
        scope_copy[name]['value'] = value
        set_scope(scope_copy)
        set_memory({**memory, name: value})

    def on_set_parameter(event, name):
        """
        Handles the parameters changed by the user.

        :param event: the click event
        :param name: the name of the parameter element
        """

        set_kwargs({**kwargs, name: event['target']['value']})
        set_memory({**memory, name: event['target']['value']})

    def on_set_df(event, name):
        """
        Sets the active dataframe and triggers the reevaluation of parameters
        that depend on the dataframe.

        :param event: the click event
        :param name: the name of the element that triggered the event
        """
        context.active_dataframe = event['target']['value']
        set_df_instance(context.active_dataframe)

        # only change return_df if it is default df:
        if selected_program.return_df in context.dataframes:
            selected_program.return_df = context.active_dataframe

        set_memory({**memory, 'active_dataframe': event['target']['value']})

        # set dependent scope kwarg values:
        new_kwargs = kwargs.copy()
        for param in selected_program.df_dependencies:
            if param in kwargs:
                new_kwargs[param] = selected_program.refined_kwargs[param]

        set_kwargs(new_kwargs)

    def on_set_return_df(event, name):
        selected_program.return_df = event['target']['value']
        set_memory({**memory, name: event['target']['value']})

    def on_show_more_param(event):
        set_show_more_param(not show_more_param)

    def on_show_more_scope(event):
        set_show_more_scope(not show_more_scope)

    def on_show_docs(event):
        set_show_docs(not show_docs)
        if not show_docs and show_suggestions:
            set_show_suggestions(False)

    def on_search(name, category):
        if category == 'df':
            set_df_display('block')
            set_scope_display('none')
            set_param_display('none')
            set_visible_parameters([])

        elif category == 'parameter':
            set_visible_parameters([name])
            set_df_display('none')
            set_scope_display('none')
            set_param_display('block')

            if name not in visible_parameters:
                set_visible_parameters([*visible_parameters, name])

        elif category == 'scope':
            set_df_display('none')
            set_scope_display('block')
            set_param_display('none')

            if name not in visible_parameters:
                set_visible_parameters([*visible_parameters, name])

    def on_select_suggestion(key, value):
        new_vis_param = visible_parameters.copy()
        if key not in visible_parameters:
            new_vis_param.append(key)
            set_visible_parameters(new_vis_param)

            if key in scope_parameters:
                set_scope_display('block')
            if key in parameters:
                set_param_display('block')

        if key in kwargs:
            set_kwargs({**kwargs, key: value})
        elif key in scope:
            scope_copy = scope.copy()
            scope_copy[key]['value'] = value
            set_scope(scope_copy)

    def reset():
        set_visible_parameters([param for param in selected_program.kwargs.copy()])
        set_df_display('block')
        set_param_display('block')
        set_scope_display('block')

    # ------------------ dataframe, scope and parameter selection-----------------------------------------------
    # instance selection
    df_selection_element, return_df_selection_element = get_dataframe_options(
        dataframes=dataframes,
        active_df=active_df,
        return_df=selected_program.return_df,
        on_set_df=on_set_df,
        on_set_return_df=on_set_return_df
    )

    # scope selection
    scope_html, additional_scope_html = get_scope_selection(
        scope_parameters=scope_parameters,
        scope=scope,
        on_set_scope_parameters=on_set_scope_parameters,
        on_set_scope=on_set_scope,
        kwargs=kwargs,
        visible_parameters=visible_parameters
    )

    # parameter selection
    param_options_html, additional_options_html = get_parameter_selection(
        parameters=parameters,
        on_set_parameter=on_set_parameter,
        kwargs=kwargs,
        visible_parameters=visible_parameters
    )

    # ------------------ html sections ---------------------------------------------------------------------------------
    # dataframe selection
    dataframe_selection = html.div(
        {'id': 'df', 'style': {'display': df_display}},
        html.h4({"style": headline_style()}, "DataFrame Instance: "),
        df_selection_element,
        return_df_selection_element,
    ),

    # scope selection
    scope_section = (html.div(
        {'id': 'scope', 'style': {'display': scope_display}},
        html.h4({"style": headline_style()}, "Scope: "),
        html.div(param for param in scope_html),
        (html.div(param for param in additional_scope_html) if show_more_scope else ""),

        (html.div(
            button(
                handle_click=on_show_more_scope,
                label=f'show {"less" if show_more_scope else "more"} scope options',
                style=blue_button_style(border="0px", text_align='left'),
                icon=f"{'fa fa-angle-up' if show_more_scope else 'fa fa-angle-down'}"
            )
        ) if additional_scope_html != [] else ""),

    ) if scope_html != [] or additional_scope_html != [] else "")

    # parameter selection
    parameter_section = (html.div(
        {'id': 'scope', 'style': {'display': param_display}},
        html.h4({"style": headline_style()}, "Parameters: "),
        html.div(param for param in param_options_html),

        (html.div(param for param in additional_options_html) if show_more_param else ""),

        (html.div(
            button(
                handle_click=on_show_more_param,
                label=f'show {"less" if show_more_param else "more"} parameters',
                style=blue_button_style(border="0px", text_align='left'),
                icon=f"{'fa fa-angle-up' if show_more_param else 'fa fa-angle-down'}"
            )
        ) if additional_options_html != [] else ""),

    ) if param_options_html != [] or additional_options_html != [] else "")

    return html.div(
        {"style": {
            "display": "flex",
            "flex-direction": "row",
            "align-items": "baseline",
        }
        },
        html.div(
            {'style': {'margin-right': '20px'}},
            dataframe_selection,
            scope_section,
            parameter_section,

            button(
                handle_click=lambda event: on_apply_refinement(event, kwargs, scope, memory),
                label='apply changes',
                style=blue_button_style()
            )
        ),
        html.div(
            {"style": {
                "margin-left": "auto",
                "margin-right": "5px",
                "display": "flex",
                "flex-direction": "column",
            }},
            html.div(
                {'name': 'outer_docs_and_search',
                 "style": {
                     "display": "flex",
                     "flex-direction": "row",
                     "align-items": "baseline",
                     "margin-left": "auto",
                 }},

                # read docs
                button(
                    handle_click=on_show_docs,
                    label='Hide docs' if show_docs else 'Read docs',
                    style=blue_button_style(
                        text_align='left',
                        width="4cm",
                    ),
                    icon="fa fa-question-circle"
                ),

                search_field(
                    on_option_select=on_search,
                    options=search_options,
                    reset=reset,
                    past_actions=past_actions,
                    on_select_suggestion=on_select_suggestion,
                ),
            ),
            html.div(
                {"style": {
                    "display": "block" if show_docs else "none",
                    "border-radius": "2px",
                    "white-space": "pre-wrap",
                    "padding": "5px",
                    "background": "#edf1ff",
                    "max-height": "8cm",
                    "overflow": "auto",
                    "box-shadow": '0 6px 12px rgba(0, 0, 0, 0.175)',
                    "min-width": "13cm",
                    "position": "relative",
                }},
                html.div(html.p(selected_program.program_info['documentation']))
            ),
        ),
    )
