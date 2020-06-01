<template>
  <v-select
    v-model="innerValue"
    dense
    ref="selectList"
    append-icon="mdi-chevron-down"
    loading="false"
    :full-width="false"
    :items="actions"
    :placeholder="(!hasSelectedValue && placeHolder) || ''"
  ></v-select>
</template>

<script>
export default {
  name: "select-list",

  props: {
    actions: Array,
    placeHolder: String,
    index: Number,
    value: String,
  },

  data() {
    return {
      innerValue: this.value,
    };
  },

  mounted() {
    this.resizeInputWidth();
    this.resizeInputPlaceholderWidth();
  },

  methods: {
    resizeInputPlaceholderWidth() {
      let additionWidthSize = 6;
      const input = this.$refs.selectList.$el.getElementsByTagName("input")[0];
      let placeHolderLength = input.placeholder.length;
      let inputSize = placeHolderLength + additionWidthSize;
      if (this.hasSelectedValue) {
        inputSize = 1;
      } else {
        if (inputSize === 6) {
          inputSize = 14;
        }
        input.size = inputSize;
      }
    },

    resizeInputWidth() {
      const input = this.$refs.selectList.$el.getElementsByTagName("input")[0];
      if (this.hasSelectedValue) {
        input.style.width = "3ch";
      } else {
        input.style.width = "auto";
      }
    },
  },
  computed: {
    hasSelectedValue() {
      return this.innerValue || this.innerValue === 0;
    },
  },
  watch: {
    innerValue() {
      this.resizeInputWidth();
      this.resizeInputPlaceholderWidth();
      this.$emit("selectedAction", this.innerValue, this.index);
    },
    value() {
      this.innerValue = this.value;
    },
  },
};
</script>

<style lang="scss" scoped>
$select-list--font-size: 14px;

::v-deep .v-input__slot {
  width: fit-content;
  margin-bottom: 0;

  .v-select__selections .v-select__selection {
    font-size: $select-list--font-size;
    line-height: $select-list--font-size;
  }

  .v-select__selections input::placeholder {
    font-size: $select-list--font-size;
    width: fit-content !important;
  }
}
</style>
