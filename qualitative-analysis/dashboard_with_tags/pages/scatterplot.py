import dash
from dash import html, Input, Output, State, dcc
from assets import components, styles, data
import plotly.express as px
import json
from pathlib import Path

PLOT_TEMPLATE = 'plotly_dark'

d = data.d
dropdown_cols = data.col_names
dropdown_stats = data.list_of_stats

dropdown_first_row_content = [
    {'id': 'x',
     'Label': 'X',
     'options': dropdown_cols,
     'value': 'pri'},
    {'id': 'y',
     'Label': 'Y',
     'options': dropdown_cols,
     'value': 'pos'},
    {'id': 'color',
     'Label': 'Color',
     'options': dropdown_cols,
     'value': 'rel'},
    {'id': 'highlight-stimid',
     'Label': 'Highlight StimID',
     'options': ['None'] + list(range(1, 13)),
     'value': 'None'},
    {'id': 'plot-color-scale',
     'Label': 'Plot Color Scale',
     'options': styles.named_color_scales,
     'value': styles.default_color_scale},
    {'id': 'plot-using',
     'Label': 'Plot Using:',
     'options': dropdown_stats,
     'value': 'mean'}
]
dropdown_second_row_content = [
    {'id': 'condition-col-1',
     'options': dropdown_cols,
     'value': 'rel'},
    {'id': 'condition-stat-1',
     'options': dropdown_stats,
     'value': 'q75'},
    {'id': 'comparison-op',
     'options': ['<', '>'],
     'value': '<'},
    {'id': 'condition-col-2',
     'options': dropdown_cols,
     'value': 'rel'},
    {'id': 'condition-stat-2',
     'options': dropdown_stats,
     'value': 'q25'}
]
filter_button = [
    {
        'id': 'filter-button',
        'children': 'Apply Filter',
        'style': styles.white_button_style
    }
]
save_tag_button = [
    {
        'id': 'save-tag-button',
        'children': 'Save',
        'style': styles.white_button_style
    }
]

first_row_html = components.build_dropdown_row(dropdown_first_row_content)
second_row_html = components.build_dropdown_row(dropdown_second_row_content)
second_row_html += components.build_button_row(filter_button)
menus_html = [
                html.Div(style={'display': 'flex'}, 
                    children=first_row_html,),
                html.Div(style={'display': 'flex'}, 
                    children=second_row_html),
            ]
tags_html = ( [html.Div(id='tag-window', style={
    'height': 100, 'font_size': '10px', 'overflow':'scroll'})])

layout = html.Div(children=[
        html.Div(style={'display': 'flex'}, children=[
            html.Div(style={'width': '70%'}, 
                     children=menus_html),
            html.Div(style={'width': '10%'}, children=components.build_button_row(save_tag_button)),
            html.Div(style={'width': '20%'}, 
                     children=tags_html),
        ]),
        html.Div(style=dict(display='flex', marginBottom=0), children=[
        html.Div(style=dict(width='75%'), children=[dcc.Graph(id='plot'),]),
        html.Div(style=dict(width='25%'), children=[dcc.Markdown(id='hover-data')]),
        # html.Div(style=dict(width='20%'), children=[dcc.Markdown(id='click-data')]),
    ]),
        # html.Div(id='displayed-tags', children=''),
    ])
   
## HELPER FUNCTIONS
def apply_filter(button_n_clicks, condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2):
    # check if filter is valid
    valid_filter_condition = all([
        condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2])
    # On click, apply or remove filter (if valid)
    if button_n_clicks % 2 == 1:
        if valid_filter_condition:  
            filter_flag = 'on'
            query_str = f'{condition_col_1}_{condition_stat_1} {comparison_op} {condition_col_2}_{condition_stat_2}'
        else:
            filter_flag = 'invalid'
            query_str = None
    else:
        filter_flag = 'off'
        query_str = None
    return query_str, filter_flag

def update_button_style(filter_flag):
    if filter_flag == 'on':
        button_style = styles.blue_button_style
        button_text = 'Filter Applied'
    elif filter_flag == 'off':
        button_style = styles.white_button_style
        button_text = 'Apply Filter'
    elif filter_flag == 'invalid':
        button_style = styles.red_button_style
        button_text = 'Invalid Filter'
    return button_style, button_text

## FIRST CALLBACK
@dash.callback(
    Output('plot', 'figure'),
    Output('filter-button', 'style'),
    Output('filter-button', 'children'),
    [
        Input('x', 'value'),
        Input('y', 'value'),
        Input('color', 'value'),
        Input('highlight-stimid', 'value'),
        Input('highlighted-tag-name', 'data'),
        State('saved-tags', 'data'),
        Input('plot-color-scale', 'value'),
        Input('plot-using', 'value'),
        Input('condition-col-1', 'value'),
        Input('condition-stat-1', 'value'),
        Input('comparison-op', 'value'),
        Input('condition-col-2', 'value'),
        Input('condition-stat-2', 'value'),
        Input('filter-button', 'n_clicks'),
    ],
)
def update_graph(x_col, y_col, color_col, highlight_StimID, 
                 highlighted_tag_name, saved_tags,
                 color_scale, stat,
                 condition_col_1, condition_stat_1, comparison_op, 
                 condition_col_2, condition_stat_2, button_n_clicks
                 ):
    '''
    Parameters are all strings, taken from the dropdown menus.
    (except for button_n_clicks, which is an int)
    Returns: fig (the plot object), button_style (replaces button color), button_text (replaces button text)
    '''
    plotdf = d
    query_str, filter_flag = apply_filter(button_n_clicks, 
                    condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2)
    if query_str:
        plotdf = d.query(query_str)
    button_style, button_text = update_button_style(filter_flag)
    x = x_col + '_' + stat
    y = y_col + '_' + stat
    color = color_col + '_' + stat
    # Create figure
    fig = px.scatter(plotdf, 
        x=x, y=y, color=color, template=PLOT_TEMPLATE,
        color_continuous_scale=color_scale,)
    ## TURN ON CLICK TO SELECT
    fig.update_layout(clickmode='event+select')
    ## HIGHLIGHT SELECTED TAG
    if saved_tags and highlighted_tag_name != None:
        # saved_tags = json.loads(saved_tags)
        highlighted_tag_items = saved_tags[int(highlighted_tag_name)]
        fig.add_traces(
            px.scatter(plotdf.query(f'rowlabel in @highlighted_tag_items'), 
                    x=x, y=y, color=color)
                    .update_traces(marker_size=25).data
        )
    ## HIGHLIGHT SELECTED STIMID
    if highlight_StimID != 'None':
        fig.add_traces(
            px.scatter(plotdf.query(f'StimID == {highlight_StimID}'), 
                    x=x, y=y, color=color)
                    .update_traces(marker_size=25).data
        )
    ## AXES AND MARGINS OPTIONS
    # put x axis label on top
    fig.update_layout(xaxis=dict(title_standoff=5, side='top'),)
    # reduce margins
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=5),)
    return fig, button_style, button_text

## SECOND CALLBACK
# Update sidebar text when hovering on a point
@dash.callback(
    Output('hover-data', 'children'),
    [
        Input('plot', 'hoverData'),
    ]
)
def display_hover_data(hover_data):
    if hover_data is None:
        return ''
    
    point_index = hover_data['points'][0]['pointIndex']
    hover_text = d.iloc[point_index]['stimulus']
    
    return f'{hover_text}'

# THIRD CALLBACK
# Update tag window on select
@dash.callback(
    Output('tag-window', 'children'),
    [
        Input('plot', 'selectedData'),
    ],
    prevent_initial_call=True,
)
def update_tag_window(selected_data):
    if not selected_data:
        return ''
    pointrefs = [d.iloc[point['pointNumber']].rowlabel for point in selected_data['points']]
    return json.dumps(pointrefs)

## HELPERS
def read_tags_file():
    with open(data.TAGS_FILE_PATH, 'r') as f:
        tags = f.read()
    tags = json.loads(tags)
    if tags:
        return tags
    else:
        return [[]]
def write_tags_file(saved_tags):
    with open(data.TAGS_FILE_PATH, 'w') as f:
        f.write(saved_tags)

# FOURTH CALLBACK
# Update saved tags when Save button is clicked
@dash.callback(
    Output('saved-tags', 'data'),
    [
        State('tag-window', 'children'),
        State('saved-tags', 'data'),
        Input('save-tag-button', 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def save_tag(tag_window, saved_tags, n_clicks):
    # Load previously saved tags, or initialize if None
    if saved_tags:
        if type(saved_tags) is str:
            saved_tags = json.loads(saved_tags)
    else:
        saved_tags = read_tags_file()
    
    if tag_window:
        tag_window_list = json.loads(tag_window)
        saved_tags.append(tag_window_list)
        saved_tags = json.dumps(saved_tags)
        write_tags_file(saved_tags)
    return saved_tags


dash.register_page(__name__, path="/scatterplot", layout=layout)  