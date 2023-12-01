import dash
from dash import dcc, html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

mypath = '/home/omarsagha/code/relevance-of-answers/qualitative-analysis/dashboard/app.py'

relevance_dir = Path(__file__).resolve().parent.parent.parent
# INPUT DATA
data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item_with_stimuli.csv'
# Augment dataframe with markdown-formatted stimulus text.
def format_stimulus(s):
    '''
    Take a row s in the dataframe and 
    return a markdown string with the 
    context/answer conditions and the stimulus text.
    '''
    out = f'AnswerCertainty: **`{s.AnswerCertainty}`**\n\nAnswerPolarity: **`{s.AnswerPolarity}`**\n\nContextType: **`{s.ContextType}`**\n\n'
    out += f'{s.Context}\n\n{s.YourQuestionIntro} **{s.YourQuestion}**\n\n{s.AnswerIntro} **{s.Answer}**'
    return out
d = pd.read_csv(data_path)
d['stimulus'] = d.apply(
    lambda s: format_stimulus(s),
    axis=1)
# Add deltas to dataframe
d = d.assign(
    delta_rel_bfu=lambda x: x.rel_q50 - x.bfu_q50,
    delta_rel_klu=lambda x: x.rel_q50 - x.klu_q50,
    delta_rel_ech=lambda x: x.rel_q50 - x.ech_q50,
    delta_rel_bch=lambda x: x.rel_q50 - x.bch_q50,
)

# DASH APP CODE
app = dash.Dash(__name__)

color_scale = 'viridis'

median_slider_responses = {
    'pri_q50': 'Prior',
    'pos_q50': 'Posterior',
    'rel_q50': 'Relevance',
}
median_measures = {
    'bch_q50': 'BeliefCh',
    'klu_q50': 'KLU',
    'ech_q50': 'EntropyCh',
    'bfu_q50': 'BFU',
}
deltas = {
    'delta_rel_bfu': 'Rel - BeliefChange',
    'delta_rel_klu': 'Rel - KLU',
    'delta_rel_ech': 'Rel - EntropyChange',
    'delta_rel_bfu': 'Rel - BFU',
}
median_second_order_measures = {
    'conf_pri_q50': 'PriorConfidence',
    'conf_pos_q50': 'PosteriorConfidence',
    '2o_bch_q50': '2ndOrderBeliefChange',
    'beta_ech_q50': 'BetaEntropyCh',
    'beta_klu_q50': 'BetaKLU',
    'beta_bfu_q50': 'BetaBFU',
    'beta_bch_q50': 'BetaBeliefCh',
}
dropdown_cols = (
    dict(list(median_slider_responses.items()) 
         + list(median_measures.items()) 
         + list(deltas.items())
         + list(median_second_order_measures.items())
))

dropdown_filters = [
    '',
    'rel_q75 < bfu_q25',
    'rel_q25 > bfu_q75',
    'rel_q75 < klu_q25',
    'rel_q25 > klu_q75',
]

# LAYOUT
app.layout = html.Div([
    # DROPDOWN MENUS
    # create three dropdown menus in a single row
    # for setting the X, Y, and Color in the scatterplot
    html.Div(style=dict(display='flex', marginBottom=0), children=[
        html.Div([
            html.Label('X'),
            dcc.Dropdown(id='x', 
                         options=dropdown_cols, 
                         value='pri_q50'),
        ], style=dict(width='25%')),
        html.Div([
            html.Label('Y'),
            dcc.Dropdown(id='y', 
                         options=dropdown_cols, 
                         value='pos_q50'),
        ], style=dict(width='25%')),
        html.Div([
            html.Label('Color'),
            dcc.Dropdown(id='color', 
                         options=dropdown_cols, 
                         value='rel_q50'),
        ], style=dict(width='25%')),
        html.Div([
            html.Label('Filter'),
            dcc.Dropdown(id='filter', 
                         options=dropdown_filters,
                         value = ''),
        ], style=dict(width='25%'))
    ]),
    # PLOT AND MOUSEOVER TEXT
    html.Div(style=dict(display='flex', marginBottom=0),
        children=[
        html.Div(style=dict(width='70%'), children=[dcc.Graph(id='plot'),]),
        html.Div(style=dict(width='30%'), children=[dcc.Markdown(id='hover-data')]),
    ])
])
# CALLBACKS
# Callback to update plot after dropdown is edited
@app.callback(
    Output('plot', 'figure'),
    [
        Input('x', 'value'),
        Input('y', 'value'),
        Input('color', 'value'),
        Input('filter', 'value')
    ],
)
def update_graph(x_col, y_col, color_col, filter):
    if filter:
        mydata = d.query(filter)
    else:
        mydata = d
    fig = px.scatter(mydata, 
        x=x_col, 
        y=y_col, 
        color=color_col,
        color_continuous_scale=color_scale,
        )
    # put x axis label on top
    fig.update_layout(xaxis=dict(title_standoff=5, side='top'),)
    # reduce margins
    fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=5),
)
    return fig
# Callback to update sidebar text
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
