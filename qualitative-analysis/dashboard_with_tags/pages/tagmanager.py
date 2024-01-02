import dash
from dash import html, Output, Input, State, dcc
import dash_bootstrap_components as dbc
from assets import data
import json

layout = html.Div(children=[
    dbc.Label('Choose tag:'),
    dbc.RadioItems(id='tag-menu', inline=True),
    dbc.Label('Choose item:'),
    dbc.RadioItems(id='item-menu', inline=True),
    dcc.Markdown(id='displayed-item-text'),
])

@dash.callback(
    Output('tag-menu', 'options'),
    State('saved-tags', 'data'),
    Input('saved-tags', 'modified_timestamp'),
)
def update_tag_menu(saved_tags, timestamp):
    if not saved_tags:
         return []
    if type(saved_tags) is list:
        print(saved_tags)
    else:
        saved_tags = json.loads(saved_tags)
    tag_menu_options = [i for i, _ in enumerate(saved_tags)]
    tag_menu_options = {i: 'Tag ' + str(i) for i in tag_menu_options}
    return tag_menu_options

@dash.callback(
    Output('item-menu', 'options'),
    State('saved-tags', 'data'),
    Input('tag-menu', 'value'),
)
def update_item_menu(saved_tags, tag_menu_value):
    if not saved_tags or tag_menu_value is None:
        return []
    if type(saved_tags) is str:
        saved_tags = json.loads(saved_tags)
    chosen_tag_index = int(tag_menu_value)
    tag = saved_tags[chosen_tag_index]
    item_menu_options = tag
    return item_menu_options
@dash.callback(
    Output('highlighted-tag-name', 'data'),
    Input('tag-menu', 'value'),
)
def update_highlighted_tag(tag_menu_value):
    if tag_menu_value == 'None':
         return None
    return tag_menu_value

@dash.callback(
    Output('displayed-item-text', 'children'),
    Input('item-menu', 'value'),
)
def display_current_item(item_menu_value):
    stim_text = data.items.query('rowlabel == @item_menu_value').stimulus
    return stim_text


dash.register_page(__name__, path="/tagmanager", layout=layout)