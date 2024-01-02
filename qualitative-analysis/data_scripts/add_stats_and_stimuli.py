import numpy as np
import pandas as pd
from pathlib import Path

relevance_dir = Path(__file__).resolve().parent.parent.parent
# INPUT
included_data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'included_data.csv'

# OUTPUT
processed_data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'processed_data.csv'

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

# Read the round 2 data with exclusions applied.
d = pd.read_csv(included_data_path)

###############################
### DROP AND RENAME COLUMNS ###
###############################

dropped_cols = [
    'attention_score',
    'reasoning_score',
    'group',
]

submission_id = [
    'submission_id',
]

group_by_cols = [
    'StimID',
    'AnswerCertainty',
    'AnswerPolarity',
    'ContextType',
]

first_order_cols = [
    'posterior_sliderResponse',
    'prior_sliderResponse',
    'relevance_sliderResponse',
    'first_order_belief_change',
    'entropy_change',
    'kl_utility',
    'bayes_factor_utility',
]
second_order_cols = [
    'posterior_confidence',
    'prior_confidence', 
    'second_order_belief_change',
    'beta_entropy_change',
    'beta_kl_utility',
    'beta_bayes_factor_utility',
    'pure_second_order_belief_change',
]
beta_params = [
    'prior_beta_for_kl_a',
    'prior_beta_for_kl_b',
    'posterior_beta_for_kl_a',
    'posterior_beta_for_kl_b',
    'prior_beta_for_entropy_a',
    'prior_beta_for_entropy_b',
    'posterior_beta_for_entropy_a',
    'posterior_beta_for_entropy_b',
    'prior_beta_for_bf_a',
    'prior_beta_for_bf_b',
    'posterior_beta_for_bf_a',
    'posterior_beta_for_bf_b',
    'prior_beta_for_2nd_order_change_a',
    'prior_beta_for_2nd_order_change_b',
    'posterior_beta_for_2nd_order_change_a',
    'posterior_beta_for_2nd_order_change_b',
]

# Check that the partition is exhaustive.
assert(set(d.columns) == set(dropped_cols + submission_id + group_by_cols + first_order_cols + second_order_cols + beta_params))


# Rename columns of interest
first_order_col_renames = {
    'posterior_sliderResponse'  : 'pos',
    'prior_sliderResponse'      : 'pri',
    'relevance_sliderResponse'  : 'rel',
    'first_order_belief_change' : 'bch',
    'entropy_change'            : 'ech',
    'kl_utility'                : 'klu',
    'bayes_factor_utility'      : 'bfu',
}
second_order_col_renames = {
    'posterior_confidence'              : 'conf_pos',
    'prior_confidence'                  : 'conf_pri',
    'second_order_belief_change'        : '2ord_bch',
    'beta_entropy_change'               : 'beta_ech',
    'beta_kl_utility'                   : 'beta_klu',
    'beta_bayes_factor_utility'         : 'beta_bfu',
    'pure_second_order_belief_change'   : 'beta_bch',
}


# Set new column names
d = (d
    # Select columns of interest.
    .loc[:,(submission_id + group_by_cols + first_order_cols + second_order_cols)]
    # Rename first-order measures to shorter names.
    .rename(columns=first_order_col_renames)
    # Rename second-order measures.
    .rename(columns=second_order_col_renames)
)

# Add unique row ids and non-unique group ids for convenience
d = d.assign(
    RowID = lambda x: x.StimID.astype(str) + x.AnswerCertainty + x.AnswerPolarity + x.ContextType + x.submission_id.astype(str),
    GroupID = lambda x: x.StimID.astype(str) + x.AnswerCertainty + x.AnswerPolarity + x.ContextType
)

# Treat categorical columns as categorical.
d = d.astype(
    { 
    'RowID': 'category',
    'GroupID': 'category',
    'StimID': 'category',
    'AnswerCertainty': 'category',
    'AnswerPolarity': 'category',
    'ContextType': 'category',
    }
)

#####################
### ADD NEW STATS ###
#####################

new_col_names = list(first_order_col_renames.values()) + list(second_order_col_renames.values())

## Add ranks
for col in new_col_names:
    d[f'{col}_rank'] = d[col].rank()

## Add rank diffs
for col in new_col_names:
    d[f'{col}_rank_diff'] = d[f'{col}_rank'] - d['rel_rank']

## Functions for getting aggregate stats.
def combine_dicts(list_of_dicts):
    '''
    Helper function to flatten a list of dicts.
    (For some reason itertools.chain.from_iterable
    was not working for this use case.)
    '''
    single_dict = {}
    for d in list_of_dicts:
       single_dict.update(d)
    return single_dict

def summary_stats(grp: pd.DataFrame) -> pd.Series:
    '''
    Calcuate summary stats for each measure.
    '''
    return pd.Series(combine_dicts([
        # list comprehension of dicts where
        # each dict contains summary stats
        # for one input column
        {
            f'{col}_mean': grp[col].mean(),
            f'{col}_rank_mean': grp[col+'_rank'].mean(),
            f'{col}_rank_diff_mean': grp[col+'_rank_diff'].mean(),
        } for col in new_col_names
    ]))



group_stats = d.groupby('GroupID').apply(summary_stats)

d = pd.merge(d, group_stats, on='GroupID')

d.to_csv(processed_data_path, index=False)