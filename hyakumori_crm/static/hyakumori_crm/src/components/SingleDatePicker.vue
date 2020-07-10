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
        <ValidationProvider :rules="rules" :name="name" v-slot="{ errors }">
          <v-text-field
            class="date-input"
            @change="emit('change', event)"
            dense
            height="45"
            outlined
            :readonly="readonly"
            single-line
            v-model="innerDate"
            v-on="on"
            :rules="rules"
            :error-messages="errors[0]"
          ></v-text-field>
        </ValidationProvider>
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
import { ValidationProvider } from "vee-validate";
export default {
  name: "single-date-picker",
  components: {
    ValidationProvider,
  },

  props: {
    name: String,
    label: String,
    date: String,
    readonly: { type: Boolean, default: true },
    rules: String,
  },

  data() {
    return {
      menu: false,
      innerDate: this.date,
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
  .date-input .v-text-field__details {
    margin-bottom: 0;
  }
}
</style>
