python3 qualify_participants.py --raw_responses ../results/round_1.0/results_80_relevance-answers.csv --output ../results/round_1.0/results_filtered.tmp
python3 widen_dataframe.py --input ../results/round_1.0/results_filtered.tmp
python3 fit_beta.py --input ../results/round_1.0/results_filtered.tmp
python3 compute_metrics.py --input ../results/round_1.0/results_filtered.tmp --output ../results/round_1.0/results_processed.jsonl
rm ../results/round_1.0/results_filtered.tmp



