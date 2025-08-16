## preamble ----

library(tidyverse)
library(brms)
library(tidyboot)
library(tidyjson)
library(patchwork)
library(GGally)
library(cowplot)
library(BayesFactor)
library(aida)   # custom helpers: https://github.com/michael-franke/aida-package
library(faintr) # custom helpers: https://michael-franke.github.io/faintr/index.html
library(cspplot) # custom styles: https://github.com/CogSciPrag/cspplot
library(ordbetareg) # for ordered beta-regression
library(cmdstanr)

## set up options / global environment ----

# these options help Stan run faster
options(mc.cores = parallel::detectCores(),
        brms.backend = "cmdstanr")

# use the CSP-theme for plotting
theme_set(theme_csp())

# global color scheme from CSP
project_colors = cspplot::list_colors() |> pull(hex)

# setting theme colors globally
scale_colour_discrete <- function(...) {
  scale_colour_manual(..., values = project_colors)
}
scale_fill_discrete <- function(...) {
  scale_fill_manual(..., values = project_colors)
}

## helper function(s) ----

Lambert_test <- function(loo_comp) {
  1 - pnorm(-loo_comp[2,1], loo_comp[2,2])
}

## load data and select relevant information ----

# data from the full experiment
d_FullExp <- read_csv("../results/round_2.0/results_preprocessed.csv") |> 
  # drop column with numbers
  select(-`...1`) |> 
  # data exclusion based on attention & reasoning score (279 before | 235 after) 
  filter(attention_score == 1) |> 
  filter(reasoning_score >= 0.5) |> 
  # set "non-answers" to AnswerPolarity "positive"
  mutate(AnswerPolarity = ifelse(
    AnswerCertainty == "non_answer", 
    "positive", 
    AnswerPolarity)) |> 
  # casting into factor
  mutate(
    group = factor(group, levels = c("relevant", "helpful")),
    ContextType = factor(ContextType, 
                         levels = c("negative", "neutral", "positive")),
    AnswerPolarity = factor(AnswerPolarity, 
                            levels = c("positive", "negative")),
    AnswerCertainty = factor(AnswerCertainty, 
                             levels = c("non_answer", "low_certainty", 
                                        "high_certainty", "exhaustive"))
  ) |> 
  rename(sliderResponse = relevance_sliderResponse) |> 
  mutate(ExperimentType = "FullExp") |>
  select(submission_id, ExperimentType, group, StimID,
         ContextType, AnswerPolarity, AnswerCertainty, sliderResponse)

d_RelOnly <- read_csv("../results/relevance-only/results_preprocessed.csv")
# inspect the distribution of reasoning & attention scores  
d_RelOnly |> pull(attention_score) |> hist()
d_RelOnly |> pull(reasoning_score) |> hist()

# data from the relevance only replication
d_RelOnly <- read_csv("../results/relevance-only/results_preprocessed.csv") |> 
  # drop column with numbers
  select(-`...1`) |> 
  # data exclusion based on attention & reasoning score (151 before | 56 after)
  filter(attention_score == 1) |> 
  filter(reasoning_score >= 0.5) |> 
  # set "non-answers" to AnswerPolarity "positive"
  mutate(AnswerPolarity = ifelse(
    AnswerCertainty == "non_answer", 
    "positive", 
    AnswerPolarity)) |> 
  # casting into factor
  mutate(
    group = factor(group, levels = c("relevant", "helpful")),
    ContextType = factor(ContextType, 
                         levels = c("negative", "neutral", "positive")),
    AnswerPolarity = factor(AnswerPolarity, 
                            levels = c("positive", "negative")),
    AnswerCertainty = factor(AnswerCertainty, 
                             levels = c("non_answer", "low_certainty", 
                                        "high_certainty", "exhaustive"))
  ) |> 
  mutate(ExperimentType = "RelOnly") |>
  select(submission_id, ExperimentType, group, StimID,
         ContextType, AnswerPolarity, AnswerCertainty, sliderResponse)

# combined data from both experiments
d_AllData <- bind_rows(d_FullExp, d_RelOnly)

# descriptive stats & plotting

descriptive_stats <- d_AllData |> 
  group_by(ContextType, ExperimentType, AnswerPolarity, AnswerCertainty) |>
  tidyboot_mean(sliderResponse)

descriptive_stats |> 
  ggplot(aes(x = AnswerCertainty,
             y = mean, 
             ymin = ci_lower, 
             ymax = ci_upper, 
             color = ExperimentType, 
             fill = ExperimentType)) +
  geom_pointrange(position = position_dodge(width = 0.5)) +
  geom_line(aes(group = ExperimentType), position = position_dodge(width = 0.5)) + 
  facet_grid(ContextType ~ AnswerPolarity, scales = "free")
# Observations:
# - for negative answers, relevance judgments in Exp2 don't (clearly) differentiate
#   between low and high certainty, but in Exp1 they do
# - for non-resolving answers (low / high certainty), relevance judgments are higher
#   in Exp1 than in Exp2 (by visual inspection)

d_AllData |> 
  group_by(ExperimentType) |>
  tidyboot_mean(sliderResponse)
# Observation:
# - Exp1 has higher relevance ratings than Exp2

# ______________________________________
# build a look-up table for by-item IVs
# **************************************

d_lookup_IVs <- read_csv("../results/round_2.0/results_preprocessed.csv") |> 
  # drop column with numbers
  select(-`...1`) |> 
  # set "non-answers" to AnswerPolarity "positive"
  mutate(AnswerPolarity = ifelse(
    AnswerCertainty == "non_answer", 
    "positive", 
    AnswerPolarity)) |> 
  # casting into factor
  mutate(
    group = factor(group, levels = c("relevant", "helpful")),
    ContextType = factor(ContextType, 
                         levels = c("negative", "neutral", "positive")),
    AnswerPolarity = factor(AnswerPolarity, 
                            levels = c("positive", "negative")),
    AnswerCertainty = factor(AnswerCertainty, 
                             levels = c("non_answer", "low_certainty", 
                                        "high_certainty", "exhaustive"))
  ) |> 
  select(
    "submission_id",
    "group",
    "StimID",
    "AnswerCertainty",
    "AnswerPolarity",
    "ContextType",
    "attention_score",
    "reasoning_score",
    "prior_sliderResponse",
    "posterior_sliderResponse",
    "posterior_confidence",
    "prior_confidence",
    "relevance_sliderResponse",
    "first_order_belief_change",                   
    "second_order_belief_change",
    "pure_second_order_belief_change_scaled",
    "entropy_change_scaled",
    "beta_entropy_change_scaled",
    "kl_scaled",
    "beta_kl_scaled",
    "bayes_factor_utility",
    "beta_bayes_factor_utility_1_scaled"
   ) |> 
  rename(
    "probability change" = "first_order_belief_change",
    "commitment change" = "second_order_belief_change",
    "concentration change" = "pure_second_order_belief_change_scaled",
    "entropy change" = "entropy_change_scaled",
    "entropy change (2nd-order)" = "beta_entropy_change_scaled",
    "KL utility" = "kl_scaled",
    "KL utility (2nd-order)" = "beta_kl_scaled",
    "BF utility" = "bayes_factor_utility",
    "BF utility (2nd-order)" = "beta_bayes_factor_utility_1_scaled"
  ) |> 
  group_by(StimID, AnswerCertainty, AnswerPolarity, ContextType) |>
  summarise(
    across(
      c(`probability change`, `commitment change`, `concentration change`, 
        `entropy change`, `entropy change (2nd-order)`, `KL utility`, 
        `KL utility (2nd-order)`, `BF utility`, `BF utility (2nd-order)`),
      mean
    ),
    .groups = "drop"
  ) 
  
  
  # 
  # group_by(StimID, AnswerCertainty, AnswerPolarity, ContextType) |>
  # summarise(
  #   across(
  #     c(ProbabilityChange, CommitmentChange, ConcentrationChange, 
  #       EntropyChange, EntropyChange_2ndOrder, KLUtility, 
  #       KLUtility_2ndOrder, BayesFactor, BayesFactor_2ndOrder),
  #     mean
  #   ),
  #   .groups = "drop"
  # ) |> 
  

# ______________________________________
# extract DVs (REL judgments) by item
# **************************************

d_lookup_DVs <- d_AllData |> 
  group_by(ExperimentType, StimID, ContextType, AnswerPolarity, AnswerCertainty) |>
  summarise(
    RelevanceJudgment = mean(sliderResponse, na.rm = TRUE),
    .groups = "drop"
  ) |> 
  pivot_wider(names_from = ExperimentType, 
              values_from = RelevanceJudgment, 
              names_prefix = "RelevanceJudgment_")
  
# overall correlation in by-item judgments across experiments:

d_lookup_DVs |> 
  ggplot(aes(x = RelevanceJudgment_FullExp, 
             y = RelevanceJudgment_RelOnly
             )) +
  geom_point( aes( shape = ContextType,
                   color = AnswerPolarity)) +
  geom_smooth(method = "lm") +
  labs(x = "Relevance Judgments (FullExp)",
       y = "Relevance Judgments (RelOnly)") 
# Observation:
#  average by-item relevance judgement are ALL > .5
#  for negative AnswerPolarity in Exp 1 (?!?)

# ______________________________________
# merge DVs and IVs
# **************************************

d_lookup <- d_lookup_IVs |> 
  left_join(d_lookup_DVs, by = c("StimID", "ContextType", "AnswerPolarity", "AnswerCertainty"))

# ______________________________________
# correlations of IVs with DVs
# **************************************

# compute the correlation between each DV and each IV

correlations <- d_lookup |> 
  select(-StimID, -ContextType, -AnswerPolarity, -AnswerCertainty) |> 
  cor() |> 
  as.data.frame() |> 
  rownames_to_column("Variable") |> 
  select(Variable, RelevanceJudgment_FullExp, RelevanceJudgment_RelOnly) |> 
  filter(Variable != "RelevanceJudgment_FullExp" & 
           Variable != "RelevanceJudgment_RelOnly") |> 
  arrange(RelevanceJudgment_RelOnly) |> 
  rename(model = Variable)

# ______________________________________
# compare corr-s to previous model comp.
# **************************************

looComp_data <- read_csv(file = "R_data_4_TeX/Hyp3_LOO-comparison_results.csv")

# merge the correlation data with the LOO comparison data
looComp_data <- looComp_data |> 
  left_join(correlations, by = "model") 

looComp_data |> 
  ggplot(aes(x= ELPD, y = RelevanceJudgment_RelOnly, label=model)) +
  geom_point() +
  geom_text(nudge_y = -0.005, size = 3)

# function to plot rankings for different model comparison methods
plot_rankings <- function(x, y, x_label="", y_label="", nudges_x = NULL, nudges_y = NULL) {
  
  # nudges for moving labels away from points
  if (is.null(nudges_x)) {nudges_x <- rep(0, length(x))}
  if (is.null(nudges_y)) {nudges_y <- rep(0, length(y))}
  
  # Compute ranks (higher is better)
  rank1 <- rank(-x)
  rank2 <- rank(-y)
  
  # Identify mismatches
  mismatch <- abs(rank1 - rank2)
  
  # Create labeled data frame
  df <- tibble(
    Model = looComp_data$model,
    Method1_rank = rank1,
    Method2_rank = rank2,
    `rank mismatches` = factor(mismatch)
  )
  
  ggplot(df, aes(x = Method1_rank, y = Method2_rank, label = Model)) +
    geom_point(aes(color = `rank mismatches`), size = 3) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
    geom_text(nudge_y = nudges_y, nudge_x = nudges_x, size = 3) +
    scale_color_manual(values = c(project_colors[1], project_colors[3], project_colors[2])) +
    scale_x_continuous(breaks = 1:9) +
    scale_y_continuous(breaks = 1:9) +
    labs(
      x = x_label,
      y = y_label,
    )  
}

# plot the rankings for ELPD vs. aggregate data from Exp2 (RelOnly)
x <- looComp_data$ELPD
y <- looComp_data$RelevanceJudgment_RelOnly
x_label <- "Rank (ELPD for Exp 1 data)"
y_label <- "Rank (Corr for Exp 2 data)"
nudges_y <- c(
  0.5,  # probability change  
  -0.5, # entropy change 
  -0.5, # KL utility
  0.5,  # BF utility 
  -0.4, # commitment change
  -0.5,  # concentration change
  0.5,  # entropy change (2nd-order)
  0.5, # KL utility (2nd-order)
  -0.5) # BF utility (2nd-order)
nudges_x <- c(
  0,  # probability change  
  -0, # entropy change 
  -0, # KL utility
  0,  # BF utility 
  -0.2, # commitment change
  0,  # concentration change
  -0.5,  # entropy change (2nd-order)
  -0.3, # KL utility (2nd-order)
  0.3) # BF utility (2nd-order)
(rankings_plot_A1_A2 <- plot_rankings(x, y,x_label, y_label, nudges_x, nudges_y))

# plot the rankings for aggr. data Exp 1 vs. aggregate data from Exp2 (RelOnly)
x <- looComp_data$RelevanceJudgment_FullExp
y <- looComp_data$RelevanceJudgment_RelOnly
x_label <- "Rank (Corr for Exp 1 data)"
y_label <- "Rank (Corr for Exp 2 data)"
nudges_y <- c(
  0.5,  # probability change  
  -0.5, # entropy change 
  -0.5, # KL utility
  0.5,  # BF utility 
  -0.2, # commitment change
  -0.5,  # concentration change
  0.5,  # entropy change (2nd-order)
  0.5, # KL utility (2nd-order)
  0.5) # BF utility (2nd-order)
nudges_x <- c(
  0,  # probability change  
  -0, # entropy change 
  -0, # KL utility
  0,  # BF utility 
  -0.5, # commitment change
  0.5,  # concentration change
  -0.5,  # entropy change (2nd-order)
  0, # KL utility (2nd-order)
  0) # BF utility (2nd-order)
(rankings_plot_A2_A3 <- plot_rankings(x, y,x_label, y_label, nudges_x, nudges_y))


# plot the rankings for aggr. data Exp 1 vs. aggregate data from Exp2 (RelOnly)
x <- looComp_data$ELPD
y <- looComp_data$RelevanceJudgment_FullExp
x_label <- "Rank (ELPD for Exp 1 data)"
y_label <- "Rank (Corr for Exp 1 data)"
nudges_y <- c(
  0.5,  # probability change  
  -0.5, # entropy change 
  0.5, # KL utility
  0.5,  # BF utility 
  0.4, # commitment change
  -0.5,  # concentration change
  0.5,  # entropy change (2nd-order)
  0.5, # KL utility (2nd-order)
  -0.5) # BF utility (2nd-order)
nudges_x <- c(
  0,  # probability change  
  0.3, # entropy change 
  -0, # KL utility
  0,  # BF utility 
  -0.5, # commitment change
  0.3,  # concentration change
  -0.5,  # entropy change (2nd-order)
  -0.3, # KL utility (2nd-order)
  0.3) # BF utility (2nd-order)
(rankings_plot_A1_A3 <- plot_rankings(x, y,x_label, y_label, nudges_x, nudges_y))

# a table with all correlations for all models
tibble(comparison = c("ELPD Exp1 vs Corr Exp2",
                      "Corr Exp1 vs Corr Exp2",
                      "ELPD Exp1 vs Corr Exp1"),
       Spearman = c(cor(looComp_data$ELPD, looComp_data$RelevanceJudgment_RelOnly, 
                        method = "spearman") |> round(3),
                    cor(looComp_data$RelevanceJudgment_FullExp, looComp_data$RelevanceJudgment_RelOnly, 
                          method = "spearman") |> round(3),
                    cor(looComp_data$ELPD, looComp_data$RelevanceJudgment_FullExp, 
                        method = "spearman") |> round(3)),
       Kendall = c(cor(looComp_data$ELPD, looComp_data$RelevanceJudgment_RelOnly, 
                       method = "kendall") |> round(3),
                    cor(looComp_data$RelevanceJudgment_FullExp, looComp_data$RelevanceJudgment_RelOnly, 
                        method = "kendall") |> round(3),
                    cor(looComp_data$ELPD, looComp_data$RelevanceJudgment_FullExp, 
                        method = "kendall") |> round(3))
       ) #   kableExtra::kable(format = "latex", booktabs = TRUE, digits = 3)

# Suggested formulations: "The two methods produce highly similar model rankings 
# (Spearman ρ = 0.93; Kendall τ = 0.83), suggesting near-equivalence in their 
# ordinal preferences, with only minor disagreements."



