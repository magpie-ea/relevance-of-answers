python3 make_results_df.py --raw_responses ../results/pilot/results_80_relevance-answers_pilot_0.3.csv --output ../results/pilot/results_filtered.tmp --pilot
python3 compute_metrics.py --input ../results/pilot/results_filtered.tmp --output ../results/pilot/results_processed.csv
rm ../results/pilot/results_filtered.tmp
