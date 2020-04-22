<template>
  <div class="text-info">
    <h5>{{ label }}</h5>
    <text-input
      v-if="isUpdate"
      :rules="rules"
      :value="value"
      :name="name"
      @input="$emit('input', $event)"
    />
    <p v-else>{{ value }}</p>
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
    value: String,
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
      border: 1px solid #e1e1e1;
    }

    input {
      font-size: 14px;
      color: #999999;
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
}
</style>
