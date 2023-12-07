import dash
from dash import dcc, html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
from preprocessing import preprocessed_data, dropdown_cols, dropdown_stats

d = preprocessed_data

# COLORS AND STYLES
default_color_scale = 'viridis'
named_color_scales = list(px.colors.named_colorscales())
# style options for ALL buttons
button_style = {
    'transition-duration': '0.1s',
    'border-radius': '8px',
    'height': '37px',}
# styles for specific button states
white_button_style = dict(button_style.items() | {
    'background-color': 'white',
    'color': 'black',
    }.items())
blue_button_style = dict(button_style.items() | {
    'background-color': 'blue',
    'color': 'white',}.items())
red_button_style = dict(button_style.items() | {
    'background-color': 'red',
    'color': 'white',}.items())

## DASH APP CODE
# The layout div has three child divs. The first div
# has the first row of dropdown menus, the second div
# has the second row of dropdown menus, and the last div
# contains the plot and sidebar text.
app = dash.Dash(__name__)
app.layout = html.Div([
    ## FIRST ROW OF DROPDOWN MENUS
    # create three dropdown menus in a single row
    # for setting the X, Y, and Color in the scatterplot
    html.Div(style=dict(display='flex'), children=[
        html.Div(style=dict(width='15%'), children=[
            html.Label('X'),
            dcc.Dropdown(id='x', 
                         options=dropdown_cols, 
                         value='pri'),
        ]),
        html.Div(style=dict(width='15%'), children=[
            html.Label('Y'),
            dcc.Dropdown(id='y', 
                         options=dropdown_cols, 
                         value='pos'),
        ]),
        html.Div(style=dict(width='15%'), children=[
            html.Label('Color'),
            dcc.Dropdown(id='color', 
                         options=dropdown_cols, 
                         value='rel'),
        ]),
        html.Div(style=dict(width='15%'), children=[
            html.Label('Highlight StimID'),
            dcc.Dropdown(id='highlight-stimid', 
                         options=['None'] + list(range(1,13)), 
                         value='None'),
        ]),
        html.Div(style=dict(width='15%'), children=[
            html.Label('Plot Color Scale'),
            dcc.Dropdown(id='plot-color-scale', 
                         options=named_color_scales, 
                         value=default_color_scale),
        ]),
    ]),
    ## SECOND ROW OF DROPDOWN MENUS
    html.Div(style=dict(display='flex'), children=[
        # FIRST COL NAME
        html.Div(style=dict(width='10%'), children=[
            dcc.Dropdown(id='condition-col-1', 
                         options=dropdown_cols, 
                         value='rel'),
        ]),
        # FIRST COL STAT (e.g. quantile)
        html.Div(style=dict(width='10%'), children=[
            dcc.Dropdown(id='condition-stat-1', 
                         options=dropdown_stats, 
                         value='q75'),
        ]),
        # COMPARISON OPERATOR
        html.Div(style=dict(width='10%'), children=[
            dcc.Dropdown(id='comparison-op', 
                         options=['<', '>'], 
                         value='<'),
        ]),
        # SECOND COL NAME
        html.Div(style=dict(width='10%'), children=[
            dcc.Dropdown(id='condition-col-2', 
                         options=dropdown_cols, 
                         value='rel'),
        ]),
        # SECOND COL STAT (e.g. quantile)
        html.Div(style=dict(width='10%'), children=[
            dcc.Dropdown(id='condition-stat-2', 
                         options=dropdown_stats, 
                         value='q25'),
        ]),
        # 'APPLY FILTER' BUTTON (changes color)
        html.Div(style=dict(width='10%'), children=[
            html.Button(children='Apply Filter', 
                        id='filter-button', n_clicks=0,
                        style=white_button_style),
        ]),
    ]),
    # PLOT AND MOUSEOVER TEXT
    html.Div(style=dict(display='flex', marginBottom=0), children=[
        html.Div(style=dict(width='75%'), children=[dcc.Graph(id='plot'),]),
        html.Div(style=dict(width='25%'), children=[dcc.Markdown(id='hover-data')]),
    ])
])
## CALLBACKS
# The app has *two callbacks*, one to update the graph
# when dropdown options are changed, and one to update
# the hover text in the sidebar whenever the user
# hovers on a different point.

## FIRST CALLBACK 
# update plot after dropdown options
@app.callback(
    Output('plot', 'figure'),
    Output('filter-button', 'style'),
    Output('filter-button', 'children'),
    [
        Input('x', 'value'),
        Input('y', 'value'),
        Input('color', 'value'),
        Input('highlight-stimid', 'value'),
        Input('plot-color-scale', 'value'),
        Input('condition-col-1', 'value'),
        Input('condition-stat-1', 'value'),
        Input('comparison-op', 'value'),
        Input('condition-col-2', 'value'),
        Input('condition-stat-2', 'value'),
        Input('filter-button', 'n_clicks'),
    ],
)
def update_graph(x_col, y_col, color_col, highlight_StimID, color_scale,
                 condition_col_1, condition_stat_1, comparison_op, 
                 condition_col_2, condition_stat_2, button_n_clicks):
    '''
    Parameters are all strings, taken from the dropdown menus.
    Returns: fig (the plot object), button_style (replaces button color), button_text (replaces button text)
    '''
    # check if filter is valid
    valid_filter_condition = all([
        condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2])
    # On click, apply or remove filter (if valid)
    if button_n_clicks % 2 == 1:
        if valid_filter_condition:
            filter_flag = 'on'
            query_str = f'{condition_col_1}_{condition_stat_1} {comparison_op} {condition_col_2}_{condition_stat_2}'
            plotdf = d.query(query_str)
        else:
            filter_flag = 'invalid'
            plotdf = d
    else:
        filter_flag = 'off'
        plotdf = d
    # Use medians for plotting
    chosen_stat = '_q50'
    x = x_col + chosen_stat
    y = y_col + chosen_stat
    color = color_col + chosen_stat
    # Create figure
    fig = px.scatter(plotdf, 
        x=x, 
        y=y, 
        color=color,
        color_continuous_scale=color_scale,
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
    ## UPDATE BUTTON STYLE
    if filter_flag == 'on':
        button_style = blue_button_style
        button_text = 'Filter Applied'
    elif filter_flag == 'off':
        button_style = white_button_style
        button_text = 'Apply Filter'
    elif filter_flag == 'invalid':
        button_style = red_button_style
        button_text = 'Invalid Filter'
    return fig, button_style, button_text

## SECOND CALLBACK
# Update sidebar text when hovering on a point
@app.callback(
    Output('hover-data', 'children'),
    [Input('plot', 'hoverData')]
)
def display_hover_data(hover_data):
    if hover_data is None:
        return ''
    
    point_index = hover_data['points'][0]['pointIndex']
    hover_text = d.iloc[point_index]['stimulus']
    
    return f'{hover_text}'

## RUN THE APP
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
