import pandas as pd
from pathlib import Path

relevance_dir = Path(__file__).resolve().parent.parent.parent.parent
# INPUT DATA
infile = relevance_dir / 'qualitative-analysis' / 'data' / 'by_item_with_stimuli.csv'

outfile = relevance_dir / 'qualitative-analysis' / 'data' / 'for_dashboard.csv'

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

d = pd.read_csv(infile)
# d['rowid'] = str(d.StimID) + str(d.AnswerCertainty)[:2] + str(d.AnswerPolarity)[:2] + str(d.ContextType)[:2]

# Add deltas to dataframe
preprocessed_data = d.assign(
    rowlabel = lambda x: x.StimID.astype(str) + x.AnswerCertainty + x.AnswerPolarity + x.ContextType,
    delta_rel_bfu_mean=lambda x: x.rel_mean - x.bfu_mean,
    delta_rel_klu_mean=lambda x: x.rel_mean - x.klu_mean,
    delta_rel_ech_mean=lambda x: x.rel_mean - x.ech_mean,
    delta_rel_bch_mean=lambda x: x.rel_mean - x.bch_mean,
    clicked = lambda x: False,
)
preprocessed_data['stimulus'] = preprocessed_data.apply(
    lambda s: format_stimulus(s),
    axis=1)

preprocessed_data.to_csv(outfile)

# SETUP COLUMN NAMES FOR APP
median_slider_responses = {
    'pri': 'Prior',
    'pos': 'Posterior',
    'rel': 'Relevance',
}
median_measures = {
    'bch': 'BeliefCh',
    'klu': 'KLU',
    'ech': 'EntropyCh',
    'bfu': 'BFU',
}
deltas = {
    'delta_rel_bfu': 'Rel - BeliefChange',
    'delta_rel_klu': 'Rel - KLU',
    'delta_rel_ech': 'Rel - EntropyChange',
    'delta_rel_bfu': 'Rel - BFU',
}
median_second_order_measures = {
    'conf_pri': 'PriorConfidence',
    'conf_pos': 'PosteriorConfidence',
    '2ord_bch': '2ndOrderBeliefChange',
    'beta_ech': 'BetaEntropyCh',
    'beta_klu': 'BetaKLU',
    'beta_bfu': 'BetaBFU',
    'beta_bch': 'BetaBeliefCh',
}
dropdown_cols = (
    dict(list(median_slider_responses.items()) 
         + list(median_measures.items()) 
         + list(deltas.items())
         + list(median_second_order_measures.items())
))
# OPTIONS FOR SUMMARY STATS
dropdown_stats = [
    'mean',
    'min',
    'q25',
    'q50',
    'q75',
    'max',
]