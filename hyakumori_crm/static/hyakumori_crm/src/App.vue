<template>
  <v-app id="app" fullheight>
    <page-header />
    <router-view class="main-content"></router-view>
  </v-app>
</template>

<script>
import PageHeader from "./components/PageHeader";

export default {
  name: "App",

  components: {
    PageHeader,
  },
};
</script>

<style lang="scss">
html {
  overflow: auto !important;
}

#app {
  height: 100%;
  background-color: #dddddd;
}
</style>
