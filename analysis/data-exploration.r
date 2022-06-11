library(tidyverse)
library(tidyjson)
# library(GGally)
library(cowplot)
library(BayesFactor)
library(brms)
library(aida)
library(faintr)

# # # # # # # # # # # # # # # # # # # # 
## preamble ----
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
## read & explore data ----
# # # # # # # # # # # # # # # # # # # # 

# read cleaned data from JSON-lines file and cast to tibble
d <- read_json("../results/round_1.0/results_processed.jsonl") %>% 
  spread_all() %>% 
  select(-..JSON, -document.id) %>% as_tibble() %>% 
  # set "non-answers" to AnswerPolarity "positive"
  mutate(AnswerPolarity = ifelse(AnswerCertainty == "non_answer", "positive", AnswerPolarity))

# add information from (nested) JSON entries on beta-parameters for prior and posterior
prior_beta <- read_json("../results/round_1.0/results_processed.jsonl") %>% 
  enter_object(prior_beta) %>% gather_array() %>% 
  mutate(parameter = ifelse(array.index == 1, "prior_beta_a", "prior_beta_b"),
         value = as.numeric(..JSON)) %>% 
  pivot_wider(id_cols = document.id, names_from = parameter, values_from = value)

posterior_beta <- read_json("../results/round_1.0/results_processed.jsonl") %>% 
  enter_object(posterior_beta) %>% gather_array() %>% 
  mutate(parameter = ifelse(array.index == 1, "posterior_beta_a", "posterior_beta_b"),
         value = as.numeric(..JSON)) %>% 
  pivot_wider(id_cols = document.id, names_from = parameter, values_from = value)

d <- cbind(
  d,
  prior_beta %>% select(-document.id), 
  posterior_beta %>% select(-document.id)
)

# View(d)

# what is what?
# submission_id : ID for each participant
# group : whether the participant saw trigger word 'helpful' or 'relevant'
# StimID : ID for each stimulus (vignette)
# AnswerCertainty : whether shown answer in trial was 'exhaustive', 'high_certainty', 'low_certainty' or 'non_answer' 
# AnswerPolarity : whether shown answer in trial was 'positive' (suggesting yes) or 'negative' (suggestion no)
# ContextType : whether the vignette was realized as making a 'no' answer more likely ('negative'), or a 'yes' answer ('positive') or neither ('neutral')
# posterior_confidence : slider rating indicating confidence in the corresponding posterior rating
# prior_confidence : slider rating indicating confidence in the corresponding prior rating
# posterior_SliderResponse : slider rating indicating posterior belief (= after the answer)
# prior_SliderResponse : slider rating indicating prior belief (= before the answer)
# relevance_sliderResponse : slider rating indicating how 'relevant' or 'helpful' the answer was (trigger word depends on 'group' variable)
# prior_concentration : 
# posterior_concentration :
# kl : KL divergence from posterior (true distribution) to prior (approximate distribution)
# kl_util : scaled KL divergence as 1 - (10^{-kl})
# entropy_reduction : abs(Entropy(prior) - Entropy(posterior))
# bayes_factor : abs(log(BF)) where BF is the Bayes factor, computed as posterior-odds / prior-odds (based on ratings given for prior and posterior)
# exp_bayes_factor : scaled Bayes factor, computed as 1 - (10^{-bayes_factor})
# posterior_distance : distance of posterior from uniform distribution, calculated as 2 * abs(0.5 - prior)
# prior_posterior_distance : distance between prior and posterior, calculated as abs(prior - posterior)
# kl_beta : KL divergence between the higher-order prior & posterior distributions, which are computed from the prior/posterior slider ratings and the corresponding confidence ratings
# kl_util_beta : scaled kl_beta computed as 2^{-kl_beta}
# entropy_reduction_beta : Entropy(higher-order prior) - Entropy(higher-order posterior)
# prior_beta_a : alpha parameter of the (inferred) beta distribution describing the participants prior beliefs, based on ratings for 'prior' and 'prior_confidence' 
# prior_beta_b : beta parameter of the (inferred) beta distribution describing the participants prior beliefs, based on ratings for 'prior' and 'prior_confidence' 
# posterior_beta_a : alpha parameter of the (inferred) beta distribution describing the participants posterior beliefs, based on ratings for 'posterior' and 'posterior_confidence' 
# posterior_beta_b : beta parameter of the (inferred) beta distribution describing the participants posterior beliefs, based on ratings for 'posterior' and 'posterior_confidence' 

# renaming and re-leveling (for convenience)
d <- d %>% 
  mutate(
    "trigger word" = factor(group, levels = c("relevant", "helpful")),
    "relevance rating" = relevance_sliderResponse,
    ContextType = factor(ContextType, levels = c("negative", "neutral", "positive")),
    AnswerPolarity = factor(AnswerPolarity, levels = c("positive", "negative")),
    AnswerPolarity = factor(AnswerPolarity, levels = c("positive", "negative")),
    AnswerCertainty = factor(AnswerCertainty, 
                             levels = c("non_answer", "low_certainty", "high_certainty", "exhaustive"))
  ) 

# 71 subjects after cleaning
d %>% pull(submission_id) %>% unique() %>% length()

# each gave 9 or 10 judgements
table(d$submission_id)

# participants either got questions after "relevance" or "helpfulness"
d %>% group_by(submission_id, group) %>% 
  summarize(n = n())

# items were classified in terms of ContextType, AnswerCertainty and AnswerPolarity
d %>% group_by(StimID, ContextType, AnswerCertainty, AnswerPolarity) %>% 
  count()

# # # # # # # # # # # # # # # # # # # # 
## sanity-check manipulations ----
# # # # # # # # # # # # # # # # # # # # 

# TODO redo these calculations with more sophisticated models (additional factors and RE structures)

#### ContextType ----

# check whether ContextType manipulation worked, by comparing
# prior ratings for each type of context; we expect this order of 
# prior ratings for the levels of ContextType:
#   negative < neutral < positive

fit_contextType_SC <- brm(
  prior_sliderResponse ~ ContextType,
  data = d
)

ContextType_SC_negVSneu <- 
  compare_groups(
    fit_contextType_SC, 
    lower = ContextType == "negative",
    higher = ContextType == "neutral" 
  )
ContextType_SC_neuVSpos <- 
  compare_groups(
    fit_contextType_SC, 
    lower = ContextType == "neutral",
    higher = ContextType == "positive"
  )


fit_contextType_SC_conf <- brm(
  prior_confidence ~ ContextType,
  data = d
)

ContextType_SC_neuVSneg_conf <- 
  compare_groups(
    fit_contextType_SC_conf, 
    lower = ContextType == "neutral",
    higher = ContextType == "negative" 
  )
ContextType_SC_negVSpos_conf <- 
  compare_groups(
    fit_contextType_SC_conf, 
    lower = ContextType == "negative",
    higher = ContextType == "positive"
  )

results_ContextType_SanityCheck <- 
  tribble(
  ~comparison, ~measure, ~posterior, ~"95%HDI (low)", ~"95%HDI (high)",
  "negative < neutral" , "prior", ContextType_SC_negVSneu$post_prob, ContextType_SC_negVSneu$l_ci, ContextType_SC_negVSneu$u_ci,  
  "neutral < positive" , "prior", ContextType_SC_neuVSpos$post_prob, ContextType_SC_neuVSpos$l_ci, ContextType_SC_neuVSpos$u_ci,  
  "neutral < negative" , "prior-confidence", ContextType_SC_neuVSneg_conf$post_prob, ContextType_SC_neuVSneg_conf$l_ci, ContextType_SC_neuVSneg_conf$u_ci,  
  "negative < positive" , "prior-confidence", ContextType_SC_negVSpos_conf$post_prob, ContextType_SC_negVSpos_conf$l_ci, ContextType_SC_negVSpos_conf$u_ci,  
  )

# RESULTS:
# The ContextType manipulation seems to have worked for the prior ratings: 
# lower in 'negative' than in 'neutral' than in 'positive'.
# There are also differences in the confidence ratings, 
# with lowest confidence in the 'neutral' contexts (which makes sense), 
# but also a difference between 'negative' having less confidence than 'positive'.

d %>% ggplot(aes(x = prior_sliderResponse, color = ContextType, fill = ContextType)) +
  geom_density(alpha = 0.3) + 
  xlab("prior rating") +
  ylab("")

d %>% ggplot(aes(x = prior_confidence, color = ContextType, fill = ContextType)) +
  geom_density(alpha = 0.3) + 
  xlab("prior confidence") +
  ylab("")

d %>% ggplot(aes(x = prior_sliderResponse, y = prior_confidence, color = ContextType)) +
  geom_jitter(height = 0.3, width =0, alpha = 0.7) +
  facet_grid(~ContextType) +
  xlab("prior rating") +
  ylab("prior confidence") 

d %>% ggplot(aes(x = prior_sliderResponse, y = prior_confidence, color = ContextType)) +
  geom_jitter(height = 0.3, width =0, alpha = 0.7) +
  # geom_point(alpha = 0.7) +
  xlab("prior rating") +
  ylab("prior confidence") 
# this last plot shows an exceptional status of prior = 0.5,
# but otherwise a seemingly U-shaped curve
# however, we also see a trend to be more confident in ratings further away from 0.5
# [It's funny that people are confident in the estimate 0.5]

#### AnswerPolarity & AnswerCertainty----

# Sanity-check for answer polarity:
# define "beliefChange" as difference between posterior and prior IN THE EXPECTED DIRECTION by the answer's polarity
# we then expect beliefChange to be > 0 for both 'positive' and 'negative' polarity
# careful: ignore non-answers (which are categorized as "positive")

# Sanity-check for answer certainty:
# for both positive / negative answers:
# belief change is lower for 'low certainty' than for 'high certainty' than for 'exhaustive'

d %>% filter(AnswerCertainty != "non_answer") %>% 
  mutate(beliefChange = posterior_sliderResponse - prior_sliderResponse,
         beliefChange = ifelse(AnswerPolarity == "positive", beliefChange, - beliefChange)) %>% 
  ggplot(aes(x = beliefChange, color = AnswerCertainty, fill = AnswerCertainty)) +
  geom_density(alpha = 0.3) +
  facet_grid(AnswerPolarity ~ AnswerCertainty) +
  xlab("belief change (in expected direction)") +
  ylab("")

fit_answer_SC <- brm(
  formula = beliefChange ~ AnswerCertainty * AnswerPolarity,
  data = d %>% filter(AnswerCertainty != "non_answer") %>% 
    mutate(beliefChange = posterior_sliderResponse - prior_sliderResponse,
           beliefChange = ifelse(AnswerPolarity == "positive", beliefChange, - beliefChange))
)

# 1. Check if belief change in each cell is bigger than zero
cellDraws_answers <- tibble(
  extract_cell_draws(fit_answer_SC, AnswerCertainty == "low_certainty" & AnswerPolarity == "positive", "low_pos"),
  extract_cell_draws(fit_answer_SC, AnswerCertainty == "high_certainty" & AnswerPolarity == "positive", "high_pos"),
  extract_cell_draws(fit_answer_SC, AnswerCertainty == "exhaustive"    & AnswerPolarity == "positive", "exh_pos"),
  extract_cell_draws(fit_answer_SC, AnswerCertainty == "low_certainty" & AnswerPolarity == "negative", "low_neg"),
  extract_cell_draws(fit_answer_SC, AnswerCertainty == "high_certainty" & AnswerPolarity == "negative", "high_neg"),
  extract_cell_draws(fit_answer_SC, AnswerCertainty == "exhaustive"    & AnswerPolarity == "negative", "exh_neg")
) 

# all posterior 95% HDIs are wayquire above 0 
cellDraws_answers %>% as.matrix() %>% 
  apply(., 2, aida::summarize_sample_vector)

# posterior probability of mean bigger 1 for each cell is 1
as.matrix(cellDraws_answers) %>% 
  apply(., 2, function(x) {mean(x>0)})

# Result: belief change in each cell is credibly bigger than zero

# 2. check if there is a main effect of polarity, and whether 
# the expected ordering (low < high < exh) is borne out

AnswerPolarity_main <- compare_groups(
  fit_answer_SC,
  lower = AnswerPolarity == "positive",
  higher  = AnswerPolarity == "negative"
)

AnswerCertainty_lowVShigh <- compare_groups(
  fit_answer_SC,
  lower   = AnswerCertainty == "low_certainty",
  higher  = AnswerCertainty == "high_certainty"
)

AnswerCertainty_highVSexh <- compare_groups(
  fit_answer_SC,
  lower   = AnswerCertainty == "high_certainty",
  higher  = AnswerCertainty == "exhaustive"
)

results_answer_SC <- tribble(
  ~comparison, ~posterior, ~"95%HDI (low)", ~"95%HDI (high)",
  "polarity (main)" , AnswerPolarity_main$post_prob, AnswerPolarity_main$l_ci, AnswerPolarity_main$u_ci,  
  "polarity (main)" , AnswerCertainty_lowVShigh$post_prob, AnswerCertainty_lowVShigh$l_ci, AnswerCertainty_lowVShigh$u_ci,  
  "polarity (main)" , AnswerCertainty_highVSexh$post_prob, AnswerCertainty_highVSexh$l_ci, AnswerCertainty_highVSexh$u_ci  
)

# Results:
# no indication of a main effect of polarity
# support for the claim that our manipulation of AnswerCertainty induced gradually larger belief changes

# # # # # # # # # # # # # # # # # # # # 
## plotting ----
# # # # # # # # # # # # # # # # # # # # 

# the "group" variable has likely no impact so we can gloss over it.
# still let's first show a plot that has everything (using "groups") separately

d %>% 
  filter(group == "relevant") %>% 
  ggplot(aes(x = `relevance rating`, color = AnswerPolarity, fill = AnswerPolarity)) +
  facet_grid(AnswerCertainty ~ ContextType , scales = "free") +
  geom_density(alpha = 0.3) +
  ggtitle("trigger word: 'relevant'")

d %>% 
  filter(group == "helpful") %>% 
  ggplot(aes(x = `relevance rating`, color = AnswerPolarity, fill = AnswerPolarity)) +
  facet_grid(AnswerCertainty ~ ContextType , scales = "free") +
  geom_density(alpha = 0.3) +
  ggtitle("trigger word: 'helpful'")


# d %>% 
#   ggplot(aes(x = AnswerCertainty, y = `relevance rating`)) +
#   geom_violin() +
#   facet_grid(`trigger word` AnswerPolarity)
# 
# contextSubset <- "positive"
# d %>% 
#   filter(ContextType == contextSubset) %>% 
#   ggplot(aes(x = `relevance rating`, color = `trigger word`, fill = `trigger word`)) +
#   geom_density(alpha = 0.4) +
#   facet_grid(AnswerPolarity~AnswerCertainty, scales = "free" )

p <- ggpairs(iris, aes(color = Species)) + theme_bw()
for(i in 1:p$nrow) {
  for(j in 1:p$ncol){
    p[i,j] <- p[i,j] + 
      scale_fill_manual(values=c("#00AFBB", "#E7B800", "#FC4E07")) +
      scale_color_manual(values=c("#00AFBB", "#E7B800", "#FC4E07"))  
  }
}
p

predictiveFactors <- c(
  "relevance_sliderResponse",
  "kl",
  "bayes_factor",
  "exp_bayes_factor",
  "entropy_reduction",
  "prior_posterior_distance"
)

predFactorMatrix <- d %>% select(all_of(predictiveFactors)) %>% as.matrix()

ggcorr(predFactorMatrix, palette = "RdBu")

p <- ggpairs(d %>% select(all_of(predictiveFactors), AnswerCertainty),
        aes(color = AnswerCertainty)) + theme_aida()
for(i in 1:p$nrow) {
  for(j in 1:p$ncol){
    p[i,j] <- p[i,j] + 
      scale_fill_manual( values=project_colors) +
      scale_color_manual(values=project_colors)  
  }
}
p

# # # # # # # # # # # # # # # # # # # # 
## analysis (experimental factors) ----
# # # # # # # # # # # # # # # # # # # # 

# I'm ommitting interactions in the REs because of the unbalanced (factorial) design
# TODO rethink this
formula = relevance_sliderResponse ~ group * ContextType * AnswerCertainty * AnswerPolarity + 
  (1 + group + ContextType + AnswerCertainty + AnswerPolarity | StimID) + 
  (1 + ContextType + AnswerCertainty + AnswerPolarity | submission_id)

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

draws_ContextType <- 
  tibble(
    extract_cell_draws(fit, ContextType == "positive", colname = "positive"),
    extract_cell_draws(fit, ContextType == "negative", colname = "negative"),
    extract_cell_draws(fit, ContextType == "neutral", colname = "neutral")
  ) %>% pivot_longer(cols = everything())

draws_ContextType %>% 
  ggplot(aes(x = value, color = name, fill = name)) +
  geom_density(alpha = 0.3)

ContextType_neutral <- 
  compare_groups(fit, higher = ContextType == "neutral", lower = ContextType != "neutral")

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
  "Context neutral > pos/neg", ContextType_neutral$post_prob, ContextType_neutral$l_ci, ContextType_neutral$u_ci
)

cellComparisons

# RESULTS:
# there is no (strong) indication for a main effect of trigger word, answer polarity or contextual bias
#   this would speak against KL- and ER-based notions because these do depend on prior
# there does seem to be an effect of answer type (certainty), but that's predicted on all accounts

# # # # # # # # # # # # # # # # # # # # 
## analysis (predictive factors) ----
# # # # # # # # # # # # # # # # # # # # 

#### simple comparison using `BayesFactor` package ----

BFComp <- generalTestBF(relevance_sliderResponse ~ exp_bayes_factor + entropy_reduction + kl, 
                        data = as.data.frame(d %>% filter(! is.na(kl))))
plot(BFComp)

#### model comparison using LOO-CV ----

fit_predFactors_all <- brm(
  relevance_sliderResponse ~ exp_bayes_factor + entropy_reduction + kl,
  iter = 4000,
  prior = prior(student_t(1, 0, 5), class = "b"),
  sample_prior = T,
  data = d %>% filter(! is.na(kl))
)

fit_predFactors_dropKL <- brm(
  relevance_sliderResponse ~ exp_bayes_factor + entropy_reduction,
  iter = 4000,
  prior = prior(student_t(1, 0, 5), class = "b"),
  sample_prior = T,
  data = d %>% filter(! is.na(kl))
)

fit_predFactors_dropBF <- brm(
  relevance_sliderResponse ~ entropy_reduction + kl,
  iter = 4000,
  prior = prior(student_t(1, 0, 5), class = "b"),
  sample_prior = T,
  data = d %>% filter(! is.na(kl))
)

fit_predFactors_dropER <- brm(
  relevance_sliderResponse ~ exp_bayes_factor + kl,
  iter = 4000,
  prior = prior(student_t(1, 0, 5), class = "b"),
  sample_prior = T,
  data = d %>% filter(! is.na(kl))
)

fit_predFactors_all    <- add_criterion(fit_predFactors_all, "loo", model_name = "all")
fit_predFactors_dropER <- add_criterion(fit_predFactors_dropER, "loo", model_name = "dropER")
fit_predFactors_dropBF <- add_criterion(fit_predFactors_dropBF, "loo", model_name = "dropBF")
fit_predFactors_dropKL <- add_criterion(fit_predFactors_dropKL, "loo", model_name = "dropKL")

loo_compare(
  fit_predFactors_all   ,   
  fit_predFactors_dropER,
  fit_predFactors_dropBF, 
  fit_predFactors_dropKL 
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
