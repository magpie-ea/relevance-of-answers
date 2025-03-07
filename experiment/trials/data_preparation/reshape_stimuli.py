import pandas as pd
import re

df = pd.read_csv("stimuli.csv")
df = df.set_index([x for x in df.columns if "answer" not in x])
df.columns = pd.Index([('Answer', 'non_answer', 'N/A'),
                ('Answer', 'exhaustive', 'positive'),
            ('Answer', 'high_certainty', 'positive'),
             ('Answer', 'low_certainty', 'positive'),
             ('Answer', 'low_certainty', 'negative'),
            ('Answer', 'high_certainty', 'negative'),
                ('Answer', 'exhaustive', 'negative')],
                          names=["", "AnswerCertainty", "AnswerPolarity"])

df = df.stack().stack()
df = df.reset_index(["context-neutral-bias", "context-positive-bias", "context-negative-bias"]).set_index(["Answer"], append=True)
df.columns = pd.Index([("Context", "neutral"), ("Context", "positive"), ("Context", "negative")], names=["", "ContextType"])
df = df.stack()
df = df.reset_index().set_index("StimID")

trials = []
for trial in ["prior", "posterior", "relevance"]:
    df_t = df.rename(lambda x: (x, trial), axis=1)
    df_t.columns = pd.Index(list(df_t.columns), names=["", "TaskType"])
    trials.append(df_t)
df = pd.concat(trials).stack()
df = df.reset_index(["TaskType"])
df["TrialType"] = "main"
df = df.set_index("TrialType", append=True).reset_index("TrialType")

df["SliderLabelLeft"] = df["TaskType"].apply(lambda x: "completely unhelpful" if x=="relevance" else "highly unlikely")
df["SliderLabelRight"] = df["TaskType"].apply(lambda x: "maximally helpful" if x=="relevance" else "highly likely")
df["CriticalProposition"] = df["CriticalProposition"].apply(lambda x: re.compile(r"The probability that (.*) is \{probability\}.").match(x).group(1))
df["YourQuestionIntro"] = df.apply(lambda x: x["YourQuestionIntro"].format(name=x["name"]), axis=1)
df["AnswerIntro"] = df.apply(lambda x: x["name"].capitalize() + " responds:", axis=1)
df = df.drop(["prompt-likelihood", "prompt-relevance", "prompt-helpfulness"], axis=1)

def get_task_question(row):
    if row["TaskType"] == "prior":
        return "How likely do you think it is that {cp}?".format(cp=row["CriticalProposition"])
    elif row["TaskType"] == "posterior":
        return "How likely do you think it is now, after hearing {name}'s answer, that {cp}?".format(name=row["name"], cp=row["CriticalProposition"])
    else:
        return "How helpful was {name}'s response to the question at hand?".format(name=row["name"])

df["TaskQuestion"] = df.apply(get_task_question, axis=1)

df.to_csv("../relevance_stimuli.csv")
