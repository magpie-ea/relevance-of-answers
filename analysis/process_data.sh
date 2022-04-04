python3 qualify_participants.py --raw_responses ../results/pilot/results_80_relevance-answers_pilot_0.3.csv --output ../results/pilot/results_filtered.tmp --pilot
python3 widen_dataframe.py --input ../results/pilot/results_filtered.tmp
python3 fit_beta.py --input ../results/pilot/results_filtered.tmp
python3 compute_metrics.py --input ../results/pilot/results_filtered.tmp --output ../results/pilot/results_processed.jsonl
rm ../results/pilot/results_filtered.tmp



