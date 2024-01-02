import numpy as np
import pandas as pd
import os
from pathlib import Path

# Set filepaths.
relevance_dir = Path(__file__).resolve().parent.parent.parent

round2_results_path = relevance_dir / 'results' / 'round_2.0' / 'results_preprocessed.csv'
data_with_exclusions_path = relevance_dir / 'qualitative-analysis' / 'data' / 'included_data.csv'
excluded_data = relevance_dir / 'qualitative-analysis' / 'data' / 'excluded_data.csv'

# Read the round 2 data.
d = pd.read_csv(round2_results_path)

## CLEANING

# All non-answers are set to positive polarity
# as in Michael's script.
d['AnswerPolarity'] = np.where(
    d['AnswerCertainty'] == 'non_answer',
    'positive',
    d['AnswerPolarity'])

# Treat categorical columns as categorical.
d = d.astype(
    { 
    'StimID': 'category',
    'AnswerCertainty': 'category',
    'AnswerPolarity': 'category',
    'ContextType': 'category',
    }
)

## EXCLUSIONS

# If not a non-answer, mark participants 
# with < 0.05 belief change as deviant.

d['answer_class'] = np.where(
    d['AnswerCertainty'] != 'non_answer',
    True,
    False
)

d['belief_change'] = np.where(
    ((np.abs(d['prior_sliderResponse'] - d['posterior_sliderResponse']) >= 0.05) 
        | d['prior_confidence'] != d['posterior_confidence']),
    True,
    False
)

d['deviant'] = np.where(
    d['answer_class'],
    ~d['belief_change'],
    False
)

# Compute task-sensitivity.
d = (
d.groupby(['submission_id'])
    .apply(lambda g: g.assign(
        task_sensitivity = (1 - (g.deviant.sum() /g.answer_class.sum()))))
)

# Apply exclusion criteria by filtering on a query.

exclusion_query = '(attention_score == 1 & reasoning_score > 0.5 & task_sensitivity > 0.75)'
included = (
    d
    .query(exclusion_query)
    .drop([ 
        'answer_class', 
        'belief_change', 
        'deviant',
        'task_sensitivity',
        'Unnamed: 0',
    ], axis=1)
)
excluded = (
    d
    .query('~' + exclusion_query)
    .drop([ 
        # 'answer_class', 
        # 'belief_change', 
        # 'deviant',
        # 'task_sensitivity',
        'Unnamed: 0',
    ], axis=1)
)

# Write to file.
included.to_csv(data_with_exclusions_path, index=False)
excluded.to_csv(excluded_data, index=False)