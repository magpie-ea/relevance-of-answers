import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, State, Output
from assets import styles, components, data
import json


app = Dash(__name__, 
        use_pages=True, 
        external_stylesheets=[dbc.themes.DARKLY],
        suppress_callback_exceptions=True,)

pages = {
    # page title: page url
    'Home': '/',
    'Plot': '/plot',
    # 'Scatter Plot': '/scatterplot',
    'Tag Manager': '/tagmanager',
}

initial_plot_settings = {
    'highlight': 'None',
    'items_or_responses': 'Items',
    'x': 'pri',
    'y': 'pos',
    'color': 'rel',
    'color_scale': 'sunsetdark',
}

def read_tags_file():
    with open(data.TAGS_FILE_PATH, 'r') as f:
        tags = f.read()
    tags = json.loads(tags)
    if tags:
        return tags
    else:
        return [[]]
app.layout = html.Div([
    dcc.Store(id='saved-tags',
              data=read_tags_file()),
    dcc.Store(id='highlighted-tag-name'),
    dcc.Store(id='filter-settings'),
    # dcc.Store(id='plot-settings',
            #   data=initial_plot_settings),
    dcc.Store(id='plot_settings',
              data=initial_plot_settings),
    dcc.Store(id='placeholder'),
    dcc.Location(id="url"), 
    components.build_navbar(brand='Plots', pages=pages), 
    dash.page_container])

@dash.callback(
        Output('placeholder', 'data'),
        State('saved-tags', 'data'),
        Input('saved-tags', 'modified_timestamp'),
)
def write_tags_file(saved_tags, timestamp):
    with open(data.TAGS_FILE_PATH, 'w') as f:
        f.write(json.dumps(saved_tags))
    return None


if __name__ == "__main__":
    app.run_server(host='127.0.0.1', port='8888', debug=True)