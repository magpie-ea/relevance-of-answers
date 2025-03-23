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

# descriptive stats

descriptive_stats <- d_AllData |> 
  group_by(ContextType, AnswerPolarity, AnswerCertainty, ExperimentType) |>
  tidyboot_mean(sliderResponse)

d_AllData |> 
  group_by(ExperimentType) |>
  tidyboot_mean(sliderResponse)



## plot the distribution of relevance ratings ----

plot_relevance_ratings <- function(d) {
  d |>
    mutate(AnswerCertainty = case_when(AnswerCertainty == "low_certainty" ~ "low",
                                       AnswerCertainty == "high_certainty" ~ "high",
                                       AnswerCertainty == "non_answer" ~ "non-answer",
                                       TRUE ~ "exhaustive",
    ) |> factor(level = c("non-answer", "low", "high","exhaustive"))) |>
    ggplot(aes(x = sliderResponse, color = AnswerPolarity, fill = AnswerPolarity)) +
    facet_grid(AnswerCertainty ~ ContextType , scales = "free") +
    geom_density(alpha = 0.2, linewidth = 1.5) +
    xlab("relevance rating") + ylab("")
}

plot_relevance_ratings(d_FullExp)
plot_relevance_ratings(d_RelOnly)

plot_positive <- d_AllData |>
  filter(AnswerPolarity == "positive") |>
  mutate(AnswerCertainty = case_when(AnswerCertainty == "low_certainty" ~ "low",
                                     AnswerCertainty == "high_certainty" ~ "high",
                                     AnswerCertainty == "non_answer" ~ "non-answer",
                                     TRUE ~ "exhaustive",
  ) |> factor(level = c("non-answer", "low", "high","exhaustive"))) |>
  ggplot(aes(x = sliderResponse, color = ExperimentType, fill = ExperimentType)) +
  facet_grid(AnswerCertainty ~ ContextType , scales = "free") +
  # histogram with dodged bars
  geom_density(alpha = 0.2, linewidth = 1.5) +
  xlab("relevance rating") + ylab("") +
  ggtitle("AnswerPolarity: positive")

plot_negative <- d_AllData |>
  filter(AnswerPolarity == "negative") |>
  mutate(AnswerCertainty = case_when(AnswerCertainty == "low_certainty" ~ "low",
                                     AnswerCertainty == "high_certainty" ~ "high",
                                     AnswerCertainty == "non_answer" ~ "non-answer",
                                     TRUE ~ "exhaustive",
  ) |> factor(level = c("non-answer", "low", "high","exhaustive"))) |>
  ggplot(aes(x = sliderResponse, color = ExperimentType, fill = ExperimentType)) +
  facet_grid(AnswerCertainty ~ ContextType, scales = "free") +
  geom_density(alpha = 0.2, linewidth = 1.5) +
  xlab("relevance rating") + ylab("") +
  ggtitle("AnswerPolarity: negative")


plot_positive / plot_negative

## fit ordinal beta-regression models ----

fit_model <- function(d, model_name, refit = T, withExpVariable = F) {
  
  # brms formula: whether to use 'ExperimentType' as predictor or not
  if (withExpVariable) {
    formula = brms::brmsformula(
      sliderResponse ~ ContextType * AnswerCertainty * AnswerPolarity * ExperimentType +
        (1 + ContextType + AnswerCertainty + AnswerPolarity || StimID) +
        (1 + ContextType + AnswerCertainty + AnswerPolarity || submission_id)
    )  
  } else {
    formula = brms::brmsformula(
      sliderResponse ~ ContextType * AnswerCertainty * AnswerPolarity + 
        (1 + ContextType + AnswerCertainty + AnswerPolarity || StimID) +
        (1 + ContextType + AnswerCertainty + AnswerPolarity || submission_id)
    )  
  }
  
  # model name for saving
  model_name_expanded <- paste0("cachedModels-round2/exploration-RelOnly-",model_name,".Rds")
  
  # fitting or retrieving cached models
  if (refit) {
    fit <- ordbetareg::ordbetareg(
      formula = formula,
      data = d,
      coef_prior_SD = 5,
      save_pars = save_pars(all=TRUE)
    )
    saveRDS(fit, model_name_expanded)
  } else{
    fit_contextType_SC <- readRDS(model_name_expanded)
  }
  return(fit)
}

fit_AllData_smpl <- fit_model(d_AllData, model_name = "AllData", refit = T, withExpVariable = F)
fit_AllData_cmpl <- fit_model(d_AllData, model_name = "AllData", refit = T, withExpVariable = T)

## compare models with LOO ----

rerun_loo <- T

if (rerun_loo) {
  loo_comp <- loo::loo_compare(
    list("w/o_ExpVariable" = loo(fit_AllData_smpl),
         # moment_match = TRUE,
         # reloo = TRUE),
         "w/_ExpVariable" = loo(fit_AllData_cmpl)))
  saveRDS(loo_comp, "cachedModels-round2/exploration-RelOnly-loo_comp_groups.Rds")
} else {
  loo_comp = read_rds("cachedModels-round2/exploration-RelOnly-loo_comp_groups.Rds")
}
loo_comp
Lambert_test(loo_comp)


## check main effects of AnswerPolarity and ContextType ----

# fit_RelOnly <- fit_model(d_RelOnly, model_name = "RelOnly", refit = T )
# 
# predicted_draws <- d_RelOnly |> 
#   select(ContextType, AnswerPolarity, AnswerCertainty) |>
#   unique() |> 
#   tidybayes::add_predicted_draws(
#     fit_RelOnly, 
#     ndraws = 200, 
#     allow_new_levels = T
#     ) 
# 
# predicted_draws |> 
#   filter(AnswerPolarity == "positive") |>
#   ggplot(aes(x = .prediction)) +
#   geom_density(color = CSP_colors[1]) +
#   geom_density(aes(x = sliderResponse), color = CSP_colors[2], data = d_RelOnly) +
#   facet_wrap(ContextType ~ AnswerCertainty, scales = "free") +
#   ylab("density") + xlab("relevance rating") +
#   theme(legend.position = "none")

# 
# fit_to_use = fit_RelOnly
# 
# ## expected ordering relation?
# ## non-answers vs low-certainty => poster = 1
# nonAns_VS_low  <- compare_groups(
#   fit_to_use,
#   lower  = AnswerCertainty == "non_answer",
#   higher = AnswerCertainty == "low_certainty"
# )
# ## low-certainty vs high-certainty => poster = 0.9922
# low_VS_high <- compare_groups(
#   fit_to_use,
#   lower  = AnswerCertainty == "low_certainty",
#   higher = AnswerCertainty == "high_certainty"
# )
# ## high-certainty vs exhaustive => poster = 1
# high_VS_exh <- compare_groups(
#   fit_to_use,
#   lower  = AnswerCertainty == "high_certainty",
#   higher = AnswerCertainty == "exhaustive"
# )
# 
# 
# ## effects of AnswerPolarity?
# AnswerPolarity_main <- compare_groups(
#   fit_to_use,
#   lower  = AnswerPolarity == "positive" & AnswerCertainty != "non_answer",
#   higher = AnswerPolarity == "negative" & AnswerCertainty != "non_answer"
# )
# 
# AnswerPolarity_lowCertain <- compare_groups(
#   fit_to_use,
#   lower  = AnswerPolarity == "positive" & AnswerCertainty == "low_certainty",
#   higher = AnswerPolarity == "negative" & AnswerCertainty == "low_certainty"
# )
# 
# AnswerPolarity_highCertain <-compare_groups(
#   fit_to_use,
#   lower  = AnswerPolarity == "positive" & AnswerCertainty == "high_certainty",
#   higher = AnswerPolarity == "negative" & AnswerCertainty == "high_certainty"
# )
# 
# AnswerPolarity_exhaustive <-compare_groups(
#   fit_to_use,
#   lower  = AnswerPolarity == "positive" & AnswerCertainty == "exhaustive",
#   higher = AnswerPolarity == "negative" & AnswerCertainty == "exhaustive"
# )
# 
# ContextType_neutral_negative <-
#   compare_groups(fit_to_use, higher = ContextType == "neutral", lower = ContextType == "negative")
# 
# ContextType_neutral_positive <-
#   compare_groups(fit_to_use, higher = ContextType == "neutral", lower = ContextType == "positive")
# 
# 
# cellComparisons <- tribble(
#   ~comparison, ~measure, ~posterior, ~"HDI (low)", ~"HDI (high)",
#   "non-answer < low certainty" , "relevance", nonAns_VS_low$post_prob, 
                 # nonAns_VS_low$l_ci, nonAns_VS_low$u_ci,
#   "low certain < high certain" , "relevance", low_VS_high$post_prob, 
                 # low_VS_high$l_ci, low_VS_high$u_ci,
#   "high certain < exhaustive" , "relevance", high_VS_exh$post_prob, 
                 # high_VS_exh$l_ci, high_VS_exh$u_ci,
#   "answer: pos < neg", "relevance", AnswerPolarity_main$post_prob, 
                 # AnswerPolarity_main$l_ci, AnswerPolarity_main$u_ci,
#   "context: neutral > pos", "relevance", ContextType_neutral_positive$post_prob, 
                 # ContextType_neutral_positive$l_ci, ContextType_neutral_positive$u_ci,
#   "context: neutral > neg", "relevance", ContextType_neutral_negative$post_prob, 
                 # ContextType_neutral_negative$l_ci, ContextType_neutral_negative$u_ci
# )
# 
# write_csv(cellComparisons,
#           "R_data_4_TeX/results-relevance-ratings.csv", col_names = T)
# 
# knitr::kable(cellComparisons)
