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

    <!-- <Screen> -->

    <!--   <Slide> -->
    <!--     <p>Fries or soup?</p> -->
    <!--     <SliderInput -->
    <!--     initial="50" -->
    <!--         left="Fries" -->
    <!--         right="Soup" -->
    <!--         :response.sync= "$magpie.measurements.lunch" /> -->
    <!--     Lunch: {{$magpie.measurements.lunch}}% Soup -->
    <!--     <button @click="$magpie.saveAndNextScreen();">Submit</button> -->
    <!--   </Slide> -->

    <!-- </Screen> -->

  <template >
    <Screen v-for="(item, i) in relevanceItems2">

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
          :response.sync= "$magpie.measurements.sliderResponse"
          :initial="0"/>
        <span v-if="$magpie.measurements.sliderResponse >=0"
              style="color:gray">
          Your selection means that there is a
          {{$magpie.measurements.sliderResponse}}% chance that {{item.CriticalProposition}}.
        </span>
        <button v-if="($magpie.measurements.sliderResponse >=0 && sliderResponseClicked =='false' && ! item.TrialType.includes('relevance'))"
                @click="toggleSliderResponseFlag()">
          Continue
        </button>
        <br>
        <strong v-if="sliderResponseClicked=='true' && ! item.TrialType.includes('relevance')">
          How confident are you that the probability
          is {{$magpie.measurements.sliderResponse}}%? and {{item.TrialType.includes('relevance')}}
        </strong>
        <RatingInput
          v-if="sliderResponseClicked=='true' && ! item.TrialType.includes('relevance')"
          left="highly unsure"
          right="highly confident"
          :response.sync= "$magpie.measurements.confidence"
          />
        <button v-if="$magpie.measurements.confidence >=0 && ! item.TrialType.includes('relevance')"
                @click="toggleSliderResponseFlag();addTrialInfo(item,i);$magpie.saveAndNextScreen();">
          Submit
        </button>
        <button v-if="$magpie.measurements.sliderResponse >=0 && item.TrialType.includes('relevance')"
                  @click="toggleSliderResponseFlag();addTrialInfo(item,i);$magpie.saveAndNextScreen();">
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
        <!--   <strong>How confident are in your previous rating that the probability is {{$magpie.measurements.sliderResponse}}%?</strong> -->

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

var sliderResponseClicked = 'false';

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
            sliderResponseClicked: sliderResponseClicked,

            // Expose lodash.range to template above
            range: _.range
        };
    },
    methods: {
        showmf: function() {console.log("I can do this!")},
        addTrialInfo: function(item, i) {
            $magpie.measurements.trial_nr = i+1;
            $magpie.measurements.Trialtype = item.TrialType;
            $magpie.measurements.Contexttype = item.AnswerType;
            $magpie.measurements.StimID = item.StimID;
        },
        toggleSliderResponseFlag: function() {
            if (this.sliderResponseClicked == 'true') {
                this.sliderResponseClicked = 'false'
            } else {
                this.sliderResponseClicked = 'true'
            }
        }
    }
};

</script>
