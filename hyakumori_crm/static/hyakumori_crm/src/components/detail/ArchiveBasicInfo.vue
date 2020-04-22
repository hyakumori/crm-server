<template>
  <v-row>
    <v-col cols="6">
      <range-date-picker
        v-if="isUpdate"
        label="協議日時|カレンダー"
        :dates="['2020-03-04', '']"
      />
      <text-info
        v-else
        label="協議日時|カレンダー"
        value="2020/3/4"
        :isUpdate="isUpdate"
        @input="input"
      />
      <text-info
        label="今後の対応"
        value="害虫駆除の発注先を検討する"
        :isUpdate="isUpdate"
        @input="input"
      />
    </v-col>

    <v-col cols="6">
      <text-info
        label="場所"
        value="岡山県倉敷市大谷4-1-3"
        :isUpdate="isUpdate"
        @input="input"
      />
      <archive-participant-card
        class="mt-3"
        :class="{ 'mt-6': isUpdate }"
        :isAuthor="true"
        name="山田花子"
      />
    </v-col>

    <div class="pl-3 container content">
      <h5>協議内容</h5>
      <v-textarea
        v-if="isUpdate"
        dense
        value="害獣駆除の進め方について相談。害獣駆除の進め方について相談。害獣駆除の進め方について相談。害獣駆除の進め方について相談。害獣駆除の進め方について相談。"
        :outlined="isUpdate"
      />
      <p v-else>
        害獣駆除の進め方について相談。害獣駆除の進め方について相談。害獣駆除の進め方について相談。害獣駆除の進め方について相談。害獣駆除の進め方について相談。
      </p>
    </div>
  </v-row>
</template>

<script>
import TextInfo from "./TextInfo";
import RangeDatePicker from "../RangeDatePicker";
import ArchiveParticipantCard from "./ArchiveParticipantCard";

export default {
  name: "archive-basic-info",

  components: {
    TextInfo,
    RangeDatePicker,
    ArchiveParticipantCard,
  },

  props: {
    info: Object,
    isUpdate: Boolean,
    isSave: Boolean,
  },

  methods: {
    input() {
      // TODO: Handle input
    },
  },
};
</script>

<style lang="scss" scoped>
.content ::v-deep {
  h5,
  p {
    color: #444444;
    font-size: 14px;
  }

  fieldset {
    border: 1px solid #e1e1e1;
  }

  textarea {
    color: #999999;
  }
}
</style>
