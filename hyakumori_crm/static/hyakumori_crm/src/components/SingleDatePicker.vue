<template>
  <div class="single-date-picker">
    <h5>{{ label }}</h5>
    <v-menu
      :close-on-content-click="false"
      :return-value.sync="innerDate"
      min-width="290px"
      offset-y
      ref="menu"
      transition="scale-transition"
      v-model="menu"
    >
      <template v-slot:activator="{ on }">
        <v-text-field
          dense
          height="45"
          outlined
          readonly
          single-line
          v-model="innerDate"
          v-on="on"
          :rules="rules"
        ></v-text-field>
      </template>
      <v-date-picker no-title scrollable v-model="innerDate">
        <v-spacer></v-spacer>
        <v-btn @click="menu = false" color="primary" text>キャンセル</v-btn>
        <v-btn @click="save" color="primary" text>OK</v-btn>
      </v-date-picker>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "single-date-picker",

  props: {
    label: String,
    date: String,
  },

  data() {
    return {
      menu: false,
      innerDate: this.date,
      rules: [val => !!val || `${this.label}は必須項目です`],
    };
  },

  methods: {
    save() {
      this.$refs.menu.save(this.innerDate);
      this.$emit("newDate", this.innerDate);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "src/styles/variables";

.single-date-picker ::v-deep {
  @extend %picker-shared;
}
</style>
