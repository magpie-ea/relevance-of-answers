# Relevance of Answers

This repository contains code and data for an investigation into which of different notions of (Bayesian and information-theoretic) relevance best predict human judgements of an answer's helpfulness.

For detailed information about each subpart of the project, consult the `README.md` file contained in each subdirectory.

Clone the repository and set up the project with `npm install 16`

To run the experiment locally, run:
```
nvm use 16
npm run serve -- --host localhost
```

A live version is here: [https://magpie3-relevance-answers.netlify.app/](https://magpie3-relevance-answers.netlify.app/)

For detailed information about each subpart of the project, consult the `README.md` file contained in each subdirectory. 
- `analysis` contains all code related to data analysis
- `experiment` contains the code for the experiment
- `plotting` contains code for additional plotting (on top of what is inside `analysis`) 
- `qualitative-analysis` contains code supporting the exploratory qualitative analysis on top of `analysis`
- `results` contains the data from the runs of the experiment
