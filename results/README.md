# README for the `results` directory

Here we have results from different stages of the experiment:

1. `beta` contains results from the beta-testing trials with some of our friends/family.
2. `pilot` contains results from 2 pilot experiments on Prolific.
    - Note: `pilot_0.3` also contains all the results from `pilot_0.2`.
    - Note: `pilot_0.1` is nowhere to be found...
3. `round_1.0` contains results from the first official launch of the experiment. 
    - `results_80_relevance-answers.csv` is all the raw responses **including pilot responses**
    - `results_processed.jsonl` is the post-processed data. 
      See the `analysis` directory `README` for a full description of post-processing.
4. `round_2.0` contains results from the second (preregistered) launch
    - `results_80_relevance-answers.csv` is all the raw responses **including pilot responses and round 1.0 responses**