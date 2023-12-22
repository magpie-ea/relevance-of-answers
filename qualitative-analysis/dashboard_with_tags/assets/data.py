from pathlib import Path
import pandas as pd

relevance_dir = Path(__file__).resolve().parent.parent.parent.parent

data_path = relevance_dir / 'qualitative-analysis' / 'data' / 'for_dashboard.csv'

TAGS_FILE_PATH = relevance_dir / 'qualitative-analysis' / 'data' / 'saved_tags.txt'

d = pd.read_csv(data_path)


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
deltas = {
    'delta_rel_bfu_q50': 'Rel - BeliefChange',
    'delta_rel_klu_q50': 'Rel - KLU',
    'delta_rel_ech_q50': 'Rel - EntropyChange',
    'delta_rel_bfu_q50': 'Rel - BFU',
}
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
         + list(deltas.items())
         + list(second_order_measures.items())
))

# OPTIONS FOR SUMMARY STATS
list_of_stats = [
    'mean',
    'min',
    'q25',
    'q50',
    'q75',
    'max',
]