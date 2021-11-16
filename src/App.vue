<template>
<Experiment title="_magpie demo">

  <!-- <InstructionScreen :title="'Welcome'"> -->
    <!--   This is a sample introduction screen. -->
    <!--   <br /> -->
    <!--   <br /> -->
    <!--   This screen welcomes the participant and gives general information about -->
    <!--   the experiment. -->
    <!--   <br /> -->
    <!--   <br /> -->
    <!--   This mock up experiment is a showcase of the functionality of magpie. -->
    <!-- </InstructionScreen> -->

  <!-- <InstructionScreen :title="'General Instructions'"> -->
    <!--   This is a sample instructions view. -->
    <!--   <br /> -->
    <!--   <br /> -->
    <!--   First you will go through two practice trials. The practice trial view -->
    <!--   uses magpie's forced choice trial input. -->
    <!-- </InstructionScreen> -->

  <template v-for="(item, i) in relevanceItems2">
    <Screen>

      <Slide>
        <span style="color:gray">Context:</span> {{item.Context}}
        <br>
        <br>
        {{item.YourQuestionIntro}}
        <br>
        <strong>"{{item.YourQuestion}}"</strong>
        <br>
        <br>
        <div  v-if="! item.TrialType.includes('prior')"
              style="background-color:lightblue; display:inline-block">
          {{item.AnswerIntro}}
          <br>
          <strong>"{{item.Answer}}"</strong>
        </div>
        <br>
        <br>
        <strong>{{item.TaskQuestion}}</strong>

        <SliderInput
          :left="item.SliderLabelLeft"
          :right="item.SliderLabelRight"
          disabled="likelihoodClicked"
          :initial="0"
          :response.sync= "$magpie.measurements.likelihood" />
        <span v-if="$magpie.measurements.likelihood >=0"
              style="color:gray">
          Your selection means that there is a {{$magpie.measurements.likelihood}}% chance that {{item.CriticalProposition}}.
        </span>
        <button v-if="($magpie.measurements.likelihood >=0 && likelihoodClicked =='false' && ! item.TrialType.includes('relevance'))"
                @click="toggleLikelihoodFlag()">
          Continue
        </button>
        <br>
        <strong v-if="likelihoodClicked=='true' && ! item.TrialType.includes('relevance')">
          How confident are you that the probability
          is {{$magpie.measurements.likelihood}}%? and {{item.TrialType.includes('relevance')}}
        </strong>
        <RatingInput
          v-if="likelihoodClicked=='true' && ! item.TrialType.includes('relevance')"
          left="highly unsure"
          right="highly confident"
          :response.sync= "$magpie.measurements.confidence"
          />
        <button v-if="$magpie.measurements.confidence >=0 && ! item.TrialType.includes('relevance')"
                @click="toggleLikelihoodFlag();addTrialInfo(item,i);$magpie.saveAndNextScreen();">
          Submit
        </button>
        <button v-if="$magpie.measurements.likelihood >=0 && item.TrialType.includes('relevance')"
                  @click="toggleLikelihoodFlag();addTrialInfo(item,i);$magpie.saveAndNextScreen();">
            Submit
          </button>

        </Slide>

        <!-- <Slide> -->
        <!--   <span style="color:gray">Context:</span> {{item.Context}} -->
        <!--     <br> -->
        <!--     {{item.YourQuestionIntro}} -->
        <!--     <br> -->
        <!--   <p v-if="! item.TrialType.includes('prior')"> -->
        <!--     <strong>"{{item.YourQuestion}}"</strong> -->
        <!--     <br> -->
        <!--     <br> -->
        <!--     {{item.AnswerIntro}} -->
        <!--     <br> -->
        <!--     <strong>"{{item.Answer}}"</strong> -->
        <!--   </p> -->
        <!--   <br> -->
        <!--   <br> -->
        <!--   <strong>How confident are in your previous rating that the probability is {{$magpie.measurements.likelihood}}%?</strong> -->

        <!--   <SliderInput -->
        <!--     left="highly unsure" -->
        <!--     right="highly confident" -->
        <!--     :initial="0" -->
        <!--     :response.sync= "$magpie.measurements.confidence" /> -->
        <!--   <span v-if="$magpie.measurements.confidence >=0" -->
        <!--         style="color:gray"> -->
        <!--     You selected confidence level {{$magpie.measurements.confidence}} (from 0 to 100). -->
        <!--   </span> -->
        <!--   <button v-if="$magpie.measurements.confidence" -->
        <!--           @click="$magpie.saveAndNextScreen();"> -->
        <!--     Submit -->
        <!--   </button> -->
        <!-- </Slide> -->

      </Screen>

        </template>


    <PostTestScreen />

    <DebugResultsScreen />
  </Experiment>
</template>

<script>
// Load data from csv files as javascript arrays with objects
// import relevanceItems from '../trials/relevance_stimuli_long.csv';
import relevanceItems2 from '../trials/relevance_stimuli_medium.csv';
import _ from 'lodash';

var likelihoodClicked = 'false';

export default {
    name: 'App',
    data() {
        return {
            // forced_choice,
            // multi_dropdown,
            // sentenceChoice,
            // imageSelection: _.shuffle(imageSelection),
            // sliderRating,
            // relevanceItems: relevanceItems,
            relevanceItems2: relevanceItems2,
            likelihoodClicked: likelihoodClicked,

            // Expose lodash.range to template above
            range: _.range
        };
    },
    methods: {
        showmf: function() {console.log("I can do this!")},
        addTrialInfo: function(item, i) {
            $magpie.measurements.trial_nr = i;
            $magpie.measurements.Trialtype = item.TrialType;
            $magpie.measurements.Contexttype = item.AnswerType;
            $magpie.measurements.StimID = item.StimID;
        },
        toggleLikelihoodFlag: function() {
            if (this.likelihoodClicked == 'true') {
                this.likelihoodClicked = 'false'
            } else {
                this.likelihoodClicked = 'true'
            }
        }
    }
};

</script>
