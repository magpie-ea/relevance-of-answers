# README for the `trials` directory

This directory contains all the stimuli for the experiment and some pre-processing.

### Contents
1. `data_preparation/reshape_stimuli.py`: This script is responsible for taking the concise, 
   hand-written version of the stimuli, and translating into a format that `magpie` can use.
2. `data_preparation/stimuli.csv`: This is the concise, hand-written version of the stimuli.
3. `answer-conditions.csv`: This is a list of all 7 answer conditions, which `magpie` uses to construct an experiment.
4. `practice_stimuli.csv`: The stimuli for the practice trial. `StimID` 1 is used for Experiment 1, `StimID`s 2-5 are used for Experiment 2.
5. `relevance_fillers.csv`: The stimuli for the attention check and reasoning check trials. `StimID`s 1-2 and used for Experiment 1. `StimID`s 3-4 are used for Experiment 2.
6. `relevance_stimuli.csv`: The stimuli for the main trials in the long format that `magpie` requires.


# Overview

Now we give a summary of how the stimuli are structured, what the different conditions are, and how the experiment unfolds.

### Materials

Main trials are based on 12 vignettes (column: `StimID`), each of which is instantiated 21 times to realize each of the 21 different experimental conditions.
An experimental condition is defined as a triple of factors: 
  + `AnswerCertainty` w/ 4 levels: `exhaustive` `high_certainty`, `low_certainty` and `non_answer`
  + `AnswerPolarity` w/ 2 levels: `negative` and `positive` (it is undefined for `non_answer`s)
  + `ContextType` w/ 3 levels: `negative`, `neutral` and `positive`

### Procedure

Each participant sees a total of 14 trials, of which 10 are *main trials*, 2 are *reasoning control trials* and 2 are *attention check trials*. The 10 main trials appear in randomized order. The reasoning control and attention check trials appear in the same order at the same positions in the experiment, namely the two reasoning control trials appear as 2nd and 8th trial and the two attention check trials appear as 5th and 13th trial.
 
The 10 main trials shown in each experiment are constructed by selecting 10 different vignettes at random (from the set of all 12 vignettes). 
Each participant sees at least two `high_certainty`, two `low_certainty`, two `exhaustive`, and one `non-answer` trial. The remaining three answer conditions are sampled uniformly without replacement.
For `high_certainty`, `low_certainty`, `exhaustive` answers, at least one has a `positive` value and one has a `negative` value for `AnswerPolarity`.
There is no variation in this variable for `non_answer` trials.
For the variable `ContextType`, each participant sees at least three instances of `negative`, `neutral`, and `positive`, each.
The 10th `ContextType` is sampled uniformly.
`ContextType` conditions are sampled independently from `AnswerType` and `AnswerPolarity` conditions.


