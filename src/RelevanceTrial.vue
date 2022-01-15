<!-- RelevanceTrial.vue -->
<template>
  <Screen>
    <Slide>
      <Record
        :data="{
          trialNr: trialNR + 1,
          StimID: item.StimID,
          TrialType: item.TrialType,
          TaskType: item.TaskType,
          ContextType: item.ContextType,
          AnswerCertainty: item.AnswerCertainty,
          AnswerPolarity: item.AnswerPolarity,
          p_min: item.p_min,
          p_max: item.p_max,
          certainty_min: item.certainty_min,
          certainty_max: item.certainty_max
        }"
      />
      <KeypressInput
        :response.sync="$magpie.measurements.lunch"
        :keys="{
          '~': 'next'
        }"
        @update:response="$magpie.saveAndNextScreen()"
      />

      <div
        v-if="
          item.TrialType == 'practice' &&
          sliderResponseClicked == 'false' &&
          item.TaskType.includes('prior')
        "
      >
        <div class="callout">
          <p>
            Read the scenario, and then judge the probability that the
            statement is true.<br /><br />
            Drag the slider to give your best guess at the probability.<br /><br />
            Don't worry if there's not enough information to choose an exact
            probability.<br /><br />
            The Eiffel Tower seems like a pretty "unmissable" site, so a
            probability between 50% and 90% seems reasonable.
          </p>
        </div>
      </div>

      <div
        v-if="
          item.TrialType == 'practice' &&
          sliderResponseClicked == 'true' &&
          item.TaskType.includes('prior')
        "
      >
        <div class="callout">
          <p>
            The probability is fairly hard to judge, so you may have low
            commitment to your judgment. Based on just this information, a
            high probability like 60% or 80% might be the best guess.
            But the context leaves open a strong possibility that a low probability
            like 40% or even 10% is more appropriate (for example, if Aaron
            doesn't consider the Eiffel tower "unmissable").<br /><br />
            So select a button on the lower end, like 1, 2, or 3.
          </p>
        </div>
      </div>

      <div
        v-if="
          item.TrialType == 'practice' &&
          sliderResponseClicked == 'false' &&
          item.TaskType.includes('posterior')
        "
      >
        <div class="callout">
          <p>
            Read Jess's response, and judge the probability that the statement
            is true <strong>with this new information.</strong><br /><br />
            It's pretty unlikely that Aaron will go to the Eiffel Tower if he
            hates it.<br /><br />
            So select a low probability, like 5%.
          </p>
        </div>
      </div>

      <div
        v-if="
          item.TrialType == 'practice' &&
          sliderResponseClicked == 'true' &&
          item.TaskType.includes('posterior')
        "
      >
        <div class="callout">
          <p>
            Now tell us how committed you are to your probability judgment.<br /><br />
            You might be more committed than before that the probability is very
            low, like 1% or 5%. Other similar probabilities like 2% or 10% are plausible,
            but very different probabilities like 60% or 80% are unreasonable.<br /><br />
            So select a button that's higher than before, like 4, 5, or 6.
          </p>
        </div>
      </div>

      <div
        v-if="
          item.TrialType == 'practice' && item.TaskType.includes('relevance')
        "
      >
        <div class="callout">
          <p>
            Now tell us how <strong>helpful</strong> Jess's answer was in
            response to your question.<br /><br />
            Jess's answer doesn't directly answer the question, but you would probably find it
            pretty helpful in this context.<br /><br />
            So move the slider towards the right.
          </p>
        </div>
      </div>

      <span style="color: gray;">Context:</span> {{ item.Context }}
      <br />
      <br />
      {{ item.YourQuestionIntro }}
      <br />
      <strong>"{{ item.YourQuestion }}"</strong>
      <br />
      <br />
      <div
        v-if="
          !(
            item.TaskType.includes('prior') |
            item.TrialType.includes('reasoning')
          )
        "
        style="background-color: lightblue; display: inline-block;"
      >
        {{ item.AnswerIntro }}
        <br />
        <strong>"{{ item.Answer }}"</strong>
      </div>
      <div
        v-if="
          !item.TaskType.includes('prior') &&
          item.TrialType.includes('reasoning')
        "
        style="background-color: lightblue; display: inline-block;"
      >
        <strong>{{ item.Answer }}</strong>
      </div>
      <br />
      <br />
      <strong>{{ item.TaskQuestion }}</strong>

      <SliderInput
        :left="item.SliderLabelLeft"
        :right="item.SliderLabelRight"
        :response.sync="$magpie.measurements.sliderResponse"
        :disabled="sliderResponseClicked == 'true'"
        :initial="0"
      />
      <span
        v-if="
          $magpie.measurements.sliderResponse >= 0 &&
          !item.TaskType.includes('relevance')
        "
        style="color: gray;"
      >
        Your selection means that there is around a
        {{ $magpie.measurements.sliderResponse }}% chance that
        {{ item.CriticalProposition }}.
      </span>
      <span
        v-if="
          $magpie.measurements.sliderResponse >= 0 &&
          item.TaskType.includes('relevance')
        "
        style="color: gray;"
      >
       You selected {{ $magpie.measurements.sliderResponse }} on a scale from 0 to 100.
      </span>

      <button
        v-if="
          $magpie.measurements.sliderResponse >= 0 &&
          sliderResponseClicked == 'false' &&
          !item.TaskType.includes('relevance')
        "
        @click="toggleSliderResponseFlag()"
      >
        Continue
      </button>
      <br />
      <strong
        v-if="
          sliderResponseClicked == 'true' &&
          !item.TaskType.includes('relevance')
        "
      >
        How committed are you to the probability being around
        {{ $magpie.measurements.sliderResponse }}%?
      </strong>
      <RatingInput
        v-if="
          sliderResponseClicked == 'true' &&
          !item.TaskType.includes('relevance')
        "
        left="weakly committed"
        right="strongly committed"
        :response.sync="$magpie.measurements.confidence"
      />
      <button
        v-if="
          $magpie.measurements.confidence >= 0 &&
          !item.TaskType.includes('relevance')
        "
        @click="
          toggleSliderResponseFlag();
          $magpie.saveAndNextScreen();
        "
      >
        Submit
      </button>
      <button
        v-if="
          $magpie.measurements.sliderResponse >= 0 &&
          item.TaskType.includes('relevance')
        "
        @click="$magpie.saveAndNextScreen()"
      >
        Submit
      </button>


    </Slide>
  </Screen>
</template>

<script>
var sliderResponseClicked = 'false';

export default {
  name: 'RelevanceTrial',
  props: {
    item: {
      type: Object,
      required: true
    },
    trialNR: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      sliderResponseClicked: sliderResponseClicked
    };
  },
  methods: {
    toggleSliderResponseFlag: function () {
      if (this.sliderResponseClicked == 'true') {
        this.sliderResponseClicked = 'false';
      } else {
        this.sliderResponseClicked = 'true';
      }
    }
  }
};
</script>
