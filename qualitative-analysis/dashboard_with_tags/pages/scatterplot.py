import dash
from dash import html, Input, Output, State, dcc
from assets import components, styles, data
import plotly.express as px
import json

PLOT_TEMPLATE = 'plotly_dark'

dropdown_cols = data.col_names
dropdown_item_stats = data.list_of_stats
response_stats = [
    {'value': '', 'label': 'Raw', 'disabled': False},
    {'value': '_rank', 'label' : 'Rank', 'disabled': False}]

dropdown_settings = [
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
]
dropdown_item_stats = [
      {'id': 'x-stat-items',
     'Label': 'X Stat:',
     'options': dropdown_item_stats,
     'value': 'mean'},
    {'id': 'y-stat-items',
     'Label': 'Y Stat:',
     'options': dropdown_item_stats,
     'value': 'mean'},
    {'id': 'color-stat-items',
     'Label': 'Color Stat:',
     'options': dropdown_item_stats,
     'value': 'mean'},
]
dropdown_response_stats = [
      {'id': 'x-stat-responses',
     'Label': 'X Stat:',
     'options': response_stats,
     'value': ''},
    {'id': 'y-stat-responses',
     'Label': 'Y Stat:',
     'options': response_stats,
     'value': ''},
    {'id': 'color-stat-responses',
     'Label': 'Color Stat:',
     'options': response_stats,
     'value': ''},
    {'id': 'plot-items-or-responses',
     'Label': 'Plot Items or Responses',
     'options': ['Items', 'Responses'],
     'value': 'Items',
    }
]


dropdown_filter_content = [
    {'id': 'condition-col-1',
     'options': dropdown_cols,
     'value': 'rel'},
    {'id': 'condition-stat-1',
     'options': dropdown_item_stats,
     'value': 'q75'},
    {'id': 'comparison-op',
     'options': ['<', '>'],
     'value': '<'},
    {'id': 'condition-col-2',
     'options': dropdown_cols,
     'value': 'rel'},
    {'id': 'condition-stat-2',
     'options': dropdown_item_stats,
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
plot_button = [
    {
        'id': 'plot-button',
        'children': 'Plot',
        'style': styles.white_button_style
    }
]

settings_html = components.build_dropdown_row(dropdown_settings)
item_stats_html = components.build_dropdown_row(dropdown_item_stats)
response_stats_html = components.build_radio_row(dropdown_response_stats)
filter_html = components.build_dropdown_row(dropdown_filter_content)
filter_html += components.build_button_row(filter_button)
menus_html = [
                html.Div(style={'display': 'flex'}, 
                    children=settings_html,),
                html.Div(style={'display': 'flex'},
                    id='item-stats-dropdown',
                    children=item_stats_html),
                html.Div(style={'display': 'flex'},
                    id='response-stats-menu',
                    children=response_stats_html),
                html.Div(style={'display': 'none'}, 
                    children=filter_html),
            ]
tags_html = ( [html.Div(id='tag-window', style={
    'height': 100, 'font_size': '10px', 'overflow':'scroll'})])

layout = html.Div(children=[
        html.Div(style={'display': 'flex'}, children=[
            html.Div(style={'width': '60%'}, 
                     children=menus_html),
            html.Div(style={'width': '10%'}, children=components.build_button_row(plot_button)),
            html.Div(style={'width': '10%'}, children=components.build_button_row(save_tag_button)),
            html.Div(style={'width': '20%'}, 
                     children=tags_html),
        ]),
        html.Div(style=dict(display='flex', marginBottom=0), children=[
        html.Div(style=dict(width='70%'), children=[dcc.Graph(id='plot'),]),
        html.Div(style=dict(width='5%'), children=[]),
        html.Div(style=dict(width='25%'), children=[dcc.Markdown(id='hover-data')]),
    ]),
    ])

@dash.callback(
    Output('plot-settings', 'data'),
    [
        Input('x', 'value'),
        Input('x-stat-items', 'value'),
        Input('x-stat-responses', 'value'),
        Input('y', 'value'),
        Input('y-stat-items', 'value'),
        Input('y-stat-responses', 'value'),
        Input('color', 'value'),
        Input('color-stat-items', 'value'),
        Input('color-stat-responses', 'value'),
        Input('plot-color-scale', 'value'),
        Input('plot-items-or-responses', 'value'),
        Input('highlight-stimid', 'value'),
        Input('highlighted-tag-name', 'data'),
        State('saved-tags', 'data'),
    ],
)
def update_plot_settings(x_col, x_stat_items, x_stat_responses, 
                         y_col, y_stat_items, y_stat_responses, 
                         color_col, color_stat_items, color_stat_responses, 
                         color_scale, items_or_responses, 
                         highlight_StimID, highlighted_tag_name, saved_tags):
    plot_settings = {}
    if items_or_responses == 'Items':
        x = x_col + '_' + x_stat_items
        y = y_col + '_' + y_stat_items
        color = color_col + '_' + color_stat_items
    else:
        x = x_col + x_stat_responses
        y = y_col + y_stat_responses
        color = color_col + color_stat_responses
    if highlighted_tag_name:
        highlighted_tag_items = saved_tags[int(highlighted_tag_name)]
        plot_settings['highlight'] = f'StimID == {highlight_StimID}'
    else:
        plot_settings['highlight'] = f'StimID == {highlight_StimID}'
    plot_settings['items_or_responses'] = items_or_responses
    plot_settings['x'] = x
    plot_settings['y'] = y
    plot_settings['color'] = color
    plot_settings['color_scale'] = color_scale
    
    return plot_settings

# 
# @dash.callback(
#     Output('item-stats-dropdown', 'disabled'),
#     Output('response-stats-menu', 'options'),
#     Input('plot-settings', 'modified_timestamp'),
#     State('plot-settings', 'data'),
#     State('response-stats-menu', 'options')
# )
# def update_dropdowns(timestamp, plot_settings, response_stats_menu_options):
#     new_response_options = response_stats_menu_options
#     if plot_settings['items_or_responses'] == 'Items':
#         item_stats_disabled = False
#     else:
#         new_response_options[0]['disabled'] = False
#         new_response_options[1]['disabled'] = False
#         item_stats_disabled = True
#     return item_stats_disabled, new_response_options

# Re-generate plot when settings are modified
@dash.callback(
    Output('plot', 'figure'),
    [
        State('plot-settings', 'data'),
        Input('plot-settings', 'modified_timestamp'),
        Input('plot-button', 'n_clicks'),
    ],
)
def update_graph(plot_settings, timestamp, n_clicks):
    if not plot_settings:
        return
    if plot_settings['items_or_responses'] == 'Responses':
        plotdf = data.responses
    else:
        plotdf = data.items
    x = plot_settings['x']
    y = plot_settings['y']
    color = plot_settings['color']
    color_scale = plot_settings['color_scale']
    highlight = plot_settings['highlight']
    # Create figure
    fig = px.scatter(plotdf, 
        x=x, 
        y=y, 
        color=color, 
        template=PLOT_TEMPLATE,
        color_continuous_scale=color_scale,)
    ## TURN ON CLICK TO SELECT
    fig.update_layout(clickmode='event+select')
    ## HIGHLIGHTING
    if highlight != 'None':
        fig.add_traces(
            px.scatter(plotdf.query(highlight), 
                    x=x, y=y, color=color)
                    .update_traces(marker_size=25).data
        )
    ## AXES AND MARGINS OPTIONS
    # put x axis label on top
    fig.update_layout(xaxis=dict(title_standoff=5, side='top'),)
    # reduce margins
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=5),)
    return fig

# Update sidebar text when hovering on a point
@dash.callback(
    Output('hover-data', 'children'),
    [
        Input('plot', 'hoverData'),
        State('plot-items-or-responses', 'value'),
    ]
)
def display_hover_data(hover_data, items_or_responses):
    if hover_data is None:
        return ''
    
    point_index = hover_data['points'][0]['pointIndex']
    if items_or_responses == 'Items':
        hover_text = data.get_stim_from_item(point_index)
    else:
        hover_text = data.get_stim_from_response(point_index)
    return f'{hover_text}'

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
    rowlabels = list([data.get_rowlabel_from_item(point['pointNumber']) for point in selected_data['points']])
    return json.dumps(rowlabels)

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
    if tag_window:
        tag_window_list = json.loads(tag_window)
        saved_tags.append(tag_window_list)
    return saved_tags


dash.register_page(__name__, path="/scatterplot", layout=layout)  