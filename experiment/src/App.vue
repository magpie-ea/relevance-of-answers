<style>
/* Callout box - fixed position at the bottom of the page */
.callout {
  /* position: fixed; */
  /* top: 5px; */
  /* left: -10px; */
  /* margin-left: 20px; */
  /* max-width: 220px; */
  /* text-align: left; */
  /* padding: 15px; */
  background-color: #ebebeb;
  color: black;
  /* font-size: 15px; */
}
</style>

<template>
  <Experiment title="Judging answers to questions.">
    <InstructionScreen :title="'Welcome!'">
      This experiment presents 15 scenarios with a short dialogue.<br /><br />
      Your task is to read the scenarios, and share some of your judgments about
      them.<br /><br />
      <strong>Caveat:</strong> The experiment contains attention check trials.
      If you read carefully all of the text necessary to complete a trial, you
      will recognize the attention trials, because they tell you directly what
      you need to do in order to pass them.<br /><br />
      The experiment will take about {{ experimentType == 'relevance_only' ? '5' : '10-15' }} minutes to complete.<br /><br />
    </InstructionScreen>

    <InstructionScreen :title="'Instructions'">
      <template v-if="experimentType === 'relevance_only'">
        <p>You will be shown a dialogue with 3 parts:</p>
        <ol>
          <li>A context that establishes a scene</li>
          <li>A question from one person</li>
          <li>A response from another person.</li>
        </ol>
        <p>
          Your job is to judge on a scale from 0 to 100 how
          {{ group == 'helpful' ? 'helpful' : 'relevant' }} the second person's response was.
        </p>
      </template>

      <template v-else-if="experimentType === 'probability_and_relevance'">
        You’ll judge the probability of a statement being true, and then judge it
        again after receiving additional information. Both times you’ll also be
        asked to rate your level of commitment to your judgment. Finally, you'll be
        asked how {{ group == 'helpful' ? 'helpful' : 'relevant' }} the additional
        information was.
      </template>

      <br />
      Let us start with a practice trial to make you familiar with this task.
      <br /><br /><br /><br /><br />
    </InstructionScreen>

    <template v-for="(trial, i) in experimentType === 'relevance_only' ? practiceItems.slice(3,7) : practiceItems.slice(0,3)">
      <RelevanceTrial :key="i" :trial-n-r="i" :item="trial" :group="group" />
    </template>

    <InstructionScreen
      :title="'Practice is over. Click below to start the main experiment.'"
    >
      <br /><br /><br /><br /><br />
    </InstructionScreen>

    <template v-for="(trial, i) in items">
      <RelevanceTrial
        :key="i"
        :trial-n-r="i"
        :item="trial"
        :group="group"
        :progress="i / items.length"
      />/>
    </template>

    <PostTestScreen />

    <!-- <DebugResultsScreen /> -->
    <SubmitResultsScreen />
  </Experiment>
</template>

<script>
// Load data from csv files as javascript arrays with objects
import relevanceItems from '../trials/relevance_stimuli.csv';
import fillerItems from '../trials/relevance_fillers.csv';
import practiceItems from '../trials/practice_stimuli.csv';
import answerConditions from '../trials/answer-conditions.csv';
import _ from 'lodash';

var contextConditions = ['neutral', 'positive', 'negative'];

// group allocation: 'helpful' vs 'relevant'
//   whether participants see questions regarding helpfulness or relevance
//   all items are formulated in terms of helpfulness
//   if group is 'relevance', we substitute the relevant entries either
//   during the creation of the stimuli or in situ when the material is shown
var group = 'relevant';
//   var group = _.sample(['helpful', 'relevant']); // if you want to sample


var experimentType = 'relevance_only'; // if you want to run relevance trials only
// var experimentType = 'probability_and_relevance'; // if you want to run all judgment types

// creating trial structure
var vignettes = _.slice(_.shuffle(_.range(1, 13)), 0, 10);
var vAnswerConditions = _.shuffle(
  _.range(0, 7).concat(_.slice(_.shuffle(_.range(0, 7)), 0, 3))
);
var vContextConditions = _.shuffle([0, 0, 0, 1, 1, 1, 2, 2, 2]).concat([
  _.sample([0, 1, 2])
]);
var mainItems = _.flatMap(_.range(0, 10), function (i) {
  return _.filter(relevanceItems, function (o) {
    return (
      o.StimID == vignettes[i] &&
      o.AnswerCertainty ==
        answerConditions[vAnswerConditions[i]].AnswerCertainty &&
      o.AnswerPolarity ==
        answerConditions[vAnswerConditions[i]].AnswerPolarity &&
      o.ContextType == contextConditions[vContextConditions[i]]
    );
  });
});

if (experimentType == 'relevance_only') {
  var items = [
    mainItems[2],
    fillerItems[6],
    mainItems[5],
    mainItems[8],
    mainItems[11],
    fillerItems[8],
    mainItems[14],
    mainItems[17],
    fillerItems[7],
    // fillerItems[3],
    mainItems[20],
    mainItems[23],
    mainItems[26],
    fillerItems[9],
    mainItems[29],
  ]
} else if (experimentType == 'probability_and_relevance') {
  var items = _.slice(mainItems, 0, 3).concat(
    fillerItems[0],
    fillerItems[1],
    _.slice(mainItems, 3, 12),
    fillerItems[4],
    _.slice(mainItems, 12, 18),
    fillerItems[2],
    fillerItems[3],
    _.slice(mainItems, 18, 24),
    _.slice(mainItems, 24, 27),
    fillerItems[5],
    _.slice(mainItems, 27, 30)
  );
}


console.log(items)
for (let i = 0; i < items.length; i++) {
 console.log (
   i + " | " +
   items[i].StimID + " | " +
   items[i].AnswerCertainty + " | " +
   items[i].AnswerPolarity + " | " +
   items[i].ContextType + " | " +
   items[i].TrialType + " | " +
   items[i].TaskType
 );
}

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
      practiceItems: practiceItems,
      group: group,
      experimentType: experimentType
    };
  },
  computed: {
    // make lodash available in Vue template code
    _() {
      return _;
    }
  },
  mounted() {
    this.$magpie.addExpData({
      group: group,
      experimentType: experimentType
    });
  }
};
</script>
