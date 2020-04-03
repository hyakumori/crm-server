<template>
  <v-select
    ref="selectList"
    append-icon="mdi-chevron-down"
    loading="false"
    return-object
    :full-width="false"
    :items="actions"
    :placeholder="placeHolder"
    @change="onChangeSelectedItem"
  ></v-select>
</template>

<script>
import { select } from "d3";

export default {
  name: "select-list",

  props: {
    actions: Array,
    placeHolder: String,
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
      input.style.width = "2px";
    },

    onChangeSelectedItem(val) {
      this.resizeInputWidth();
      this.$emit("selectedAction", val);
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
