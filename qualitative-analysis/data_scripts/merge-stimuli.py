import numpy as np
import pandas as pd
from pathlib import Path

relevance_dir = Path(__file__).resolve().parent.parent.parent
# INPUT
data_by_item_path = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item.csv'
relevance_stimuli_path = relevance_dir / 'trials' / 'relevance_stimuli.csv'
# OUTPUT
by_item_with_stimuli_path = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item_with_stimuli.csv'

# Add in stimuli

st = pd.read_csv(relevance_stimuli_path)
st = (st
    .query('TaskType == "relevance"')
)

st['AnswerPolarity'] = np.where(
    st['AnswerCertainty'] == 'non_answer',
    'positive',
    st['AnswerPolarity'])

# Next step: merge in stimuli and see if the size of the df changes

d = pd.read_csv(data_by_item_path)

dst = d.merge(st,
            how='left')


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
    .to_csv(by_item_with_stimuli_path, index=False, 
        float_format='%.2f'
    )
)