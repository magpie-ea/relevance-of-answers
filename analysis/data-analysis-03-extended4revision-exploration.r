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

## load, prep data and select relevant information ----

d <- read_csv("../results/round_2.0/results_preprocessed.csv") |> 
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
  ) 

# data exclusion
d <- d |> as_tibble() |> 
  mutate(answer_class  = ifelse(AnswerCertainty != "non_answer", "answer", "non_answer"),
         belief_change = abs(prior_sliderResponse - posterior_sliderResponse) >= 0.05 |                                     prior_confidence != posterior_confidence,
         deviant = case_when(answer_class == "answer" ~ !belief_change,
                             answer_class != "answer" ~  FALSE)
  ) |> 
  group_by(submission_id) |> 
  mutate(task_sensitivity = 1- sum(deviant) / sum(answer_class == "answer")) |> 
  select(- answer_class, - belief_change, - deviant)

# initial number of participants
initial_nr_participants <- d |> pull(submission_id) |> unique() |> length()

d <- d |> 
  filter(attention_score == 1) |> 
  filter(reasoning_score > 0.5) |> 
  filter(task_sensitivity > 0.75)

# included participants
included_nr_participants <- d |> pull(submission_id) |> unique() |> length()

message("Initial number of participants: ", initial_nr_participants, 
        "\nIncluded after cleaning: ", included_nr_participants,
        "\nExcluded: ", initial_nr_participants - included_nr_participants)

## extended testing of hypothesis 3 ----

# iter, adapt_delta, moment_match, rerun
models_list <- list(
  "first_order_belief_change"                    = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "second_order_belief_change"                   = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "pure_second_order_belief_change"              = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "pure_second_order_belief_change_joint"        = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "pure_second_order_belief_change_scaled"       = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "pure_second_order_belief_change_joint_scaled" = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "entropy_change"                               = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_entropy_change"                          = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_entropy_change_joint"                    = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "entropy_change_scaled"                        = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_entropy_change_scaled"                   = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_entropy_change_joint_scaled"             = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "kl_utility"                                   = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  # "kl"                                           = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_kl_utility"                              = list("iter" = 6000, "adapt_delta" = 0.85, "moment_match" = F, "rerun" = F),
  "beta_kl"                                      = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_kl_utility_joint"                        = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_kl_joint"                                = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "kl_scaled"                                    = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_kl_scaled"                               = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_kl_joint_scaled"                         = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "bayes_factor_utility"                         = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility"                    = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_1"                  = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_joint"              = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_1_joint"            = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_scaled"             = list("iter" = 6000, "adapt_delta" = 0.85, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_1_scaled"           = list("iter" = 6000, "adapt_delta" = 0.85, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_joint_scaled"       = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F),
  "beta_bayes_factor_utility_1_joint_scaled"     = list("iter" = 6000, "adapt_delta" = 0.8, "moment_match" = F, "rerun" = F)
)

get_single_factor_formula <- function(factor) {
  # get formula for single factor with full RE structure
  brms::brmsformula(
    str_c("relevance_sliderResponse ~ (1 + ", factor, " | submission_id)",
          "+ (1 + ", factor, " | StimID) + ", factor))
}

get_fit <- function(factor_name, iter = 50, adapt_delta = 0.8, moment_match = F, rerun = T) {
  file_name <-  paste0("cachedModels-round2/fit_loo_revision_", factor_name, ".rds")
  message("Fitting model: ", factor_name)
  if (rerun) {
    fit <- ordbetareg(
      get_single_factor_formula(factor_name),
      iter = iter,
      save_pars = save_pars(all = T),
      data = d,
      control = list(adapt_delta = adapt_delta)
    ) |> add_criterion("loo", model_name = factor_name, moment_match = moment_match)
    write_rds(fit, file_name)
  }
  else {
    fit <- read_rds(file_name)
  }
  return(fit)
}

## get model fits ---

max_index <- length(models_list)

# for (i in 1:length(models_list)) {
for (i in 1:max_index) {
  specs <- models_list[[i]]
  models_list[[i]][["model"]] <- get_fit(
    names(models_list)[i], specs$iter, specs$adapt_delta, specs$moment_match, specs$rerun
  )
  models_list[[i]][["ELPD"]] <- loo(models_list[[i]][["model"]])$estimates['elpd_loo', 'Estimate']
  models_list[[i]][["SE"]] <- loo(models_list[[i]][["model"]])$estimates['elpd_loo', 'SE']
}

## quality check (R-hat, divergences) ----

# kl utility did not have same number of observations !?!

# for adapt_delat = 0.8, observed substantial divergences for:
#   beta_kl_utility, 
#   beta_bayes_factor_utility_scaled, 
#   beta_bayes_factor_utility_1_scaled

n_divergences <- map_dbl(
  1:length(models_list), 
  function(i) {
    filter(nuts_params(models_list[[i]]$model), Parameter == "divergent__")$Value |> sum()
  }
)
names(n_divergences) <- names(models_list)

## compare models ----

# create named list of loo objects
model_objects <- lapply(models_list[1:max_index], function(x) loo(x$model))
# assign names to list
names(model_objects) <- names(models_list)[1:max_index] 
# compare models with loo
loo_compare(model_objects)

# do plotting
## 

model_names <- names(models_list)

tibble(
  model = factor(model_names[1:max_index], levels = rev(model_names[1:max_index])),
  # level = rep(c("first-order", "second-order"), each = 1),
  ELPD  = map_dbl(models_list[1:max_index], function(i) {i$ELPD}),
  SE    = map_dbl(models_list[1:max_index], function(i) {i$SE}),
  lower = ELPD - SE,
  upper = ELPD + SE
) |> 
  ggplot(aes( x = model , y = ELPD)) +
  geom_linerange(aes(min = lower, max = upper), size = 0.5) +
  geom_point(aes(), linewidth = 2.5) +
  coord_flip() +
  xlab("") +
  ylab("expected log likelihood (LOO-CV) ")
