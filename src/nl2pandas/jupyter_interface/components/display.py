from typing import Dict

from idom import component, html

from nl2pandas.jupyter_interface.styles.styles import text_box_style


@component
def bar(score: float):
    if score >= 70:
        # green
        return html.div({"style": {
            "background": "repeating-linear-gradient(45deg, #4dbd28, #4dbd28 6px, #3c931f 6px, #3c931f 12px)",
            "width": f"{score}%",
            "height": "100%",
        }}, html.p(" "))

    elif 60 <= score < 70:
        # yellow
        return html.div({"style": {
            "background": "repeating-linear-gradient(45deg, #ffd633, #ffd633 6px, #e6b800 6px, #e6b800 12px)",
            "width": f"{score}%",
            "height": "100%",
        }}, html.p(" "))

    elif 50 <= score < 60:
        # orange
        return html.div({"style": {
            "background": "repeating-linear-gradient(45deg, #ffad33, #ffad33 6px, #e68a00 6px, #e68a00 12px)",
            "width": f"{score}%",
            "height": "100%",
        }}, html.p(" "))

    elif score < 50:
        # red
        return html.div({"style": {
            "background": "repeating-linear-gradient(45deg, #ff6633, #ff6633 6px, #ff4000 6px, #ff4000 12px)",
            "width": f"{score}%",
            "height": "100%",
        }}, html.p(" "))


@component
def score_bar(score: float):

    # div holding the bar and the text elements
    s = html.div(
        {"style": {
            "display": "flex",
            "width": "min-content",
            "height": "100%",
            "flex-direction": "row",
            "align-items": "center",
        }
        },

        # outer div of color bar
        html.div(
            {"style": {
                "border": "1px solid grey",
                "width": "70px",
                "height": "13px",
                "border-radius": "2px"
            }
            },

            # color bar
            bar(score)
        ),

        html.p({"style": {"margin-left": "3px", "min-width": "max-content"}}, f'score: {score}%'))

    return s


@component
def text_box(text: str, style: Dict = None):
    if style is None:
        style = text_box_style()

    return html.div({
        "style": style
    }, html.p(text)
    )
