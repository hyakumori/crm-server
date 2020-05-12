<template>
  <ValidationProvider
    :vid="vid"
    :rules="rules"
    :name="name || label"
    mode="aggressive"
    v-slot="{ errors }"
    slim
  >
    <v-text-field
      :disabled="disabled"
      v-model="innerValue"
      single-line
      dense
      outlined
      height="45"
      :maxlength="maxLength"
      :hide-details="hideDetails"
      :type="type"
      :placeholder="placeholder"
      :error-messages="errors[0]"
    ></v-text-field>
  </ValidationProvider>
</template>

<script>
import { ValidationProvider } from "vee-validate";

export default {
  name: "text-input",
  components: {
    ValidationProvider,
  },
  props: {
    vid: {
      type: String,
      default: undefined,
    },
    name: {
      type: String,
      default: "",
    },
    label: {
      type: String,
      default: "",
    },
    rules: {
      type: [Object, String],
      default: "",
    },
    placeholder: {
      type: String,
      default: "",
    },
    disabled: { type: Boolean, default: false },
    hideDetails: {
      type: [String, Boolean],
      default: "auto",
    },
    type: {
      type: String,
      default: "text",
      validator(value) {
        return [
          "url",
          "text",
          "password",
          "tel",
          "search",
          "number",
          "email",
        ].includes(value);
      },
    },
    value: {
      type: null,
      default: "",
    },
    maxLength: Number,
  },
  data: () => ({
    innerValue: "",
  }),
  computed: {
    hasValue() {
      return !!this.innerValue;
    },
  },
  watch: {
    innerValue(value) {
      this.$emit("input", value);
    },
    value(val) {
      if (val !== this.innerValue) {
        this.innerValue = val;
      }
    },
  },
  created() {
    if (this.value) {
      this.innerValue = this.value;
    }
  },
};
</script>
