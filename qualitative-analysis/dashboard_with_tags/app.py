import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, State, Output
from assets import styles, components
from pathlib import Path
import json


app = Dash(__name__, 
        use_pages=True, 
        external_stylesheets=[dbc.themes.DARKLY],
        suppress_callback_exceptions=True,)

pages = {
    # page title: page url
    'Home': '/',
    'Scatter Plot': '/scatterplot',
    'Tag Manager': '/tagmanager',
    # 'Linked Plots': '/linkedplots',
}

app.layout = html.Div([
    dcc.Store(id='saved-tags'),
    dcc.Store(id='highlighted-tag-name'),
    dcc.Location(id="url"), 
    components.build_navbar(brand='Plots', pages=pages), 
    dash.page_container])

# @dash.callback(
#         Output('saved-tags', 'data')
# )
# def read_tags_file():
#     with open(TAGS_FILE_PATH, 'w') as f:
#         return json.loads(f.read())

# @dash.callback(
#         State('saved-tags', 'data'),
#         Input('saved-tags', 'modified_timestamp'),
# )
# def write_tags_file(saved_tags, timestamp):
#     with open(TAGS_FILE_PATH, 'w') as f:
#         f.write(saved_tags)

if __name__ == "__main__":
    app.run(port=8888, debug=True)