<template>
  <ValidationObserver ref="observer" v-slot="{ invalid }">
    <v-row>
      <v-col cols="6">
        <text-info
          :isUpdate="!isDetail || isUpdate"
          :label="$t('forms.labels.postalhistory.title')"
          :name="$t('forms.labels.postalhistory.title')"
          :value="info.title"
          @input="val => (info.title = val)"
          rules="required|max:255"
          v-if="!isDetail || isUpdate"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <single-date-picker
          :date="date"
          :label="$t('forms.labels.postalhistory.consultant_date')"
          @newDate="val => (innerDate = val)"
          v-if="isUpdate || !isDetail"
        />
        <text-info
          :isUpdate="isUpdate"
          :label="$t('forms.labels.postalhistory.consultant_date_and_time')"
          :value="displayDatetimeFormat"
          v-else
        />
      </v-col>

      <v-col cols="6">
        <time-picker
          :label="$t('forms.labels.postalhistory.consultant_time')"
          :time="time"
          @newTime="val => (innerTime = val)"
          v-if="isUpdate || !isDetail"
        />
        <archive-participant-card
          :isAuthor="true"
          :name="info.author"
          :card_id="info.author_id"
          v-if="isUpdate || isDetail"
        />
      </v-col>
    </v-row>
    <v-row>
      <div class="container content">
        <h5>{{ $t("forms.labels.postalhistory.content") }}</h5>
        <v-textarea
          :outlined="isUpdate || !isDetail"
          :value="info.content"
          dense
          v-if="isUpdate || !isDetail"
          v-model="info.content"
        />
        <p v-else>
          {{ info.content }}
        </p>
      </div>
    </v-row>
    <slot
      :info="info"
      :invalid="invalid || datetimePickerInvalid"
      name="create-btn"
    ></slot>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver } from "vee-validate";
import TextInfo from "../../components/detail/TextInfo";
import SingleDatePicker from "../../components/SingleDatePicker";
import ArchiveParticipantCard from "../../components/detail/ArchiveParticipantCard";
import TimePicker from "../../components/TimePicker";
import { getDate, getTime, commonDatetimeFormat } from "../../helpers/datetime";

export default {
  components: {
    TextInfo,
    ArchiveParticipantCard,
    SingleDatePicker,
    TimePicker,
    ValidationObserver,
  },

  props: {
    info: Object,
    isUpdate: Boolean,
    isSave: Boolean,
    isDetail: Boolean,
  },

  data() {
    return {
      innerDate: "",
      innerTime: "",
    };
  },

  computed: {
    displayDatetimeFormat() {
      return commonDatetimeFormat(this.info.archive_date);
    },

    date() {
      if (this.isDetail || this.isUpdate) {
        return this.info.archive_date ? getDate(this.info.archive_date) : "";
      } else {
        return this.innerDate || "";
      }
    },

    time() {
      if (this.isDetail || this.isUpdate) {
        return this.info.archive_date ? getTime(this.info.archive_date) : "";
      } else {
        return this.innerTime || "";
      }
    },

    datetimePickerInvalid() {
      return !this.date || !this.time;
    },
  },

  watch: {
    info: {
      deep: true,
      async handler() {
        const isValid = await this.$refs.observer.validate();
        this.$emit("archive:save-disable", !isValid);
      },
    },

    innerDate(val) {
      if (!this.isDetail) {
        this.info.archive_date = `${val} ${this.innerTime}`;
      }
    },

    innerTime(val) {
      if (!this.isDetail) {
        this.info.archive_date = `${this.innerDate} ${val}`;
      }
    },

    async isSave(val) {
      const isValid = await this.$refs.observer.validate();
      if (val && isValid) {
        const date = this.innerDate === "" ? this.date : this.innerDate;
        const time = this.innerTime === "" ? this.time : this.innerTime;
        this.info.archive_date = `${date} ${time}`;
        this.$emit("archive:update-basic-info", this.info);
      }
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
    word-break: break-word;
  }

  fieldset {
    border: 1px solid #e1e1e1;
  }

  textarea {
    color: #999999;
  }
}
</style>
