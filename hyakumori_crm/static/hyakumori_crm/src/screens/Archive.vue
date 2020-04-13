<template>
  <main-section #section>
    <search-card />

    <data-list class="ml-7"></data-list>
  </main-section>
</template>

<script>
import SearchCard from "../components/SearchCard";
import DataList from "../components/DataList";
import MainSection from "../components/MainSection";

export default {
  name: "archive",

  components: {
    SearchCard,
    DataList,
    MainSection,
  },
};
</script>
