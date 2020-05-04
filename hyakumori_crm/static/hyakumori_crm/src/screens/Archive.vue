<template>
  <main-section class="archives">
    <template #top>
      <page-header>
        <template #bottom-right>
          <outline-round-btn
            :content="$t('buttons.add_archive')"
            :icon="$t('icon.add')"
            @click="$router.push({ name: 'archive-new' })"
          />
        </template>
      </page-header>
    </template>
    <template #section class="archives">
      <search-card :onSearch="fetchArchives" :search-criteria="headers" />
      <data-list
        :auto-headers="false"
        :data="data"
        :headers="headers"
        :is-loading="isLoading"
        :showSelect="true"
        :tableRowIcon="pageIcon"
        :serverItemsLength="totalItems"
        @rowData="rowData"
        @update:options="paginationHandler"
        class="archives__data-section"
        iconRowValue="id"
      />
    </template>
  </main-section>
</template>

<script>
import SearchCard from "../components/SearchCard";
import MainSection from "../components/MainSection";
import DataList from "../components/DataList";
import ScreenMixin from "./ScreenMixin";
import archive_header from "../assets/dump/archive_header.json";
import PageHeader from "../components/PageHeader";
import OutlineRoundBtn from "../components/OutlineRoundBtn";
import { commonDatetimeFormat } from "../helpers/datetime";

export default {
  name: "archive",

  mixins: [ScreenMixin],

  components: {
    SearchCard,
    MainSection,
    DataList,
    PageHeader,
    OutlineRoundBtn,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      pageHeader: this.$t("page_header.archive_detail"),
      tableRowIcon: this.$t("icon.archive_icon"),
      data: [],
      isLoading: false,
      totalItems: 0,
      next: null,
      previous: null,
      currentPage: 1,
    };
  },

  methods: {
    async fetchArchives(api_url) {
      this.isLoading = true;
      const data = await this.$rest
        .get(api_url)
        .then(res => res);
      this.totalItems = data.count;
      this.next = data.next;
      this.previous = data.previous;
      this.data = data.results.map(data => {
        this.isLoading = false;
        return {
          id: data.id,
          archive_date: commonDatetimeFormat(data.archive_date),
          title: data.title,
          content: data.content,
          their_participants: "",
          our_participants: "",
          associated_forest: "",
        };
      });
    },

    rowData(val) {
      this.$router.push(`/archives/${val}`);
    },

    paginationHandler(val) {
      if (val.page > this.currentPage) {
        this.currentPage = val.page;
        this.fetchArchives(this.next);
      } else if (val.page < this.currentPage) {
        this.currentPage = val.page;
        this.fetchArchives(this.previous);
      } else {
        const api_url = `/archives?page_size=${val.itemsPerPage}`;
        this.fetchArchives(api_url);
      }
    },
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
