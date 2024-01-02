from pathlib import Path
import pandas as pd

relevance_dir = Path(__file__).resolve().parent.parent.parent.parent

data_by_item_path = relevance_dir / 'qualitative-analysis' / 'data' / 'items_for_dashboard.csv'
data_by_response_path = relevance_dir / 'qualitative-analysis' / 'data' / 'responses_for_dashboard.csv'
data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'processed_data_with_stimuli.csv'

TAGS_FILE_PATH = relevance_dir / 'qualitative-analysis' / 'data' / 'saved_tags.txt'

d = pd.read_csv(data_path)
items = pd.read_csv(data_by_item_path)
responses = pd.read_csv(data_by_response_path)

def get_rowlabel_from_item(id):
    return items.iloc[id].rowlabel

def get_rowlabel_from_response(id):
    return responses.iloc[id].rowlabel

def get_stim_from_item(id):
    return items.iloc[id].stimulus

def get_stim_from_response(id):
    rowlabel = get_rowlabel_from_response(id)
    rowlabel = rowlabel[:-4]
    result = items.query('rowlabel == @rowlabel')
    return result.stimulus

slider_responses = {
    'pri': 'Prior',
    'pos': 'Posterior',
    'rel': 'Relevance',
}
first_order_measures = {
    'bch': 'BeliefCh',
    'klu': 'KLU',
    'ech': 'EntropyCh',
    'bfu': 'BFU',
}
# deltas = {
#     'delta_rel_bfu': 'Rel - BeliefChange',
#     'delta_rel_klu': 'Rel - KLU',
#     'delta_rel_ech': 'Rel - EntropyChange',
#     'delta_rel_bfu': 'Rel - BFU',
# }
second_order_measures = {
    'conf_pri': 'PriorConfidence',
    'conf_pos': 'PosteriorConfidence',
    '2ord_bch': '2ndOrderBeliefChange',
    'beta_ech': 'BetaEntropyCh',
    'beta_klu': 'BetaKLU',
    'beta_bfu': 'BetaBFU',
    'beta_bch': 'BetaBeliefCh',
}
col_names = (
    dict(list(slider_responses.items()) 
         + list(first_order_measures.items()) 
        #  + list(deltas.items())
         + list(second_order_measures.items())
))

# OPTIONS FOR SUMMARY STATS
list_of_stats = [
    'mean_rank',
    'mean',
    'min',
    'q25',
    'q50',
    'q75',
    'max',
]

stats = [
    'Score',
    'Rank',
    'Rank Diff',
    'Mean Score',
    'Mean Rank',
    'Mean Rank Diff',
]