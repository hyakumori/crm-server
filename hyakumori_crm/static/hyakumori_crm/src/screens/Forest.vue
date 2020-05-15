<template>
  <main-section class="forest">
    <template #section>
      <search-card
        :searchCriteria="filterFields"
        :onSearch="onSearch"
        ref="filter"
      />

      <div class="ml-7 forest__data-section">
        <!--   For now it has no function, so remove it temporary  -->
        <!--        <table-action-->
        <!--          class="forest__data-section__table-action mb-4"-->
        <!--          v-if="tableSelectedRow.length > 0"-->
        <!--          :selectedCount="tableSelectedRow.length"-->
        <!--        />-->

        <data-list
          mode="forest"
          itemKey="id"
          :headers="getHeaders"
          :data="getData"
          :showSelect="true"
          :isLoading="$apollo.queries.forestsInfo.loading"
          :serverItemsLength="getTotalForests"
          :tableRowIcon="tableRowIcon"
          :options.sync="options"
          @rowData="rowData"
          @selectedRow="selectedRow"
          :autoHeaders="false"
        ></data-list>
      </div>

      <snack-bar
        color="error"
        :isShow="isShowErr"
        :msg="errMsg"
        :timeout="sbTimeout"
        @dismiss="onDismissSb"
      />
    </template>
  </main-section>
</template>

<script>
import gql from "graphql-tag";
import DataList from "../components/DataList";
import SearchCard from "../components/SearchCard";
import TableAction from "../components/TableAction";
import GetForestList from "../graphql/GetForestList.gql";
import SnackBar from "../components/SnackBar";
import ScreenMixin from "./ScreenMixin";
import MainSection from "../components/MainSection";

export default {
  name: "forest",

  mixins: [ScreenMixin],

  components: {
    DataList,
    SearchCard,
    // TableAction,
    SnackBar,
    MainSection,
  },

  data() {
    return {
      pageIcon: this.$t("icon.forest_icon"),
      pageHeader: this.$t("page_header.forest_mgmt"),
      tableRowIcon: this.$t("icon.forest_icon"),
      searchCriteria: [],
      isShowErr: false,
      errMsg: null,
      sbTimeout: 5000,
      filter: {},
      options: {},
      tableSelectedRow: [],
      headers: [],
    };
  },

  apollo: {
    headers: {
      query: gql`
        query ForestTableHeaders {
          foresttable_headers {
            headers
          }
        }
      `,
      update(data) {
        return data.foresttable_headers.headers;
      },
    },
    forestsInfo: {
      query: GetForestList,
      update: data => data.list_forests,
      variables() {
        return {
          filter: this.filter,
        };
      },
      skip() {
        return !this.filter || this.headers.length === 0;
      },
    },
  },

  methods: {
    rowData(val) {
      this.$router.push(`forests/${val}`);
    },

    onDismissSb(val) {
      this.isShowErr = val;
    },

    unableDelErr(err) {
      if (err) {
        this.isShowErr = true;
        this.errMsg = this.$t("search.unable_to_remove_search_msg");
      }
    },

    conditionOutOfBoundsErr(err) {
      if (err) {
        this.isShowErr = true;
        this.errMsg = this.$t("search.condition_is_maximum");
      }
    },

    selectedRow(val) {
      this.tableSelectedRow = val;
    },

    onSearch() {
      this.filter = { ...this.filter, filters: this.requestFilters };
      this.$apollo.queries.forestsInfo.refetch();
    },
  },

  watch: {
    options: {
      handler(val, old) {
        const { sortBy, sortDesc, page, itemsPerPage } = val;
        this.filter = {
          sortBy,
          sortDesc,
          page,
          itemsPerPage,
          preItemsPerPage: old.itemsPerPage || null,
          filters: this.requestFilters,
        };
      },
      deep: true,
    },
  },

  computed: {
    getHeaders() {
      return this.headers;
    },

    getData() {
      if (this.forestsInfo) {
        return this.forestsInfo.forests.map(element => {
          const fCadastral = element.cadastral;
          const owner = element.owner;
          const contract = element.contracts;
          const tags = element.tags;

          return {
            id: element.id,
            internal_id: element.internal_id,
            cadastral__prefecture: fCadastral.prefecture,
            cadastral__municipality: fCadastral.municipality,
            cadastral__sector: fCadastral.sector,
            cadastral__subsector: fCadastral.subsector,
            owner__name_kanji: owner.name_kanji,
            owner__name_kana: owner.name_kana,
            contracts__0__status: contract[0].status,
            contracts__0__start_date: contract[0].start_date,
            contracts__0__end_date: contract[0].end_date,
            contracts__1__status: contract[1].status,
            contracts__1__start_date: contract[1].start_date,
            contracts__1__end_date: contract[1].end_date,
            contracts__2__status: contract[2].status,
            contracts__2__start_date: contract[2].start_date,
            contracts__2__end_date: contract[2].end_date,
            tags__danchi: tags["団地"],
            tags__manage_type: tags["管理形態"],
          };
        });
      } else {
        return this.forestsInfo;
      }
    },

    getTotalForests() {
      if (this.forestsInfo) {
        return this.forestsInfo.total;
      } else {
        return 0;
      }
    },

    getSearchCriteria() {
      return Array.from(this.getHeaders).map(header => header.text);
    },

    filterFields() {
      return this.headers
        .map(h => ({ text: h.text, value: h.filter_name }))
        .filter(f => f.value !== undefined);
    },
  },
};
</script>

<style lang="scss" scoped>
.forest {
  &__data-section {
    flex: 1;
    overflow: hidden;
  }
}
</style>
