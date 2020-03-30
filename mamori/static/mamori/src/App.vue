<template>
  <v-app>
    <page-header />
    <router-view></router-view>
  </v-app>
</template>

<script>
import PageHeader from "./components/PageHeader";

export default {
  name: "App",

  components: {
    PageHeader
  }
};
</script>
