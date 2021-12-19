# Materials

Main trials are based on 12 vignettes (column: `StimID`), each of which is instantiated 21 times to realize each of the 21 different experimental conditions.
An experimental condition is defined as a triple of factors: 
  + `AnswerCertainty` w/ 3 levels: `high_certainty`, `low_certainty` and `non_answer`
  + `AnswerPolarity` w/ 2 levels: `negative` and `positive` (it is undefined for `non_answer`s)
  + `ContextType` w/ 3 levels: `negative`, `neutral` and `positive`

# Procedure

Each participant sees a total of 14 trials, of which 10 are *main trials*, 2 are *reasoning control trials* and 2 are *attention check trials*. The 10 main trials appear in randomized order. The reasoning control and attention check trials appear in the same order at the same positions in the experiment, namely the two reasoning control trials appear as 2nd and 8th trial and the two attention check trials appear as 5th and 13th trial.
 
The 10 main trials shown in each experiment are constructed by selecting 10 different vignettes at random (from the set of all 12 vignettes). 
Each participant sees four `high_certainty` and four `low_certainty` trials, as well as two `non_answer` trials.
The four `high_certainty` trials are realized as two `negative` and two `positive` instances of `AnswerPolarity`.
The same holds for `low_certainty.` 
There is no variation in this variable for `non_answer` trials.
The variable `ContextType` is randomly assigned on each trial.

# notes
- don't mention preferences for chocolate bars; might influence judgements
- must mention that there are only two kinds of candy bars inside the bag
- how can you buy another 20 tickets if there are only 10 in the jar?

