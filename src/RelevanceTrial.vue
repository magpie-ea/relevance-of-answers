<!-- RelevanceTrial.vue -->
<template>
  <Screen :progress="progress">
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
        :response.sync="$magpie.measurements.launch"
        :keys="{
          '~': 'next'
        }"
        @update:response="$magpie.saveAndNextScreen()"
      />

      <div
        v-if="
          item.TrialType == 'practice' &&
          !sliderResponseClicked &&
          item.TaskType.includes('prior')
        "
        class="callout"
      >
        <p>
          <strong>Instructions:</strong> Each trial starts with the description
          of a context. Always read this description very carefully.
        </p>
      </div>

      <span style="color: gray;">Context:</span> {{ item.Context }}
      <br />
      <br />
      {{ item.YourQuestionIntro }}
      <br />
      <strong>"{{ item.YourQuestion }}"</strong>
      <br />
      <br />

      <!-- show answer unless 'prior' or 'reasoning' trials -->
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
      <!-- show additional information in 'reasoning' trials -->
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

      <!-- instructions for practice trials PRIOR -->
      <div
        v-if="
          item.TrialType == 'practice' &&
          !sliderResponseClicked &&
          item.TaskType.includes('prior')
        "
        class="callout"
      >
        <p>
          <strong>Instructions:</strong> Then you judge the probability that the
          content of the question might be true. Drag the slider to give your
          best guess at the probability. Don't worry if there's not enough
          information to choose an exact probability. Just give us an intuitive
          guess.
        </p>
      </div>

      <!-- instructions for practice trials POSTERIOR -->
      <div
        v-if="
          item.TrialType == 'practice' &&
          !sliderResponseClicked &&
          item.TaskType.includes('posterior')
        "
      >
        <div class="callout">
          <p>
            <strong>Instructions:</strong>
            Next, you will be shown an answer to your question. Read this answer
            carefully, and judge the probability that the statement is true
            <strong>with this new information.</strong>
          </p>
        </div>
      </div>
      <!-- instructions for practice trials RELEVANCE -->
      <div
        v-if="
          item.TrialType == 'practice' && item.TaskType.includes('relevance')
        "
      >
        <div class="callout">
          <p>
            Now tell us how
            <strong>{{ group == 'helpful' ? 'helpful' : 'relevant' }}</strong>
            Jess's answer was in response to your question. Jess's answer
            doesn't directly answer the question, but you would probably find it
            pretty {{ group == 'helpful' ? 'helpful' : 'relevant' }} in this
            context. So move the slider towards the right.
          </p>
        </div>
      </div>

      <!-- Task question -->
      <!-- this replacement breaks if the string 'helpful' occurs in a 'likelihood' question -->
      <strong>{{
        group == 'helpful'
          ? item.TaskQuestion
          : item.TaskQuestion.replace('helpful', 'relevant')
      }}</strong>

      <div
        v-if="
          item.TaskType.includes('posterior') ||
          item.TrialType.includes('reasoning')
        "
        style="color: gray;"
      >
        [<strong>Reminder</strong>: Before receiving the answer you selected
        probability {{ lastTrial.sliderResponse }}% and indicated a commitment
        level {{ lastTrial.confidence }}.]
      </div>

      <SliderInput
        :left="
          group == 'helpful'
            ? item.SliderLabelLeft
            : item.SliderLabelLeft.replace('unhelpful', 'irrelevant')
        "
        :right="
          group == 'helpful'
            ? item.SliderLabelRight
            : item.SliderLabelRight.replace('helpful', 'relevant')
        "
        :response.sync="$magpie.measurements.sliderResponse"
        :disabled="sliderResponseClicked"
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
        You selected {{ $magpie.measurements.sliderResponse }} on a scale from 0
        to 100.
      </span>

      <div
        v-if="
          item.TrialType == 'practice' &&
          !sliderResponseClicked &&
          item.TaskType.includes('prior') &&
          $magpie.measurements.sliderResponse >= 0 &&
          !item.TaskType.includes('relevance')
        "
        class="callout"
      >
        <p>
          <strong>Instructions:</strong>
          The Eiffel Tower seems like a pretty "unmissable" site, so to a lot of
          people a probability between 50% and 90% seems reasonable.
        </p>
      </div>

      <div
        v-if="
          item.TrialType == 'practice' &&
          !sliderResponseClicked &&
          item.TaskType.includes('posterior') &&
          $magpie.measurements.sliderResponse >= 0 &&
          !item.TaskType.includes('relevance')
        "
        class="callout"
      >
        <p>
          <strong>Instructions:</strong>
          It's pretty unlikely that Aaron will go to the Eiffel Tower if he
          hates it. So select a low probability, like 5%.
        </p>
      </div>

      <button
        v-if="
          $magpie.measurements.sliderResponse >= 0 &&
          !sliderResponseClicked &&
          !item.TaskType.includes('relevance')
        "
        @click="toggleSliderResponseFlag()"
      >
        Continue
      </button>
      <br />

      <!-- instructions for practice trials PRIOR CONFIDENCE -->
      <div
        v-if="
          item.TrialType == 'practice' &&
          sliderResponseClicked &&
          item.TaskType.includes('prior') &&
          !item.TaskType.includes('relevance')
        "
      >
        <div class="callout">
          <p>
            <strong>Instructions:</strong>
            We now ask you for how committed you are to the probability
            judgement you gave. In the case at hand, the probability is fairly
            hard to judge, so you may have low commitment to your judgment.
            Based on just this information, a high probability like 60% or 80%
            might be the best guess. But the context leaves open a strong
            possibility that a low probability like 40% or even 10% is more
            appropriate (for example, if Aaron doesn't consider the Eiffel tower
            "unmissable"). So maybe you could select a button on the lower end,
            like 1, 2, or 3.
          </p>
        </div>
      </div>

      <!-- instructions for practice trials POSTERIOR CONFIDENCE -->
      <div
        v-if="
          item.TrialType == 'practice' &&
          sliderResponseClicked &&
          item.TaskType.includes('posterior') &&
          !item.TaskType.includes('relevance')
        "
      >
        <div class="callout">
          <p>
            <strong>Instructions:</strong>
            Now tell us how committed you are to this second probability
            judgment. You might be more committed than before that the
            probability is very low, like 1% or 5%. Other similar probabilities
            like 2% or 10% are plausible, but very different probabilities like
            60% or 80% are unreasonable. So select a button that's higher than
            before, like 4, 5, or 6.
          </p>
        </div>
      </div>

      <strong
        v-if="sliderResponseClicked && !item.TaskType.includes('relevance')"
      >
        How committed are you to the probability being around
        {{ $magpie.measurements.sliderResponse }}%?
      </strong>
      <RatingInput
        v-if="sliderResponseClicked && !item.TaskType.includes('relevance')"
        left="weakly committed"
        right="strongly committed"
        :response.sync="$magpie.measurements.confidence"
      />
      <div v-if="$magpie.measurements.confidence == 1">
        {{ $magpie.measurements.confidence }}
      </div>

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
    },
    group: {
      type: String,
      required: true
    },
    progress: {
      type: Number,
      default: undefined
    }
  },
  data() {
    return {
      sliderResponseClicked: false
    };
  },
  computed: {
    lastTrial() {
      const data = this.$magpie.getAllData();
      return data[data.length - 1];
    }
  },
  methods: {
    toggleSliderResponseFlag: function () {
      if (this.sliderResponseClicked) {
        this.sliderResponseClicked = false;
      } else {
        this.sliderResponseClicked = true;
      }
    }
  }
};
</script>
