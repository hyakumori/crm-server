<template>
  <v-container fluid class="app-width d-flex px-7 pt-5">
    <slot name="section"></slot>
    <slot name="right"></slot>
  </v-container>
</template>

<script>
export default {
  name: "main-section",
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.app-width {
  width: $content-width;
  min-width: $content-width;
}
</style>
