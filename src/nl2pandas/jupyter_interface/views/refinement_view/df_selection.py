from typing import Callable, List

from idom import html

from nl2pandas.jupyter_interface.components.display import text_box
from nl2pandas.jupyter_interface.components.input import user_input
from nl2pandas.jupyter_interface.components.selection import selection
from nl2pandas.jupyter_interface.styles.styles import text_box_style


def get_dataframe_options(
        dataframes: List,
        active_df: str,
        return_df: str,
        on_set_df: Callable,
        on_set_return_df: Callable,
):
    df_selection = selection(
        name='df_instance',
        on_change=on_set_df,
        data=dataframes,
        selected=active_df,
    )
    df_selection_text = text_box(text='DataFrame', style=text_box_style(width="5cm"))
    df_selection_element = html.div(
        {
            "style": {
                "display": "flex",
                "flex-direction": "row",
                "align-items": "center",
            }
        },
        df_selection_text,
        df_selection,
    )

    return_df_selection = user_input(
        name='return_df',
        input_type='text',
        on_change=on_set_return_df,
        initial_val=return_df,
        identifier='return_df',
    )
    return_df_selection_text = text_box(text='Return Instance', style=text_box_style(width="5cm"))

    return_df_selection_element = html.div({
        "style": {
            "display": "flex",
            "flex-direction": "row",
            "align-items": "baseline",
        }
    },
        return_df_selection_text,
        return_df_selection,
    )

    return df_selection_element, return_df_selection_element
