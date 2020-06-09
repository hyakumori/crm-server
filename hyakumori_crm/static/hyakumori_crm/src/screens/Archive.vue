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
      <search-card
        :onSearch="onSearchArchives"
        :search-criteria="headers"
        ref="searchRef"
      />
      <div class="archives__data-section">
        <table-action
          ref="actionRef"
          class="mb-4"
          v-if="tableSelectedRows.length > 0"
          :actions="actions"
          :selected-count="tableSelectedRows.length"
          @selected-action="selectedAction"
        />
        <data-list
          :auto-headers="false"
          :headers="headers"
          :is-loading="isLoading"
          :showSelect="true"
          :data="data"
          :tableRowIcon="pageIcon"
          :serverItemsLength="totalItems"
          @rowData="rowData"
          :options.sync="options"
          @update:options="paginationHandler"
          @selectedRow="val => (tableSelectedRows = val)"
          iconRowValue="id"
          :iconRowValueSlice="{ shouldSlice: false }"
        />
      </div>
      <update-actions-dialog
        :items="tagKeys"
        :show-dialog="showChangeTagDialog"
        :isDisableUpdate="!selectedTagForUpdate"
        :loadingItems="fetchTagsLoading"
        :updateData="updateTagForSelectedArchives"
        :cancel="resetActionChoices"
        :updating="updatingTags"
        @update-value="val => (newTagValue = val)"
        @selected-tag="val => (selectedTagForUpdate = val)"
        @toggle-show-dialog="val => (showChangeTagDialog = val)"
      />
    </template>
  </main-section>
</template>

<script>
import SearchCard from "../components/SearchCard";
import MainSection from "../components/MainSection";
import DataList from "../components/DataList";
import ScreenMixin from "./ScreenMixin";
import PageHeader from "../components/PageHeader";
import OutlineRoundBtn from "../components/OutlineRoundBtn";
import TableAction from "../components/TableAction";
import UpdateActionsDialog from "../components/dialogs/UpdateActionsDialog";
import { commonDatetimeFormat } from "../helpers/datetime";
import { get as _get } from "lodash";

export default {
  name: "archive",

  mixins: [ScreenMixin],

  components: {
    SearchCard,
    MainSection,
    DataList,
    PageHeader,
    OutlineRoundBtn,
    TableAction,
    UpdateActionsDialog,
  },

  data() {
    return {
      actions: [
        {
          text: this.$t("action.change_tag_value"),
          value: 0,
        },
      ],
      pageIcon: this.$t("icon.archive_icon"),
      pageHeader: this.$t("page_header.archive_detail"),
      tableRowIcon: this.$t("icon.archive_icon"),
      data: [],
      isLoading: false,
      totalItems: 0,
      next: null,
      previous: null,
      currentPage: 1,
      filterQueryString: "",
      options: {},
      headers: [],
      newTagValue: null,
    };
  },

  async created() {
    try {
      const response = await this.$rest.get("/archives/headers");
      if (response && response.data) {
        this.headers = [...response.data];
      }
    } catch {}
  },

  methods: {
    renderParticipants(data) {
      const list = _get(data, "attributes.customer_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "customer__name_kanji.last_name", "");
        results += " " + _get(list[0], "customer__name_kanji.first_name", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_human_kanji", {
              count: list.length - 1,
            });
        }
        return results;
      }
      return "";
    },

    renderUsers(data) {
      const list = _get(data, "attributes.user_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "full_name", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_human_kanji", {
              count: list.length - 1,
            });
        }
        return results;
      }
      return "";
    },

    renderForests(data) {
      const list = _get(data, "attributes.forest_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "forest__internal_id", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_thing", { count: list.length - 1 });
        }
        return results;
      }
      return "";
    },

    async onSearchArchives() {
      const searchData = this.$refs.searchRef.conditions;
      const filter = searchData.map(data => {
        let criteria = data.criteria;
        let keyword = data.keyword;
        if (criteria && criteria === "archive_date" && keyword) {
          const keywords = keyword.split(",");
          keyword = keywords.join(",");
        }
        return {
          criteria,
          keyword,
        };
      });
      this.filterQueryString = this.arrayToQueryString(filter);
      const api_url = `/archives?page_size=${this.options.itemsPerPage}&${this.filterQueryString}`;
      await this.fetchArchives(api_url);
      this.options = { ...this.options, page: 1 };
    },

    arrayToQueryString(filters) {
      let result = "";
      filters
        .filter(item => item.keyword && item.criteria)
        .forEach(item => (result += `${item.criteria}=${item.keyword}&`));
      return result;
    },

    async fetchArchives(api_url) {
      this.isLoading = true;
      const data = await this.$rest.get(api_url).then(res => res);
      this.totalItems = data.count;
      this.next = data.next;
      this.previous = data.previous;
      this.isLoading = false;
      this.data = data.results.map(data => ({
        id: data.id,
        archive_date: commonDatetimeFormat(data.archive_date),
        title: data.title,
        content: data.content,
        author: data.author_name,
        their_participants: this.renderParticipants(data),
        our_participants: this.renderUsers(data),
        associated_forest: this.renderForests(data),
        tags: data.tags,
      }));
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
        const api_url = `/archives?page_size=${val.itemsPerPage}&${this.filterQueryString}`;
        this.fetchArchives(api_url);
      }
    },

    async updateTagForSelectedArchives() {
      const params = {
        ids: this.selectedRowIds,
        key: this.selectedTagForUpdate,
        value: this.newTagValue,
      };
      try {
        this.updatingTags = true;
        await this.$rest.put("/archives/ids/tags", params);
      } catch (e) {
        await this.$dialog.notify.error(e);
      } finally {
        const api_url = `/archives?page_size=${this.options.itemsPerPage}&${this.filterQueryString}`;
        this.updatingTags = false;
        this.showChangeTagDialog = false;
        this.selectedTagForUpdate = null;
        this.resetActionChoices();
        await this.fetchArchives(api_url);
      }
    },

    selectedAction(index) {
      switch (index) {
        case 0:
          this.showChangeTagDialog = true;
          this.fetchTagsLoading = true;
          this.getSelectedObject("/archives/ids");
          break;
        default:
          return;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.archives {
  &__data-section {
    flex: 1;
    margin-left: 29px;
    overflow: hidden;
  }
}
</style>
