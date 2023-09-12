from typing import Callable, Dict

from idom import component, html

from nl2pandas.jupyter_interface.styles.styles import plain_button_style


@component
def button(
        handle_click: Callable = None,
        label: str = '',
        button_type: str = "button",
        value: str = "",
        style: Dict = None,
        is_disabled: bool = False,
        icon: str = "",
        icon_margin: str = '0px 7px 0px 7px',
        title: str = ''
):
    """
    A simple button component
    :return: a button component
    """

    if style is None:
        style = plain_button_style()

    icon_html = html.div()
    if icon != "":
        icon_html = {"class": icon, "style": {"margin": icon_margin}}

    return html.button(
        {
            "onClick": handle_click,
            "type": button_type,
            "value": value,
            "disabled": is_disabled,
            "style": style,
            'title': title,
        },
        html.div(icon_html),
        label,
    )


@component
def checkbox(handle_change: Callable, label: str, default_checked=False):

    return html.div(
        html.input(
            {
                "type": "checkbox",
                "defaultChecked": default_checked,
                "name": "checkbox",
                "onChange": lambda event: handle_change(event),
            }
        ),
        html.label(
            {
                "for": "checkbox",
                "style": {"margin": "5px"}
            },
            label
        ),
    )
