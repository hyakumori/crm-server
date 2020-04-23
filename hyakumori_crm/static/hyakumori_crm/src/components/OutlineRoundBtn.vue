<template>
  <v-btn rounded dark outlined v-on="on" @click="$emit('click', $event)">
    <v-icon>{{ icon }}</v-icon>
    {{ content }}
  </v-btn>
</template>

<script>
export default {
  name: "outline-round-btn",

  props: {
    on: Object,
    icon: String,
    content: String,
  },
};
</script>
