<template>
  <ValidationObserver ref="observer" v-slot="{ invalid }">
    <v-row>
      <v-col cols="6">
        <text-info
          :isUpdate="!isDetail || isUpdate"
          :label="$t('forms.labels.archive.title')"
          :name="$t('forms.labels.archive.title')"
          :value="info.title"
          @input="val => (info.title = val)"
          rules="required"
          v-if="!isDetail || isUpdate"
        />
        <single-date-picker
          :class="{ 'mt-6': !isDetail || isUpdate }"
          :date="date"
          :label="$t('forms.labels.archive.consultant_date')"
          @newDate="val => (innerDate = val)"
          v-if="isUpdate || !isDetail"
        />
        <text-info
          :isUpdate="isUpdate"
          :label="$t('forms.labels.archive.consultant_date_and_time')"
          :value="displayDatetimeFormat"
          v-else
        />
        <text-info
          :isUpdate="isUpdate || !isDetail"
          :label="$t('forms.labels.archive.future_action')"
          :value="info.future_action"
          @input="val => (info.future_action = val)"
        />
      </v-col>

      <v-col cols="6">
        <text-info
          :isUpdate="isUpdate || !isDetail"
          :label="$t('forms.labels.archive.location')"
          :name="$t('forms.labels.archive.location')"
          :value="info.location"
          @input="val => (info.location = val)"
          rules="required"
        />
        <time-picker
          :class="{ 'mt-6': !isDetail || isUpdate }"
          :label="$t('forms.labels.archive.consultant_time')"
          :time="time"
          @newTime="val => (innerTime = val)"
          v-if="isUpdate || !isDetail"
        />
        <archive-participant-card
          :isAuthor="true"
          :name="info.author"
          v-if="isUpdate || isDetail"
        />
      </v-col>

      <div class="pl-3 container content">
        <h5>{{ $t("forms.labels.archive.content") }}</h5>
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
import TextInfo from "./TextInfo";
import SingleDatePicker from "../SingleDatePicker";
import ArchiveParticipantCard from "./ArchiveParticipantCard";
import TimePicker from "../TimePicker";
import { ValidationObserver } from "vee-validate";
import { getDate, getTime, commonDatetimeFormat } from "../../helpers/datetime";

export default {
  name: "archive-basic-info",

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
  }

  fieldset {
    border: 1px solid #e1e1e1;
  }

  textarea {
    color: #999999;
  }
}
</style>
