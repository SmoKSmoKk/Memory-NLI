# loading external css in jupyter notebook is non-trivial, therefore styles are saved in this file
# and applied to html components when necessary

def plain_button_style(
        border: str = "1px solid black",
        background_color: str = "",
        border_radius: str = "2px",
        width: str = "None",
        min_width: str = "4cm",
        max_width: str = "8cm",
        margin_bottom: str = "5px",
        margin_top: str = "5px",
        margin_left: str = "",
        margin_right: str = "5px",
        box_shadow: str = "",
        color: str = "black",
        padding: str = "4px",
        text_align: str = "center",
        position: str = '',
        right: str = '',
        overflow: str = 'auto',
):
    """
    Button with default black outline, rounded corners and shadow
    """

    return {
        "background-color": background_color,
        "border": border,
        "border-radius": border_radius,
        "width": width,
        "min-width": min_width,
        "max-width": max_width,
        "margin-bottom": margin_bottom,
        "margin-top": margin_top,
        "margin-left": margin_left,
        "margin-right": margin_right,
        "box-shadow": box_shadow,
        "color": color,
        "padding": padding,
        "text-align": text_align,
        "position": position,
        "right": right,
        "overflow": overflow,
    }


def blue_button_style(
        border: str = "2px solid #0060df",
        width: str = "8cm",
        text_align: str = 'center',
        background_color: str = 'inherit',
        min_width: str = "4cm",
        padding: str = "4px",
):
    """
    creates a button with blue border and writing
    """
    return plain_button_style(
        border=border,
        background_color=background_color,  # #3ca1c3
        width=width,
        color="#0060df",
        box_shadow="none",
        text_align=text_align,
        min_width=min_width,
        padding=padding,
    )


def headline_style(opacity: str = "0.9", text_align: str = "left"):
    """
    Sets the style for headline elements

    """
    return {"opacity": opacity, "text-align": text_align}


def text_box_style(
        background_color: str = "#fdf6e3",
        border: str = "1px solid black",
        border_radius: str = "2px",
        width: str = "",
        min_width: str = "4cm",
        margin_bottom: str = "5px",
        margin_top: str = "5px",
        margin_left: str = "",
        margin_right: str = "5px",
        text_align: str = "left",
        font_family: str = '"Helvetica Neue", Helvetica, Arial, sans-serif"',
        padding: str = "4px",
        box_shadow: str = "2px 2px 2px grey",
        overflow: str = 'auto',
):
    """
    The style of a text box element

    """
    return {
        "background-color": background_color,
        "border": border,
        "border-radius": border_radius,
        "min-width": min_width,
        "margin-bottom": margin_bottom,
        "margin-top": margin_top,
        "margin-right": margin_right,
        "margin-left": margin_left,
        "text-align": text_align,
        "font-family": font_family,
        "padding": padding,
        "box-shadow": box_shadow,
        "width": width,
        "overflow": overflow,
    }


def selection_style(
        border: str = "1px solid black",
        background_color: str = "",
        border_radius: str = "2px",
        min_width: str = "6cm",
        margin_bottom: str = "5px",
        margin_top: str = "5px",
        margin_left: str = "5px",
        margin_right: str = "",
        box_shadow: str = "",
        color: str = "black",
        padding: str = "6px"
):
    """
       Dropdown selection style
    """

    return {
        "background-color": background_color,
        "border": border,
        "border-radius": border_radius,
        "min-width": min_width,
        "margin-bottom": margin_bottom,
        "margin-top": margin_top,
        "margin-left": margin_left,
        "margin-right": margin_right,
        "box-shadow": box_shadow,
        "color": color,
        "padding": padding
    }


def dropdown_style(
        border: str = "1px solid black",
        background_color: str = "",
        border_radius: str = "2px",
        min_width: str = "6cm",
        min_height: str = "",
        max_height: str = '4cm',
        margin_bottom: str = "5px",
        margin_top: str = "",
        margin_left: str = "5px",
        margin_right: str = "",
        box_shadow: str = "",
        color: str = "black",
        padding: str = "",
        z_index: str = '999',
        position: str = 'absolute',
        overflow: str = 'auto'
):
    """
       Dropdown selection style
    """
    return {
        "background-color": background_color,
        "border": border,
        "border-radius": border_radius,
        "min-width": min_width,
        "min-height": min_height,
        "max-height": max_height,
        "margin-bottom": margin_bottom,
        "margin-top": margin_top,
        "margin-left": margin_left,
        "margin-right": margin_right,
        "box-shadow": box_shadow,
        "color": color,
        "padding": padding,
        "z-index": z_index,
        "position": position,
        "overflow": overflow,
    }


def hover_style(
        background_color: str = '#bfbfbf',
        color: str = '',
        class_name: str = 'hover_class'
):

    return f"""
    .{class_name}:hover {{
        background-color: {background_color};
        color: {color};
    }}
    """
