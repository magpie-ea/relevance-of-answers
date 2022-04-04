library(tidyverse)
library(lme4)
library(dplyr)
library(BayesFactor)
# library(ggpubr)

# Make sure to setwd() to the main directory of the repository
data <- read_csv("results/pilot/results_processed.csv")

# Filter data to exlude points with high range 
# data <- dplyr::filter(data, prior_range < 0.75, posterior_range < 0.75, helpfulness_range < 0.75)

# Add prior-posterior difference to dataframe
# data["prior_posterior_diff"] <- data["posterior_mean"] - data["prior_mean"]

# rename factors to shorter names
data <- rename(data, 
    "Pos" ="posterior_sliderResponse", 
    "PPD" = "prior_posterior_distance",
    "EntR" = "entropy_reduction",
    "KLU" = "kl_util",
    "Ans" = "AnswerCertainty", 
    "Pol" = "AnswerPolarity",
    "Con" = "ContextType",
    "Rel" = "relevance_sliderResponse",
    "BFU" = "exp_bayes_factor",
    "Part" = "submission_id",
    "Group" = "group",
)

# Model 1: No random effects.
m1 <- lm(Rel ~ BFU, data=data)
summary(m1)
# 
# Call:
#   lm(formula = Rel ~ BFU, data = data)
# 
# Residuals:
#   Min      1Q  Median      3Q     Max 
# -0.8264 -0.1578  0.0667  0.1000  0.7263 
# 
# Coefficients:
#   Estimate Std. Error t value Pr(>|t|)    
# (Intercept)  0.27374    0.03542   7.729    5e-13 ***
#   BFU          0.64268    0.04757  13.511   <2e-16 ***
#   ---
#   Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
# 
# Residual standard error: 0.2355 on 202 degrees of freedom
# Multiple R-squared:  0.4747,	Adjusted R-squared:  0.4721 
# F-statistic: 182.6 on 1 and 202 DF,  p-value: < 2.2e-16


# Model 2: Random effects for Group, Participant, and Stimulus
m2 <- lmer(Rel ~ BFU + (1 | StimID) + (1 | Group) + (1 | Part), data=data)
summary(m2)

# Linear mixed model fit by REML ['lmerMod']
# Formula: Rel ~ BFU + (1 | StimID) + (1 | Group) + (1 | Part)
# Data: data
# 
# REML criterion at convergence: -2.4
# 
# Scaled residuals: 
#   Min      1Q  Median      3Q     Max 
# -3.5244 -0.6819  0.2793  0.4301  3.0882 
# 
# Random effects:
#   Groups   Name        Variance  Std.Dev.
# Part     (Intercept) 0.0002629 0.01622 
# StimID   (Intercept) 0.0000000 0.00000 
# Group    (Intercept) 0.0000000 0.00000 
# Residual             0.0552237 0.23500 
# Number of obs: 204, groups:  Part, 21; StimID, 12; Group, 2
# 
# Fixed effects:
#   Estimate Std. Error t value
# (Intercept)  0.27287    0.03556   7.674
# BFU          0.64396    0.04753  13.548
# 
# Correlation of Fixed Effects:
#   (Intr)
# BFU -0.881
# optimizer (nloptwrap) convergence code: 0 (OK)
# boundary (singular) fit: see ?isSingular


# Model 3: Random effect for Participant only
m3 <- lmer(Rel ~ BFU + (1 | Part), data=data)
summary(m3)

# Linear mixed model fit by REML ['lmerMod']
# Formula: Rel ~ BFU + (1 | Part)
# Data: data
# 
# REML criterion at convergence: -2.4
# 
# Scaled residuals: 
#   Min      1Q  Median      3Q     Max 
# -3.5244 -0.6819  0.2793  0.4301  3.0883 
# 
# Random effects:
#   Groups   Name        Variance Std.Dev.
# Part     (Intercept) 0.000263 0.01622 
# Residual             0.055224 0.23500 
# Number of obs: 204, groups:  Part, 21
# 
# Fixed effects:
#   Estimate Std. Error t value
# (Intercept)  0.27287    0.03556   7.674
# BFU          0.64396    0.04753  13.548
# 
# Correlation of Fixed Effects:
#   (Intr)
# BFU -0.881

# extract dataframe for custom plot


extract_df <- function(bf_object) {
  df <- bf_object@bayesFactor['bf']
  # add names as a column in df
  df <- setNames(cbind(rownames(df), df, row.names = NULL), c("name", "bf")) 
  # wrap x axis tick label text
  #df$name <- str_wrap(df$name, width = 4)
  # take exp of bf
  df$bf <- exp(df$bf)
  #round to 4 sig digs
  df$bf <- signif(df$bf, digits=4)
  return(df)
}

# MODEL COMPARISON CODE

# run big comparison over subsets of five-factor model
all_models = generalTestBF(Rel ~ BFU + KLU + EntR + Pos + PPD, 
                                  data = data,
                                  whichModels="all")
# builtin plotting sucks
#plot(all_models[1:4])
#plot(all_models[5:10])


model_comparison <- extract_df(all_models)

model_comparison %>% show

one_factor_comparison <- model_comparison[1:4,]
two_factor_comparison <- model_comparison[5:10,]

custom_bf_plot <- function(df, my_title) {
  plot <-
    ggplot(data=df, aes(x=reorder(name,bf), y=bf)) +
    geom_bar(stat="identity", fill="steelblue", width=0.7)+
    #geom_text(aes(label=), vjust=1.6, color="white", size=5)+
    scale_y_log10(n.breaks = 10)+ 
    theme_minimal() +
    theme(aspect.ratio = 4/3, 
          plot.title = element_text(size=13), 
          axis.text=element_text(size=11),
          axis.text.x = element_text(angle = -45, margin=margin(0,0,0,0), color = "black")
          )+
    labs(title = my_title, x = "", y = "Bayes Factor")
  return(plot)
}

  
# plots for one factor and two factor models
one_factor_plot <- custom_bf_plot(one_factor_comparison, "(a) One Factor Models")
show(one_factor_plot)

two_factor_plot <- custom_bf_plot(two_factor_comparison, "(b) Two Factor Models")
show(two_factor_plot)



answer_context_models = generalTestBF(Rel ~ 
                                            Ans
                                          + Con 
                                          + Ans:Con
                                          #+ PPD
                                          , data=data
                                          )


answer_PPD_models = generalTestBF(Rel ~ Ans + PPD,
                                    data=data)

answer_context_comparison <- extract_df(answer_context_models)

answer_PPD_comparison <- extract_df(answer_PPD_models)


# plots for one factor and two factor models
answer_context_plot <- custom_bf_plot(answer_context_comparison, "(c) Answer vs. Context")
show(answer_context_plot)

answer_PPD_plot <- custom_bf_plot(answer_PPD_comparison, "(d) Answer vs. PPD")
show(answer_PPD_plot)

#ggarrange(one_factor_plot, two_factor_plot, answer_context_plot, answer_PPD_plot, 
#          ncol = 4, nrow = 1, align = 'h')


