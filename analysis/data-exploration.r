library(tidyverse)

d <- read_csv("../results/pilot/results_80_relevance-answers_pilot_0.2.csv") 

# 16 participants
d %>% pull(submission_id) %>% unique() %>% length()

# trial types per participant okay, except one main trial missing
d %>% group_by(TrialType, submission_id) %>% 
  summarize(n()) %>% View()

# everybody should see 10 different vignettes as main trials
# => correct, except one main trial missing
d %>% filter(TrialType == "main") %>% 
  group_by(submission_id) %>% 
  summarize(unique(StimID) %>% length()) %>% View()

# Each participant sees four `high_certainty` and four `low_certainty` trials, 
# as well as two `non_answer` trials.
# => ???
d %>% filter(TrialType == "main") %>% 
  group_by(AnswerCertainty, submission_id) %>% 
  summarize(n()/3) %>% View()
  
# first plotting
d_wrangled <-
  d %>% 
  filter(TrialType == "main") %>% 
  # exclude beta-testers
  filter(submission_id >=3009) %>% 
  pivot_wider(
    c(submission_id, StimID, AnswerCertainty, AnswerPolarity, ContextType), 
    names_from = TaskType, 
    values_from = c(sliderResponse, confidence)
    ) %>% 
  mutate(prob_diff = sliderResponse_posterior-sliderResponse_prior)

d_wrangled %>% 
  ggplot(aes(x = prob_diff, y = sliderResponse_relevance, color = AnswerPolarity)) + 
  geom_point()
  

