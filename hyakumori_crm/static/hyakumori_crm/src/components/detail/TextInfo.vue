<template>
  <div class="text-info">
    <h5 v-if="label && label.length > 0">{{ label }}</h5>
    <text-input
      v-if="isUpdate"
      :rules="rules"
      :value="value"
      :name="name"
      @input="$emit('input', $event)"
    />
    <p class="text-break" v-else>
      {{ value }} <slot name="readonly-extend"></slot>
    </p>
  </div>
</template>

<script>
import TextInput from "../forms/TextInput";

export default {
  name: "text-info",

  components: {
    TextInput,
  },

  props: {
    label: String,
    value: [String, Number],
    rules: String,
    name: String,
    isUpdate: Boolean,
  },

  data() {
    return {
      innerValue: "",
    };
  },
};
</script>

<style lang="scss" scoped>
$text-color: #444444;
$font-size: 14px;

.text-info ::v-deep {
  .v-input__slot {
    fieldset {
      border-radius: 4px;
    }

    input {
      font-size: 14px;
      color: #333;
    }
  }

  h5 {
    color: $text-color;
    font-size: $font-size;
    font-weight: bold;
  }

  p {
    color: $text-color;
    font-size: $font-size;
  }

  .text-break {
    word-break: break-all;
  }
}
</style>
