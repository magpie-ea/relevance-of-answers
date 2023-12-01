import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

mypath = '/home/omarsagha/code/relevance-of-answers/qualitative-analysis/qualitative-analysis.html'

relevance_dir = Path(mypath).resolve().parent.parent
# INPUT
data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item_with_stimuli.csv'

def format_stimulus(s):
    '''
    Take a row s in the dataframe and 
    return a string with the context/answer conditions
    and the stimulus text.
    '''
    out = f'AnswerCertainty: **`{s.AnswerCertainty}`**\n\nAnswerPolarity: **`{s.AnswerPolarity}`**\n\nContextType: **`{s.ContextType}`**\n\n'
    out += f'{s.Context}\n\n{s.YourQuestionIntro} **{s.YourQuestion}**\n\n{s.AnswerIntro} **{s.Answer}**'
    return out


d = pd.read_csv(data_path)
d['stimulus'] = d.apply(
    lambda s: format_stimulus(s),
    axis=1)
# Create Dash app
app = dash.Dash(__name__)

# PLOTS

color_scale = 'viridis'

# first plot
# slider_medians = px.scatter(d, 
#                 x='pri_q50', 
#                 y='pos_q50', 
#                 color='rel_q50',
#                 color_continuous_scale=color_scale,
#                  )
# zoomed version
# slider_medians_zoomed = go.Figure(slider_medians)
# slider_medians_zoomed.update_traces(
#     marker=dict(line=dict(width=0.01, color='black')))
# slider_medians_zoomed.update_layout(
#     xaxis=dict(range=[0, 0.25]), yaxis=dict(range=[0, 0.25]))
# plot confidence instead of slider scores
# plot second-order belief change by first order belief change

# cols = {col: col for col in d.columns}
cols = {
    'pri_q50': 'Prior',
    'pos_q50': 'Posterior',
    'rel_q50': 'Relevance',
    'bch_q50': 'BeliefChange',
    'klu_q50': 'KLU',
    'ech_q50': 'EntropyChange',
    'bfu_q50': 'BFU',
}

# Define app layout
app.layout = html.Div([
    # create three dropdown menus in a single row
    # for setting the X, Y, and Color
    # in the scatterplot
    html.Div(style=dict(display='flex', marginBottom=0), children=[
        html.Div([
            html.Label('X'),
            dcc.Dropdown(id='x', options=cols, value='pri_q50'),
        ], style=dict(width='33%')),
        html.Div([
            html.Label('Y'),
            dcc.Dropdown(id='y', options=cols,value='pos_q50'),
        ], style=dict(width='33%')),
        html.Div([
            html.Label('Color'),
            dcc.Dropdown(id='color', options=cols, value='rel_q50'),
        ], style=dict(width='33%'))
    ]),
    html.Div(style=dict(display='flex', marginBottom=0),
        children=[
        html.Div(style=dict(width='70%'), children=[dcc.Graph(id='plot'),]),
        html.Div(style=dict(width='30%'), children=[dcc.Markdown(id='hover-data')]),
    ])
])
# Callback to update dropdown
@app.callback(
    Output('plot', 'figure'),
    [
        Input('x', 'value'),
        Input('y', 'value'),
        Input('color', 'value'),
    ],
)
def update_graph(x_col, y_col, color_col):
    fig = px.scatter(d, 
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
