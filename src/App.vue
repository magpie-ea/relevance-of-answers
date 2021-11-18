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

    <template >
        <Screen v-for="(item, i) in relevanceItems">

            <Slide>
                <Record :data="{
                               trialNr :i+1,
                               Trialtype : item.TrialType,
                               Contexttype : item.AnswerType,
                               StimID : item.StimID,
                               }"
                        />
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
                <span v-if="$magpie.measurements.sliderResponse >=0
                            && ! item.TrialType.includes('relevance')"
                      style="color:gray">
                    Your selection means that there is a
                    {{$magpie.measurements.sliderResponse}}% chance that
                    {{item.CriticalProposition}}.
                </span>
                <span v-if="$magpie.measurements.sliderResponse >=0
                            && item.TrialType.includes('relevance')"
                      style="color:gray">
                    Your selection means that you give this answer a helpfulness score of
                    {{$magpie.measurements.sliderResponse}} on a scale from 0 to 100.
                </span>

                <button v-if="($magpie.measurements.sliderResponse >=0
                              && sliderResponseClicked =='false'
                              && ! item.TrialType.includes('relevance'))"
                        @click="toggleSliderResponseFlag()">
                    Continue
                </button>
                <br>
                <strong v-if="sliderResponseClicked=='true'
                              && ! item.TrialType.includes('relevance')">
                    How confident are you that the probability is
                    {{$magpie.measurements.sliderResponse}}%?
                </strong>
                <RatingInput
                    v-if="sliderResponseClicked=='true' && ! item.TrialType.includes('relevance')"
                    left="highly unsure"
                    right="highly confident"
                    :response.sync= "$magpie.measurements.confidence"
                    />
                <button v-if="$magpie.measurements.confidence >=0
                              && ! item.TrialType.includes('relevance')"
                        @click="toggleSliderResponseFlag();$magpie.saveAndNextScreen();">
                    Submit
                </button>
                <button v-if="$magpie.measurements.sliderResponse >=0 && item.TrialType.includes('relevance')"
                        @click="toggleSliderResponseFlag();$magpie.saveAndNextScreen();">
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
// import relevanceItems from '../trials/relevance_stimuli_long.csv';
import relevanceItems from '../trials/relevance_stimuli_medium.csv';
import _ from 'lodash';

var sliderResponseClicked = 'false';
var imgpath = "myTest"

export default {
    name: 'App',
    data() {
        return {
            relevanceItems: relevanceItems,
            sliderResponseClicked: sliderResponseClicked,
            imgpath: imgpath,
            // Expose lodash.range to template above
            range: _.range
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
    }
};

</script>
