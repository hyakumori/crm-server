<template>
  <div>
    <slot name="top">
      <page-header />
    </slot>

    <v-container fluid class="app-width d-flex px-7 pt-5">
      <slot name="section"></slot>
      <slot name="right"></slot>
    </v-container>
  </div>
</template>

<script>
import PageHeader from "./PageHeader";

export default {
  name: "main-section",
  components: { PageHeader },
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.app-width {
  width: $content-width;
  min-width: $content-width;
}
</style>
