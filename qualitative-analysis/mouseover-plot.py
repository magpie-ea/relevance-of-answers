import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from pathlib import Path

mypath = '/home/omarsagha/code/relevance-of-answers/qualitative-analysis/qualitative-analysis.html'

relevance_dir = Path(mypath).resolve().parent.parent
# INPUT
data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item_with_stimuli.csv'

def display_stimulus(s):
    '''
    Take a row s in the dataframe and 
    return a string with the context/answer conditions
    and the stimulus text.
    '''
    out = f'AnswerCertainty: `{s.AnswerCertainty}` AnswerPolarity: `{s.AnswerPolarity}` ContextType: `{s.ContextType}`\n'
    out += f'{s.Context}\n{s.YourQuestionIntro}\n{s.YourQuestion}\n{s.AnswerIntro}\n{s.Answer}\n'
    return out


d = pd.read_csv(data_path)
d['stimulus'] = d.apply(
    lambda s: display_stimulus(s),
    axis=1)
# Create Dash app
app = dash.Dash(__name__)

fig = px.scatter(d, x='pri_q50', y='pos_q50', 
                 color='rel_q50',
                #  hover_name='stimulus'
                 )

# Define app layout
app.layout = html.Div([
    dcc.Graph(figure=fig, id='scatter-plot'),
    html.Div(id='hover-data', style={'white-space': 'pre-line'})
])

# Define callback to update sidebar text
@app.callback(
    Output('hover-data', 'children'),
    [Input('scatter-plot', 'hoverData')]
)
def display_hover_data(hover_data):
    if hover_data is None:
        return ''
    
    point_index = hover_data['points'][0]['pointIndex']
    hover_text = d.iloc[point_index]['stimulus']
    
    return f'Hovered Text:\n{hover_text}'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
