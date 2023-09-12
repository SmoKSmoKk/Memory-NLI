from typing import Callable, Dict, List

from idom import component, html

from nl2pandas.jupyter_interface.components.controls import button
from nl2pandas.jupyter_interface.components.display import score_bar
from nl2pandas.jupyter_interface.styles.styles import plain_button_style


@component
def selection_view(on_change: Callable, data: List[Dict]):
    """
    the first view of the pandas nli dialog flow, where the user selects a pandas action
    from a list of proposed options

    :param on_change: event handler
    :param data: list of dictionaries holding the action info of the suggested programs
    :return: a component containing the html of the selection view
    """

    button_score = []
    description = []
    for program in data:
        button_element = button(handle_click=on_change,
                                label=program['grounded_action'],
                                value=program['grounded_action'],
                                style=plain_button_style(width="8cm")
                                )

        score = score_bar(score=program['probability'])
        element = html.div({"style": {"width": "8cm"}}, score, button_element)
        button_score.append(element)

        doc = program['documentation'].rsplit("\n")[0]
        doc_element = html.p({"style": {"color": "grey", "margin-bottom": "3mm"}}, doc.rsplit("\n")[0])
        description.append(doc_element)

    return html.div(
        html.h4({"style": {"opacity": "0.9", "text-align": "left"}}, 'Program Selection: '),
        html.div((html.div(b, t) for b, t in zip(button_score, description)))
    )
