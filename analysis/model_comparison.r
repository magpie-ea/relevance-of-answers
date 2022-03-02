library(tidyverse)
#library(lme4)
library(dplyr)
library(BayesFactor)
# library(ggpubr)


data <- read_csv("relevance-of-answers/results/pilot/results_processed.csv")

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
)



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

# run big comparison over subsets of four-factor model
all_models = generalTestBF(Rel ~ KLU + EntR + Pos + PPD, 
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


