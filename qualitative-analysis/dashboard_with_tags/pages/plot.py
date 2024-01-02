import dash
from dash import html, Input, Output, State, dcc
from assets import components, styles, data
import plotly.express as px
import json

PLOT_TEMPLATE = 'plotly_dark'


menus = {
    'x_col': {
        'id': 'x_col',
        'options': data.col_names,
        'value': 'pri',
    },
    'y_col': {
        'id': 'y_col',
        'options': data.col_names,
        'value': 'pos',
    },
    'color_col': {
        'id': 'color_col',
        'options': data.col_names,
        'value': 'rel',
    },
    
    'x_stat': {
        'id': 'x_stat',
        'options': data.stats,
        'value': 'Score',
    },
    'y_stat': {
        'id': 'y_stat',
        'options': data.stats,
        'value': 'Score',
    },
    'color_stat': {
        'id': 'color_stat',
        'options': data.stats,
        'value': 'Score',
    },
}


menus_html = [components.build_dropdown_menu(content) for content in menus.values()]
tags_html = []

layout = html.Div(children=[
        html.Div(style={'display': 'flex'}, children=[
            html.Div(style={'width': '60%'}, 
                     children=menus_html),
            # html.Div(style={'width': '10%'}, children=components.build_button_row(plot_button)),
            # html.Div(style={'width': '10%'}, children=components.build_button_row(save_tag_button)),
            html.Div(style={'width': '20%'}, 
                     children=tags_html),
        ]),
        html.Div(style=dict(display='flex', marginBottom=0), children=[
        html.Div(style=dict(width='70%'), children=[dcc.Graph(id='myplot'),]),
        html.Div(style=dict(width='5%'), children=[]),
        html.Div(style=dict(width='25%'), children=[dcc.Markdown(id='hovertext')]),
    ]),
    ])

plot_settings_inputs = [
    Input(menu_id, 'value')
    for menu_id in menus.keys()
]

@dash.callback(
    Output('plot_settings', 'data'),
    plot_settings_inputs,
)
def update_plot_settings(x_col, y_col, color_col,
                         x_stat, y_stat, color_stat):
    parse_stats = {
        'Score': '',
        'Rank': '_rank',
        'Rank Diff': '_rank_diff',
        'Mean Score': '_mean',
        'Mean Rank': '_rank_mean',
        'Mean Rank Diff': '_rank_diff_mean',
    }
    plot_settings = dict()
    plot_settings['x'] = x_col + parse_stats[x_stat]
    plot_settings['y'] = y_col + parse_stats[y_stat]
    plot_settings['color'] = color_col + parse_stats[color_stat]
    plot_settings['color_scale'] = 'sunsetdark'
    plot_settings['highlight'] = 'None'
    return plot_settings

@dash.callback(
    Output('myplot', 'figure'),
    [
        State('plot_settings', 'data'),
        Input('plot_settings', 'modified_timestamp'),
    ],
)
def update_graph(plot_settings, timestamp):
    if not plot_settings:
        return
    plotdf = data.d
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
        color_continuous_scale=color_scale)
    ## TURN ON CLICK TO SELECT
    fig.update_layout(clickmode='event+select')

    ## HIGHLIGHTING
    if highlight != 'None':
        fig.add_traces(
            px.scatter(plotdf.query(highlight), 
                    x=x, y=y, color=color)
                    .update_traces(marker_size=20).data
        )
    ## AXES AND MARGINS OPTIONS
    # put x axis label on top
    fig.update_layout(xaxis=dict(title_standoff=5, side='top'),)
    # reduce margins
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=5),)
    return fig

# Update sidebar text when hovering on a point
@dash.callback(
    Output('hovertext', 'children'),
    [
        Input('myplot', 'hoverData'),
    ]
)
def display_hover_data(hoverData):
    if hoverData is None:
        return ''
    point_index = hoverData['points'][0]['pointIndex']
    hovertext = data.d.iloc[point_index]['stimulus']
    return hovertext

dash.register_page(__name__, path="/plot", layout=layout)  