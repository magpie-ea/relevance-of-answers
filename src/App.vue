<style>
/* Callout box - fixed position at the bottom of the page */
.callout {
  position: fixed;
  top: 5px;
  left: -10px;
  margin-left: 20px;
  max-width: 220px;
  text-align: left;
  padding: 15px;
  background-color: #ebebeb;
  color: black;
  font-size: 15px;
}
</style>

<template>
  <Experiment title="Judging answers to questions.">
    <InstructionScreen :title="'Welcome!'">
      This experiment presents 16 scenarios with a short dialogue.<br /><br />
      Your job is to read the scenarios, and share some of your judgments about
      it.<br /><br />
      The experiment will take about 15 minutes to complete.<br /><br />
    </InstructionScreen>

    <InstructionScreen
      :title="'Let us start with a practice trial to make you familiar with this task.'"
    >
      <br /><br /><br /><br /><br />
    </InstructionScreen>

    <template v-for="(trial, i) in practiceItems">
      <RelevanceTrial :key="i" :trial-n-r="i" :item="trial" />
    </template>

    <InstructionScreen
      :title="'Practice is over. Click below to start the main experiment.'"
    >
      <br /><br /><br /><br /><br />
    </InstructionScreen>

    <template v-for="(trial, i) in items">
      <RelevanceTrial :key="i" :trial-n-r="i" :item="trial" />
    </template>

    <PostTestScreen />

    <DebugResultsScreen />
  </Experiment>
</template>

<script>
// Load data from csv files as javascript arrays with objects
import relevanceItems from '../trials/relevance_stimuli.csv';
import fillerItems from '../trials/relevance_fillers.csv';
import practiceItems from '../trials/practice_stimuli.csv';
import answerConditionsRaw from '../trials/answer-conditions.csv';
import _ from 'lodash';

var answerConditions = _.shuffle(answerConditionsRaw);

// creating trial structure
var vignettes = _.slice(_.shuffle(_.range(1, 12)), 0, 10);
var mainItems = _.flatMap(_.range(0, 10), function (i) {
  var contextTypeSample = _.sample(['neutral', 'positive', 'negative']);
  return _.filter(relevanceItems, function (o) {
    return (
      o.StimID == vignettes[i] &&
      o.AnswerCertainty == answerConditions[i].AnswerCertainty &&
      o.AnswerPolarity == answerConditions[i].AnswerPolarity &&
      o.ContextType == contextTypeSample
    );
  });
});

// console.log(mainItems)

var items = _.slice(mainItems, 0, 3).concat(
  fillerItems[0],
  fillerItems[1],
  _.slice(mainItems, 6, 12),
  fillerItems[4],
  _.slice(mainItems, 12, 18),
  fillerItems[2],
  fillerItems[3],
  _.slice(mainItems, 18, 24),
  _.slice(mainItems, 24, 27),
  fillerItems[5],
  _.slice(mainItems, 27, 30)
);

// console.log(items)

// import component
import RelevanceTrial from './RelevanceTrial.vue';

export default {
  name: 'App',
  components: {
    RelevanceTrial
  },
  data() {
    return {
      items: items,
      practiceItems: practiceItems
    };
  },
  computed: {
    // make lodash available in Vue template code
    _() {
      return _;
    }
  }
};
</script>
