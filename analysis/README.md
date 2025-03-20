# Analysis directory README

This directory contains scripts for results post-processing and analysis.

## Preregistered analysis
The official preregistered analysis (including preregistered "exploratory" analysis) are all performed in `data-analysis-round-prereg.qmd`

Other (related) files:

- `data-analysis_main.qmd` - original exploratory DA based on pilot studies
- `data-analysis_reproduceV01.qmd` - reproducing initial results with subsequent explorations (paper revision) 

## Qualitative analysis
The qualitative analysis is performed in `qualitative_analysis.ipynb`.

The main data analysis is in `data-analysis-main.qmd`.

- `R_data_4_TeX` contains results from the data analysis for reproducible use in LaTeX
- `cached_models` contains cached regression models to speed up processing
- `legacy` contains prior iterations of data analysis (including the script for the preregistration)
- `plots` contains plots generated during data analysis


## Steps for post-processing raw data

The raw experimental data needs to be processed before undergoing preregistered and qualitative analyses.
This process is already done (see `results/round_2.0/results_preprocessed.csv`),
but the can be replicated as follows:

### Step 1: Identify the location of the results file:

Set your project root before running the following.

```bash
RESULTS_DIR=$PROJECT_ROOT/results/round_2.0
cd $PROJECT_ROOT/analysis
```

OR if you want to preprocess round_1.0:
```bash
RESULTS_DIR=$PROJECT_ROOT/results/round_1.0
```

### Step 2: Participant qualification
The `qualify_participants.py` script implements the following inclusion criteria:
1. Participants scored 100% on the two attention check item, with two measurements each. 
  I.e., for each item, their `probability` slider response was within some small (predetermined) range around the requested value, 
  and their `confidence` likert judgment was exactly the requested value.
2. Participants scored >=75% on the two reasoning check item, with four measurements each
   I.e., for each item, there was a prior and a posterior trial, 
   and for each item there is a `probability` and `confidence` values 
   which we check falls within some (predetermined) moderately sized reasonable range.

Use the `--exclude_pilot` or `exclude_round1` flags if you want to exclude that data from the results file.

```bash
python3 qualify_participants.py --raw_responses $RESULTS_DIR/results_80_relevance-answers.csv --output $RESULTS_DIR/results_filtered.tmp --exclude_round1
```

OR if doing round_1.0:
```bash
python3 qualify_participants.py --raw_responses $RESULTS_DIR/results_80_relevance-answers.csv --output $RESULTS_DIR/results_filtered.tmp
```


### Step 3: Reshaping

The raw results file doesn't group responses by vignette. So we do that now.

```bash
python3 widen_dataframe.py --input $RESULTS_DIR/results_filtered.tmp
```


### Step 4: Fitting beta distributions

Now we want to estimate the higher-order belief states of participants by fitting beta distributions. 
In other words, we need to find the \alpha and \beta parameters for the beta distributions for each trial judgment. 
To do this, we use the mode/concentration parameterization of the beta distribution, 
which can be used to give the typical \alpha and \beta parameterization.

For the **mode**, we simply us the probability judgment.

For the **concentration** `K`, we have to find some mapping from the confidence likert judgments `c`. 
To do this, we assume a 2-parameter linking function: `K = a * b^c`, which we selected heuristically. 
We use sequential least squares to find the values of `a` and `b` that maximize the Pearson correlation between
the `beta-KL` measure and the relevance judgments.

```bash
python3 fit_beta.py \
    --training $PROJECT_ROOT/results/round_1.0/results_filtered.tmp \
    --input $RESULTS_DIR/results_filtered.tmp
```

### Step 5: Computing metrics

Now, we want to take the raw judgments and the beta distributions, and compute our hypothesized relevance predictors 
(e.g., entropy reduction, Bayes Factor, higher-order measures, baselines).

A complete list of predictors is as follows:
- First order belief change: `|prior - posterior|`
- Second order belief change: `|prior_confidence - posterior_confidence|`
- Entropy change: `|H(posterior) - H(prior)|`
- KL utility: `g(KL(posterior || prior)) where g(x) = 1-exp(-x)`
- Bayes Factor utility: `1 - BF(prior, posterior)` where prior and posterior are the probabilities of the alternative that decreases in probability from prior to posterior.
- Beta-KL utility: `g(KL((posterior_a, posterior_b) || (prior_a, prior_b))) where g(x) = 1-exp(-x)`
- Beta-entropy change: `|H((posterior_a, posterior_b)) - H((prior_a, prior_b))|`
- Beta-Bayes factor utility: `log(|posterior_a - prior_a| + |posterior_b - prior_b| + 2)`
- Pure second order belief change: `|prior_a + prior_b - (posterior_a + posterior_b)|`

```bash
python3 compute_metrics.py \
    --input $RESULTS_DIR/results_beta.tmp \
    --output $RESULTS_DIR/results_metrics.tmp
```

### Step 6: Clean up
```bash
python3 finalize_preprocessing.py \
    --input $RESULTS_DIR/results_metrics.tmp \
    --output $RESULTS_DIR/results_preprocessed.csv
rm $RESULTS_DIR/*.tmp
```

## Appendix 1: Post processing relevance-only data
The raw data is `data-raw-relevance-only.csv`
```bash
RESULTS_DIR=$PROJECT_ROOT/results/relevance-only
cd $PROJECT_ROOT/analysis
```

Evaluate participant reasoning and attention and filter out unnecessary rows and cols
```bash
python3 qualify_participants.py --raw_responses $RESULTS_DIR/data-raw-relevance-only.csv --output $RESULTS_DIR/results_preprocessed.csv --relevance-only
```

## Appendix 2: Universal parameters

If you want to find both metric-specific parameters and a set of universal parameters optimized jointly for all metrics:
```bash
python3 fit_beta.py \
    --training $PROJECT_ROOT/results/round_1.0/results_filtered.tmp \
    --input $RESULTS_DIR/results_filtered.tmp \
    --output $RESULTS_DIR/results_beta.tmp \
    --optimize_joint both
```

If you want to run a grid search over parameters and make nice heatmaps
```bash
python3 fit_beta.py \
    --training $RESULTS_DIR/round_1.0/results_filtered.tmp \
    --input $RESULTS_DIR/results_filtered.tmp \
    --optimize_joint grid \
    --output $PROJECT_ROOT/plotting/plots/fit_beta_heatmaps.pdf
```

## Appendix 3: Scaling metrics

You may want to scale all metrics to lie between [0, 1]. If so:

```bash
python3 compute_metrics.py \
    --input $RESULTS_DIR/results_beta.tmp \
    --train $PROJECT_ROOT/results/round_1.0/results_beta.tmp \
    --output $RESULTS_DIR/results_metrics.tmp \
    --joint both \
    --obj pearson \
    --scale
 ```

You should update `--joint both` `--joint separate` or `--joint joint` 
depending on how beta params were fit (see Appendix 2).

You can also update `--obj pearson`, `--obj mse`, `--obj pearson_reg` among other options.
