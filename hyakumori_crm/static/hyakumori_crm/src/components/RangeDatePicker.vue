<template>
  <div class="range-date-picker">
    <h5>{{ label }}</h5>
    <v-menu
      ref="menu"
      v-model="menu"
      transition="scale-transition"
      min-width="290px"
      offset-y
      nudge-top="20"
      :close-on-content-click="false"
      :return-value.sync="innerDates"
    >
      <template v-slot:activator="{ on }">
        <ValidationProvider rules="daterange" v-slot="{ errors }">
          <v-text-field
            v-model="innerDateRange"
            height="45"
            dense
            placeholder="例：2020-12-24 ～ 2025-12-24"
            single-line
            v-mask="'####-##-##～####-##-##'"
            outlined
            v-on="on"
            :error-messages="errors[0]"
          ></v-text-field>
        </ValidationProvider>
      </template>
      <v-date-picker
        v-model="innerDates"
        range
        no-title
        scrollable
        reactive
        @change="() => save(false)"
      >
        <v-spacer></v-spacer>
        <v-btn text color="primary" @click="menu = false">キャンセル</v-btn>
        <v-btn text color="primary" @click="save">OK</v-btn>
      </v-date-picker>
    </v-menu>
  </div>
</template>

<script>
import i18n from "../plugins/i18n";
import { format, isValid, parse } from "date-fns";
import { dateSeparator } from "../helpers/datetime";
import { ValidationProvider, extend } from "vee-validate";
import { split } from "lodash";

extend("daterange", {
  validate: value => {
    let result = [];
    let parts = split(value, dateSeparator).map(part => part.trim());
    if (isValid(parse(parts[0], "yyyy-MM-dd", new Date()))) {
      result.push(parts[0]);
    } else return false;
    if (parts[1] && parts[1] !== "") {
      if (isValid(parse(parts[1], "yyyy-MM-dd", new Date()))) {
        result.push(parts[1]);
      } else return false;
    }
    return (
      (result.length === 2 && result[0] < result[1]) || result.length === 1
    );
  },
  message: i18n.t("validations.daterange"),
});

export default {
  name: "range-date-picker",

  components: {
    ValidationProvider,
  },

  props: {
    label: String,
    dates: Array,
  },

  data() {
    return {
      menu: false,
      innerDates: this.dates,
      innerDateRange: this.dates.join(dateSeparator),
    };
  },

  methods: {
    save(closeMenu = true) {
      if (closeMenu) {
        this.$refs.menu.save(this.innerDates);
      }
      this.$emit("newDates", this.innerDates);
      this.innerDateRange = this.innerDates.join(dateSeparator);
    },
    rangeToInnerDate() {
      if (this.hasInvalidDate) {
        return;
      }
      const parts = this.innerDateRange
        .split(dateSeparator)
        .map(d => d.trim())
        .map(d => parse(d, "yyyy-MM-dd", new Date()))
        .filter(d => isValid(d))
        .map(d => format(d, "yyyy-MM-dd"));
      this.innerDates = parts;
    },
  },

  computed: {
    isDefaultDateEmpty() {
      return (
        this.innerDates.every(d => d.length === 0) ||
        this.innerDateRange.length === 0
      );
    },
    hasInvalidDate() {
      const parts = this.innerDateRange
        .split(dateSeparator)
        .map(part => part.trim())
        .map(d => parse(d, "yyyy-MM-dd", new Date()))
        .filter(d => isValid(d));
      return !(
        (parts.length === 2 && parts[0] < parts[1]) ||
        parts.length === 1
      );
    },
  },
  watch: {
    innerDateRange() {
      this.rangeToInnerDate();
      if (this.innerDateRange.length === 0) {
        this.$emit("newDates", ["", ""]);
      }
    },
    innerDates: {
      deep: true,
      handler(val) {
        this.$emit("newDates", val);
      },
    },
    menu() {
      if (this.menu === false) {
        this.rangeToInnerDate();
        this.$refs.menu.save(this.innerDates);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "src/styles/variables";

.range-date-picker ::v-deep {
  @extend %picker-shared;
}
</style>
