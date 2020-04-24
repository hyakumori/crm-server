<template>
  <v-btn text color="primary" medium @click="onClick" :id="id" class="f14">
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
    id: String,
  },

  methods: {
    onClick() {
      if (this.click) {
        this.click();
      }
    },
  },
};
</script>
