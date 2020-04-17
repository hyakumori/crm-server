<template>
  <v-app>
    <page-header />
    <router-view></router-view>
  </v-app>
</template>

<script>
import PageHeader from "../components/PageHeader";

export default {
  components: {
    PageHeader,
  },
};
</script>
