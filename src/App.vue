<template>
<Experiment title="_magpie demo">

  <InstructionScreen :title="'Welcome!'">
    This is a sample introduction screen.
    <br />
    <br />
    This screen welcomes the participant and gives general information about
    the experiment.
    <br />
    <br />
    This mock up experiment is a showcase of the functionality of magpie.
  </InstructionScreen>

  <!-- <InstructionScreen :title="'General Instructions'"> -->
    <!--   This is a sample instructions view. -->
    <!--   <br /> -->
    <!--   <br /> -->
    <!--   First you will go through two practice trials. The practice trial view -->
    <!--   uses magpie's forced choice trial input. -->
    <!-- </InstructionScreen> -->

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
    _.slice(mainItems,0,3).concat(
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
