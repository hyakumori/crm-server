<template>
  <div class="range-date-picker">
    <h5>{{ label }}</h5>
    <v-menu
      ref="menu"
      v-model="menu"
      transition="scale-transition"
      min-width="290px"
      offset-y
      :close-on-content-click="false"
      :return-value.sync="innerDates"
    >
      <template v-slot:activator="{ on }">
        <v-text-field
          v-model="dateRange"
          height="45"
          dense
          single-line
          outlined
          readonly
          v-on="on"
        ></v-text-field>
      </template>
      <v-date-picker v-model="innerDates" range no-title scrollable>
        <v-spacer></v-spacer>
        <v-btn text color="primary" @click="menu = false">キャンセル</v-btn>
        <v-btn text color="primary" @click="save">OK</v-btn>
      </v-date-picker>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "range-date-picker",

  props: {
    label: String,
    dates: Array,
  },

  data() {
    return {
      menu: false,
      innerDates: this.dates,
    };
  },

  methods: {
    save() {
      this.$refs.menu.save(this.innerDates);
      this.$emit("newDates", this.innerDates);
    },
  },

  computed: {
    dateRange() {
      return this.innerDates
        .map(date => date.replace(new RegExp("-", "g"), "/"))
        .join(" - ");
    },
  },
};
</script>

<style lang="scss" scoped>
$font-size: 14px;

.range-date-picker ::v-deep {
  h5 {
    font-size: $font-size;
    color: #444444;
    font-weight: bold;
  }

  fieldset {
    border: 1px solid #e1e1e1;
    border-radius: 4px;
  }

  input {
    font-size: $font-size;
    color: #999999;
  }
}
</style>
