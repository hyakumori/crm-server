<template>
  <div class="text-info">
    <h5>{{ label }}</h5>
    <select-input
      v-if="isUpdate"
      :value="value"
      :items="items"
      @input="$emit('input', $event)"
      :clearable="clearable"
    />
    <p v-else>{{ value.text }}</p>
  </div>
</template>

<script>
import SelectInput from "../forms/SelectInput";

export default {
  name: "text-info",

  components: {
    SelectInput,
  },

  props: {
    items: Array,
    label: String,
    value: [String, Number, Object],
    isUpdate: Boolean,
    clearable: { type: Boolean, default: false },
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
