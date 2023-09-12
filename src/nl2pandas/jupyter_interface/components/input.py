from typing import Callable

from idom import component, html

from nl2pandas.jupyter_interface.styles.styles import selection_style


@component
def user_input(
        on_change: Callable,
        input_type: str = 'text',
        identifier: str = '',
        name: str = '',
        initial_val: str = '',
        title: str = ''
):

    def type_check(event):
        if input_type == 'number':
            if event['target']['value'] == '0':
                event['target']['value'] = 'None'
            elif event['target']['value'].isdigit():
                event['target']['value'] = int(event['target']['value'])
            else:
                event['target']['value'] = float(event['target']['value'])

        on_change(event, identifier)

    return html.input(
        {
            "type": input_type,
            "id": identifier,
            "name": name,
            "value": initial_val,
            "onChange": lambda event: type_check(event),
            "style": selection_style(padding='4px'),
            "title": title,
        }
    )
