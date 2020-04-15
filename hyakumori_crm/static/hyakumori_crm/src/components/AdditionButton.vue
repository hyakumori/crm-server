<template>
  <v-btn text color="primary" @click="onClick">
    <v-icon left>mdi-plus</v-icon>
    {{ content }}
  </v-btn>
</template>

<script>
export default {
  name: "addition-button",

  props: {
    content: String,
    click: Function,
  },

  methods: {
    onClick() {
      this.click();
    },
  },
};
</script>
