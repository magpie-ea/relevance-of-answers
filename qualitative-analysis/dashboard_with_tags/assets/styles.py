import plotly.express as px

# COLORS AND STYLES
default_color_scale = 'sunsetdark'
named_color_scales = list(px.colors.named_colorscales())
# style options for ALL buttons
button_style = {
    'transition-duration': '0.1s',
    'border-radius': '8px',
    'height': '37px',}
# styles for specific button states
white_button_style = dict(button_style.items() | {
    'background-color': 'black',
    'color': 'white',
    }.items())
blue_button_style = dict(button_style.items() | {
    'background-color': 'blue',
    'color': 'white',}.items())
red_button_style = dict(button_style.items() | {
    'background-color': 'red',
    'color': 'white',}.items())

dropdown_style = {'background-color':'white', 'color':'black'}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
