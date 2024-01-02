import pandas as pd
from pathlib import Path

relevance_dir = Path(__file__).resolve().parent.parent.parent
# INPUT DATA
items = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item_with_stimuli.csv'
responses = relevance_dir / 'qualitative-analysis' / 'data' / 'by_response.csv'

items_for_dashboard = relevance_dir / 'qualitative-analysis' / 'data' / 'items_for_dashboard.csv'
responses_for_dashboard = relevance_dir / 'qualitative-analysis' / 'data' / 'responses_for_dashboard.csv'

# Augment dataframe with markdown-formatted stimulus text.
def format_stimulus(s):
    '''
    Take a row s in the dataframe and 
    return a markdown string with the 
    context/answer conditions and the stimulus text.
    '''
    out = f'RowID: **`{s.rowlabel}`**\n\nAnswerCertainty: **`{s.AnswerCertainty}`**\n\nAnswerPolarity: **`{s.AnswerPolarity}`**\n\nContextType: **`{s.ContextType}`**\n\n'
    out += f'{s.Context}\n\n{s.YourQuestionIntro} **{s.YourQuestion}**\n\n{s.AnswerIntro} **{s.Answer}**'
    return out

d_items = pd.read_csv(items)

preprocessed_items = d_items.assign(
    rowlabel = lambda x: x.StimID.astype(str) + x.AnswerCertainty + x.AnswerPolarity + x.ContextType,
)
preprocessed_items['stimulus'] = preprocessed_items.apply(
    lambda s: format_stimulus(s),
    axis=1)

preprocessed_items.to_csv(items_for_dashboard)

d_responses = pd.read_csv(responses)

preprocessed_responses = d_responses.assign(
    rowlabel = lambda x: x.StimID.astype(str) + x.AnswerCertainty + x.AnswerPolarity + x.ContextType + x.submission_id.astype(str),
)

preprocessed_responses.to_csv(responses_for_dashboard)