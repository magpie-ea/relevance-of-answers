import numpy as np
import pandas as pd
from pathlib import Path

relevance_dir = Path(__file__).resolve().parent.parent.parent
# INPUT
data_with_exclusions_path = relevance_dir / 'qualitative-analysis' / 'data' / 'included_data.csv'

# OUTPUT
data_by_item_path = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item.csv'

# Read the round 2 data with exclusions applied.
d = pd.read_csv(data_with_exclusions_path)

# Drop column `group` (`relevant` vs `helpful`)
# since we found it makes no difference.
# Extract the columns that are relevant for first-order measures only. Begin by partitioning all columns into four categories.

dropped_cols = [
    'submission_id',
    'attention_score',
    'reasoning_score',
    'group',
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
assert(set(d.columns) == set(dropped_cols + group_by_cols + first_order_cols + second_order_cols + beta_params))

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
    'posterior_confidence': 'conf_pos',
    'prior_confidence': 'conf_pri',
    'second_order_belief_change': '2o_bch',
    'beta_entropy_change': 'beta_ech',
    'beta_kl_utility': 'beta_klu',
    'beta_bayes_factor_utility': 'beta_bfu',
    'pure_second_order_belief_change': 'beta_bch',
}
new_col_names = list(first_order_col_renames.values()) + list(second_order_col_renames.values())

# Treat categorical columns as categorical.
d = d.astype(
    { 
    'StimID': 'category',
    'AnswerCertainty': 'category',
    'AnswerPolarity': 'category',
    'ContextType': 'category',
    }
)

## Functions for getting stats.

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
    cols = new_col_names
    return pd.Series(combine_dicts(
        [{
        # Computations that don't require looping over cols.
        'count' : grp[cols[0]].count()
        }] + [
        # list comprehension of dicts where
        # each dict contains summary stats
        # for one input column
        {
            col: sorted(list(grp[col])),
            col + '_min': grp[col].min(),
            col + '_q25': grp[col].quantile(0.25),
            col + '_mean': grp[col].mean(),
            col + '_q50': grp[col].quantile(0.50),
            col + '_q75': grp[col].quantile(0.75),
            col + '_max': grp[col].max(),
        } for col in cols
    ]))

# Group by `group_by_cols` (StimID, AnswerCertainty,
# AnswerPolarity, ContextType). 
d = (d
    # Select columns of interest.
    .loc[:,(group_by_cols + first_order_cols + second_order_cols)]
    # Rename first-order measures to shorter names.
    .rename(columns=first_order_col_renames)
    # Rename second-order measures.
    .rename(columns=second_order_col_renames)
    # Group by `group_by_cols` (StimID, AnswerCertainty,
    # AnswerPolarity, ContextType).
    .groupby(
        group_by_cols, 
        # No multi-indexing.
        as_index=False,
    )
    # Get summary stats as columns.
    .apply(summary_stats)
    .dropna()
)

d.to_csv(data_by_item_path, index=False)
