<template>
  <div class="time-picker">
    <h5>{{ label }}</h5>
    <v-menu
      :close-on-content-click="false"
      :return-value.sync="innerTime"
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
          v-model="innerTime"
          v-on="on"
          :rules="rules"
        ></v-text-field>
      </template>
      <v-time-picker format="24hr" scrollable v-model="innerTime">
        <v-spacer></v-spacer>
        <v-btn @click="menu = false" color="primary" text>キャンセル</v-btn>
        <v-btn @click="save" color="primary" text>OK</v-btn>
      </v-time-picker>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "time-picker",

  props: {
    label: String,
    time: String,
  },

  data() {
    return {
      menu: false,
      innerTime: this.time,
      rules: [val => !!val || `${this.label}は必須項目です`],
    };
  },

  methods: {
    save() {
      this.$refs.menu.save(this.innerTime);
      this.$emit("newTime", this.innerTime);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "src/styles/variables";

.time-picker ::v-deep {
  @extend %picker-shared;
}
</style>
