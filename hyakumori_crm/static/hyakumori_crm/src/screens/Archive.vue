<template>
  <main-section #section class="archives">
    <search-card :onSearch="() => {}" />
    <data-list class="archives__data-section" :headers="headers" />
  </main-section>
</template>

<script>
import SearchCard from "../components/SearchCard";
import MainSection from "../components/MainSection";
import DataList from "../components/DataList";
import ScreenMixin from "./ScreenMixin";
import archive_header from "../assets/dump/archive_header.json";

export default {
  name: "archive",

  mixins: [ScreenMixin],

  components: {
    SearchCard,
    MainSection,
    DataList,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      pageHeader: this.$t("page_header.archive_history"),
      tableRowIcon: this.$t("icon.archive_icon"),
    };
  },

  computed: {
    headers() {
      return archive_header;
    },
  },
};
</script>

<style lang="scss" scoped>
.archives {
  &__data-section {
    margin-left: 29px;
  }
}
</style>
