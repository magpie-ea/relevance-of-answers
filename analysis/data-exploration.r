library(tidyverse)
library(tidyjson)
library(brms)
library(aida)
library(faintr)

# # # # # # # # # # # # # # # # # # # # 
#### preamble ----
# # # # # # # # # # # # # # # # # # # # 


# these options help Stan run faster
options(mc.cores = parallel::detectCores())

# use the aida-theme for plotting
theme_set(theme_aida())

# global color scheme / non-optimized
project_colors = c("#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000")

# setting theme colors globally
scale_colour_discrete <- function(...) {
  scale_colour_manual(..., values = project_colors)
}
scale_fill_discrete <- function(...) {
  scale_fill_manual(..., values = project_colors)
} 

# # # # # # # # # # # # # # # # # # # # 
#### read & explore data ----
# # # # # # # # # # # # # # # # # # # # 

# read cleaned data from JSON-lines file and cast to tibble
d <- read_json("../results/round_1.0/results_processed.jsonl") %>% 
  spread_all() %>% 
  select(-..JSON, -document.id) %>% as_tibble() %>% 
  # set "non-answers" to AnswerPolarity "positive"
  mutate(AnswerPolarity = ifelse(AnswerCertainty == "non_answer", "positive", AnswerPolarity))

# 71 subjects after clearning
d %>% pull(submission_id) %>% unique() %>% length()

# each gave 9 or 10 judgements
table(d$submission_id)

# participants either got questions after "relevance" or "helpfulness"
d %>% group_by(submission_id, group) %>% 
  summarize(n = n())


# items were classified in terms of AnswerCertainty and AnswerPolarity
d %>% group_by(StimID, AnswerCertainty, AnswerPolarity) %>% 
  count()

# # # # # # # # # # # # # # # # # # # # 
#### plotting ----
# # # # # # # # # # # # # # # # # # # # 

# relevance / helpfulness by experimental factors:
# AnswerCertainty vs AnswerPolarity

d %>% ggplot(aes(x = AnswerCertainty, y = relevance_sliderResponse)) +
  geom_violin() +
  facet_grid(group ~ AnswerPolarity)

d %>%  ggplot(aes(x = relevance_sliderResponse, color = group, fill = group)) +
  geom_density(alpha = 0.4) +
  facet_grid(AnswerPolarity~AnswerCertainty, scales = "free" )

# # # # # # # # # # # # # # # # # # # # 
#### analysis ----
# # # # # # # # # # # # # # # # # # # # 

# I'm ommitting interactions in the REs because of the unbalanced (factorial) design
# TODO rethink this
formula = relevance_sliderResponse ~ group * AnswerCertainty * AnswerPolarity + 
  (1 + AnswerCertainty + AnswerPolarity | StimID) + 
  (1 + AnswerCertainty + AnswerPolarity | submission_id)

# priors must be specified b/c with improper priors posterior is improper as well
prior = prior(student_t(1, 0, 1), class = "b")

fit <- brm(
  formula = formula,  
  iter = 4000,
  prior = prior,
  data = d
)

# main effect of "group" (keyword querried in rating?)
# not if we allow for REs
group_main <- compare_groups(
  fit,
  higher = group == "relevant",
  lower  = group == "helpful"
)

## expected ordering relation?
## non-answers vs low-certainty => poster = 1
nonAns_VS_low  <- compare_groups(
  fit,
  lower  = AnswerCertainty == "non_answer",
  higher = AnswerCertainty == "low_certainty"
)
## low-certainty vs high-certainty => poster = 0.9922
low_VS_high <- compare_groups(
  fit,
  lower  = AnswerCertainty == "low_certainty",
  higher = AnswerCertainty == "high_certainty"
)
## high-certainty vs exhaustive => poster = 1
high_VS_exh <- compare_groups(
  fit,
  lower  = AnswerCertainty == "high_certainty",
  higher = AnswerCertainty == "exhaustive"
)


# TODO check if that also holds for comparisons within each group

## effects of AnswerPolarity?
AnswerPolarity_main <- compare_groups(
  fit,
  lower  = AnswerPolarity == "positive" & AnswerCertainty != "non_answer",
  higher = AnswerPolarity == "negative" & AnswerCertainty != "non_answer"
)

AnswerPolarity_lowCertain <- compare_groups(
  fit,
  lower  = AnswerPolarity == "positive" & AnswerCertainty == "low_certainty",
  higher = AnswerPolarity == "negative" & AnswerCertainty == "low_certainty"
)

AnswerPolarity_highCertain <-compare_groups(
  fit,
  lower  = AnswerPolarity == "positive" & AnswerCertainty == "high_certainty",
  higher = AnswerPolarity == "negative" & AnswerCertainty == "high_certainty"
)

AnswerPolarity_exhaustive <-compare_groups(
  fit,
  lower  = AnswerPolarity == "positive" & AnswerCertainty == "exhaustive",
  higher = AnswerPolarity == "negative" & AnswerCertainty == "exhaustive"
)


cellComparisons <- tribble(
  ~comparison, ~posterior, ~"95%HDI (low)", ~"95%HDI (high)",
  "helpful < relevance" , group_main$post_prob, group_main$l_ci, group_main$u_ci,  
  "non-answer < low certainty" , nonAns_VS_low$post_prob, nonAns_VS_low$l_ci, nonAns_VS_low$u_ci,  
  "low certain < high certain" , low_VS_high$post_prob, low_VS_high$l_ci, low_VS_high$u_ci,  
  "high certain < exhaustive" , high_VS_exh$post_prob, high_VS_exh$l_ci, high_VS_exh$u_ci,  
  "positive < negative", AnswerPolarity_main$post_prob, AnswerPolarity_main$l_ci, AnswerPolarity_main$u_ci,
  # "Polarity (low certain)", AnswerPolarity_lowCertain$post_prob, AnswerPolarity_lowCertain$l_ci, AnswerPolarity_lowCertain$u_ci,
  # "Polarity (high certain)", AnswerPolarity_highCertain$post_prob, AnswerPolarity_highCertain$l_ci, AnswerPolarity_highCertain$u_ci,
  # "Polarity (exhaustive)", AnswerPolarity_exhaustive$post_prob, AnswerPolarity_exhaustive$l_ci, AnswerPolarity_exhaustive$u_ci,
)



# d_polUnbalanced <- faintr::politeness %>% filter(! (gender == "F" & context == "pol"))
# 
# prior = prior(student_t(1, 0, 10), class = "b")
# 
# fit <- brm (pitch ~ gender * context, 
#             # data = faintr::politeness,
#             data = d_polUnbalanced,
#             prior = prior)
# 
# tibble(
#   extract_cell_draws(fit, gender == "M" & context == "pol", colname = "Mpol"),
#   extract_cell_draws(fit, gender == "M" & context == "inf", colname = "Minf"),
#   extract_cell_draws(fit, gender == "F" & context == "inf", colname = "Finf")
# ) %>% colMeans()
# 
# d_polUnbalanced %>% group_by(gender, context) %>% 
#   summarize(means = mean(pitch))


# # 32 participants
# d %>% pull(submission_id) %>% unique() %>% length() 
# 
# # trial types per participant okay, except one main trial missing
# d %>% group_by(TrialType, submission_id) %>% 
#   summarise(n = n()) %>% View()
# 
# # everybody should see 10 different vignettes as main trials
# # => correct, except one main trial missing
# d %>% filter(TrialType == "main") %>% 
#   group_by(submission_id) %>% 
#   summarise(unique(StimID) %>% length()) %>% View()
# 
# # Each participant sees four `high_certainty` and four `low_certainty` trials, 
# # as well as two `non_answer` trials.
# # => ???
# d %>% filter(TrialType == "main") %>% 
#   group_by(AnswerCertainty, submission_id) %>% 
#   summarise(n()/3) %>% View()
#   
# # first plotting
# d_wrangled <-
#   d %>% 
#   filter(TrialType == "main") %>% 
#   # exclude beta-testers
#   filter(submission_id >3009) %>% 
#   pivot_wider(
#     c(submission_id, StimID, AnswerCertainty, AnswerPolarity, ContextType), 
#     names_from = TaskType, 
#     values_from = c(sliderResponse, confidence)
#     ) %>% 
#   mutate(prob_diff = sliderResponse_posterior-sliderResponse_prior)
# 
# d_wrangled %>% 
#   ggplot(aes(x = prob_diff, y = sliderResponse_relevance, color = AnswerPolarity)) + 
#   geom_point()
#   
# 
