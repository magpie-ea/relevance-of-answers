import numpy as np
import pandas as pd
from pathlib import Path

relevance_dir = Path(__file__).resolve().parent.parent.parent
# INPUT
processed_data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'processed_data.csv'
relevance_stimuli_path = relevance_dir / 'trials' / 'relevance_stimuli.csv'
# OUTPUT
processed_data_with_stimuli_path = relevance_dir / 'qualitative-analysis' / 'data' / 'processed_data_with_stimuli.csv'

# Add in stimuli

st = pd.read_csv(relevance_stimuli_path)
st = (st
    .query('TaskType == "relevance"')
)

st['AnswerPolarity'] = np.where(
    st['AnswerCertainty'] == 'non_answer',
    'positive',
    st['AnswerPolarity'])

# Next step: merge in stimuli

d = pd.read_csv(processed_data_path)

dst = d.merge(st,
            how='left')

# Augment dataframe with markdown-formatted stimulus text.
def format_stimulus(s):
    '''
    Take a row s in the dataframe and 
    return a markdown string with the 
    context/answer conditions and the stimulus text.
    '''
    out = f'GroupID: **{s.GroupID}**\n\nAnswerCertainty: **`{s.AnswerCertainty}`**\n\nAnswerPolarity: **`{s.AnswerPolarity}`**\n\nContextType: **`{s.ContextType}`**\n\n'
    out += f'{s.Context}\n\n{s.YourQuestionIntro} **{s.YourQuestion}**\n\n{s.AnswerIntro} **{s.Answer}**'
    return out

dst['stimulus'] = dst.apply(
    lambda s: format_stimulus(s),
    axis=1)


drop_before_write = [
    'TrialType',
    'TaskType',    
    'name',
    'SliderLabelLeft',
    'SliderLabelRight',
    'TaskQuestion',
]

# write to csv

(dst
    .drop(drop_before_write, axis=1)
    .to_csv(processed_data_with_stimuli_path, index=False, 
        float_format='%.2f'
    )
)