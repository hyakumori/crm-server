<template>
  <main-section>
    <template #section> archive id: {{ $route.params.id }} </template>
    <template #right></template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";

export default {
  name: "archive-detail",

  components: {
    MainSection,
  },
};
</script>
