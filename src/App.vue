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
<Experiment title="_magpie demo">

  <InstructionScreen :title="'Welcome!'">
    This experiment presents 16 scenarios with a short dialogue.<br><br>
    Your job is to read the scenarios, and share some of your judgments about it.<br><br>
    The experiment will take about 15 minutes to complete.<br><br>
  </InstructionScreen>

  <InstructionScreen :title="'The next scenario will be a practice trial.'">
    <br><br><br><br><br>
  </InstructionScreen>

  <template v-for="(item, i) in items">
    <Screen :key="i">

      <Slide>
        <Record :data="{
                       trialNr         : i+1,
                       StimID          : item.StimID,
                       TrialType       : item.TrialType,
                       TaskType        : item.TaskType,
                       ContextType     : item.ContextType,
                       AnswerCertainty : item.AnswerCertainty,
                       AnswerPolarity  : item.AnswerPolarity,
                       p_min           : item.p_min,
                       p_max           : item.p_max,
                       certainty_min   : item.certainty_min,
                       certainty_max   : item.certainty_max,
                       }"
                />
        <KeypressInput
          :response.sync= "$magpie.measurements.lunch"
          :keys="{
                 '~': 'next'
                 }"
          @update:response="$magpie.saveAndNextScreen();" />

        <div v-if="(item.TrialType=='practice') && (sliderResponseClicked=='false') && (item.TaskType.includes('prior'))">
          <div class="callout">
            <p>
              Read the scenario, and then judge the probability of the statement.<br><br>
              Drag the slider to give your best guess at the probability.<br><br>
              Don't worry if there's not enough information to choose an exact probability.<br><br>
              The Eiffel Tower seems like a pretty "unmissable" site, so a probability between 50% and 90% seems reasonable.
            </p>
          </div>
        </div>

        <div v-if="(item.TrialType=='practice') && (sliderResponseClicked=='true') && (item.TaskType.includes('prior'))">
          <div class="callout">
            <p>
              It's hard to judge. The context makes me think Aaron might make an exception for the Eiffel Tower,
              but I can't tell if he'll think it's really worth it.<br><br>
              So select a button on the lower end, like 1, 2, or 3.
            </p>
          </div>
        </div>

        <div v-if="(item.TrialType=='practice') && (sliderResponseClicked=='false') && (item.TaskType.includes('posterior'))">
          <div class="callout">
            <p>
              Read Jess's response, and judge the probability of the statement with this new information.<br><br>
              It's pretty unlikely that Aaron will go to the Eiffel Tower if he hates it.<br><br>
              So select a low probability, like 5%.
            </p>
          </div>
        </div>

        <div v-if="(item.TrialType=='practice') && (sliderResponseClicked=='true') && (item.TaskType.includes('posterior'))">
          <div class="callout">
            <p>
              Now tell us how confident you are about the probability.<br><br>
              I'm much more confident than before that the probability is very low, but other probabilities like 2% or 10% are reasonable.<br><br>
              So select a button that's higher than before, like 4, 5, or 6.
            </p>
          </div>
        </div>

        <div v-if="(item.TrialType=='practice') && (item.TaskType.includes('relevance'))">
          <div class="callout">
            <p>
              Now tell us how <strong>helpful</strong> Jess's answer was in response to your question.<br><br>
              Jess's answer doesn't directly answer the question, but it's still pretty helpful.<br><br>
              So select a high value, like 70, 80, or 90.
            </p>
          </div>
        </div>


        <span style="color:gray">Context:</span> {{item.Context}}
        <br>
        <br>
        {{item.YourQuestionIntro}}
        <br>
        <strong>"{{item.YourQuestion}}"</strong>
        <br>
        <br>
        <div  v-if="! (item.TaskType.includes('prior') | item.TrialType.includes('reasoning'))"
              style="background-color:lightblue; display:inline-block">
          {{item.AnswerIntro}}
          <br>
          <strong>"{{item.Answer}}"</strong>
        </div>
        <div  v-if="! (item.TaskType.includes('prior')) && item.TrialType.includes('reasoning')"
              style="background-color:lightblue; display:inline-block">
          <strong>{{item.Answer}}</strong>
        </div>
        <br>
        <br>
        <strong>{{item.TaskQuestion}}</strong>

        <SliderInput
          :left="item.SliderLabelLeft"
          :right="item.SliderLabelRight"
          :response.sync= "$magpie.measurements.sliderResponse"
          :disabled="sliderResponseClicked=='true'"
          :initial="0"/>
        <span v-if="$magpie.measurements.sliderResponse >=0
                    && ! item.TaskType.includes('relevance')"
              style="color:gray">
          Your selection means that there is a
          {{$magpie.measurements.sliderResponse}}% chance that
          {{item.CriticalProposition}}.
        </span>
        <span v-if="$magpie.measurements.sliderResponse >=0
                    && item.TaskType.includes('relevance')"
              style="color:gray">
          Your selection means that you give this answer a helpfulness score of
          {{$magpie.measurements.sliderResponse}} on a scale from 0 to 100.
        </span>

        <button v-if="($magpie.measurements.sliderResponse >=0
                      && sliderResponseClicked =='false'
                      && ! item.TaskType.includes('relevance'))"
                @click="toggleSliderResponseFlag()">
          Continue
        </button>
        <br>
        <strong v-if="sliderResponseClicked=='true'
                      && ! item.TaskType.includes('relevance')">
          How confident are you that the probability is
          {{$magpie.measurements.sliderResponse}}%?
        </strong>
        <RatingInput
          v-if="sliderResponseClicked=='true' && ! item.TaskType.includes('relevance')"
          left="highly unsure"
          right="highly confident"
          :response.sync= "$magpie.measurements.confidence"
          />
        <button v-if="$magpie.measurements.confidence >=0
                      && ! item.TaskType.includes('relevance')"
                @click="toggleSliderResponseFlag();$magpie.saveAndNextScreen();">
          Submit
        </button>
        <button v-if="$magpie.measurements.sliderResponse >=0 && item.TaskType.includes('relevance')"
                @click="$magpie.saveAndNextScreen();">
          Submit
        </button>

      </Slide>

    </Screen>

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
var vignettes = _.slice(_.shuffle(_.range(1,12)), 0, 10)
var mainItems = _.flatMap(_.range(0,10), function(i) {
    var contextTypeSample = _.sample(['neutral', 'positive', 'negative']);
    return(_.filter(relevanceItems, function(o) {
        return(o.StimID == vignettes[i] &&
               o.AnswerCertainty == answerConditions[i].AnswerCertainty &&
               o.AnswerPolarity == answerConditions[i].AnswerPolarity &&
               o.ContextType == contextTypeSample)
    }))
})

// console.log(mainItems)

var items =
    _.slice(practiceItems,0,4).concat(
        _.slice(mainItems,0,3),
        fillerItems[0],
        fillerItems[1],
        _.slice(mainItems,6,12),
        fillerItems[4],
        _.slice(mainItems,12,18),
        fillerItems[2],
        fillerItems[3],
        _.slice(mainItems,18,24),
        _.slice(mainItems,24,27),
        fillerItems[5],
       _.slice(mainItems,27,30)
    )

// console.log(items)

var sliderResponseClicked = 'false';

export default {
    name: 'App',
    data() {
        return {
            mainItems             : mainItems,
            items                 : items,
            fillerItems           : fillerItems,
            sliderResponseClicked : sliderResponseClicked
        };
    },
    methods: {
        toggleSliderResponseFlag: function() {
            if (this.sliderResponseClicked == 'true') {
                this.sliderResponseClicked = 'false'
            } else {
                this.sliderResponseClicked = 'true'
            }
        }
    },
    computed: {
      // make lodash available in Vue template code
      _() {
       return _;
     }
 }
};

</script>
