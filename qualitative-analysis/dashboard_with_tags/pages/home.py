import dash
from dash import html

layout = html.Div('Interactive Scatter Plot and Tag Manager')


dash.register_page(__name__, path="/", layout=layout)
