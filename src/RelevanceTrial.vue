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
            Read the scenario, and then judge the probability of the
            statement.<br /><br />
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
            It's hard to judge. The context makes me think Aaron might make an
            exception for the Eiffel Tower, but I can't tell if he'll think it's
            really worth it.<br /><br />
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
            Read Jess's response, and judge the probability of the statement
            with this new information.<br /><br />
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
            Now tell us how confident you are about the probability.<br /><br />
            I'm much more confident than before that the probability is very
            low, but other probabilities like 2% or 10% are reasonable.<br /><br />
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
            Jess's answer doesn't directly answer the question, but it's still
            pretty helpful.<br /><br />
            So select a high value, like 70, 80, or 90.
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
        Your selection means that there is about a
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
        Your selection means that you give this answer a helpfulness score of
        {{ $magpie.measurements.sliderResponse }} on a scale from 0 to 100.
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
        How confident are you that the probability is about
        {{ $magpie.measurements.sliderResponse }}%?
      </strong>
      <RatingInput
        v-if="
          sliderResponseClicked == 'true' &&
          !item.TaskType.includes('relevance')
        "
        left="highly unsure"
        right="highly confident"
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
