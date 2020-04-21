<template>
  <v-select
    dense
    ref="selectList"
    append-icon="mdi-chevron-down"
    loading="false"
    :full-width="false"
    :items="actions"
    :placeholder="placeHolder"
    @change="onChangeSelectedItem"
    :value="value"
  ></v-select>
</template>

<script>
import { select } from "d3-selection";

export default {
  name: "select-list",

  props: {
    actions: Array,
    placeHolder: String,
    index: Number,
    value: String,
  },

  mounted() {
    this.reiszeInputPlaceHolderWidth();
  },
  methods: {
    reiszeInputPlaceHolderWidth() {
      const additionWidthSize = 2;
      const input = select(this.$refs.selectList)._groups[0][0].$refs.input;
      const placeHolderLength = input.placeholder.length;
      input.size = placeHolderLength + additionWidthSize;
    },

    resizeInputWidth() {
      const input = select(this.$refs.selectList)._groups[0][0].$refs.input;
      input.style.width = "1ch";
    },

    onChangeSelectedItem(val) {
      this.resizeInputWidth();
      this.$emit("selectedAction", val, this.index);
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
