<template>
  <v-container fluid class="pa-7">
    <v-row>
      <v-col md="3">
        <search-card
          :searchCriteria="getSearchCriteria"
          @onSearch="onSearch"
          @unableDelete="unableDelErr"
          @conditionOutOfBounds="conditionOutOfBoundsErr"
        />
      </v-col>
      <v-col cols="12" md="9">
        <table-action />

        <data-list
          class="mt-4"
          mode="forest"
          itemKey="internal_id"
          :headers="getHeaders"
          :data="getData"
          :showSelect="true"
          :isLoading="$apollo.queries.forestsInfo.loading"
          :serverItemsLength="getTotalForests"
          @rowData="rowData"
          :tableRowIcon="tableRowIcon"
          :options.sync="options"
        ></data-list>
      </v-col>
    </v-row>

    <snack-bar
      color="error"
      :isShow="isShowErr"
      :msg="errMsg"
      :timeout="sbTimeout"
      @dismiss="onDismissSb"
    />
  </v-container>
</template>

<script>
import DataList from "../components/DataList";
import SearchCard from "../components/SearchCard";
import TableAction from "../components/TableAction";
import headers from "../assets/dump/table_header_forest_jp.json";
import GetForestList from "../graphql/GetForestList.gql";
import SnackBar from "../components/SnackBar";
import ScreenMixin from "./ScreenMixin";

export default {
  name: "forest",

  mixins: [ScreenMixin],

  components: {
    DataList,
    SearchCard,
    TableAction,
    SnackBar,
  },

  data() {
    return {
      pageIcon: this.$t("icon.forest_icon"),
      pageHeader: this.$t("page_header.forest_list"),
      tableRowIcon: this.$t("icon.forest_icon"),
      searchCriteria: [],
      isShowErr: false,
      errMsg: null,
      sbTimeout: 5000,
      filter: {},
      options: {},
    };
  },

  apollo: {
    forestsInfo: {
      query: GetForestList,
      update: data => data.list_forests,
      variables() {
        return {
          filter: this.filter,
        };
      },
    },
  },

  methods: {
    rowData() {
      // console.log(val);
    },

    onSearch(err, data) {
      if (err) {
        this.isShowErr = true;
        this.errMsg = this.$t("search.duplicate_criteria_msg");
      } else {
        // Handling search data
      }
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
        };
      },
      deep: true,
    },
  },

  computed: {
    getHeaders() {
      return headers;
    },
    getData() {
      if (this.forestsInfo) {
        return this.forestsInfo.forests.map(element => {
          const fCadastral = element.cadastral;
          const owner = element.owner;
          const contract = element.contracts;
          const tag = element.tag;

          return {
            internal_id: element.internal_id,
            forestPrefecture: fCadastral.prefecture,
            forestMunicipality: fCadastral.municipality,
            forestSector: fCadastral.sector,
            forestSubsector: fCadastral.subsector,
            ownerKanji: owner.name_kana,
            ownerKana: owner.name_kanji,
            ownerPrefecture: owner.address.prefecture,
            ownerMunicipality: owner.address.municipality,
            ownerSector: owner.address.sector,
            contractLongTerm: contract[0].status,
            contractLongTermStart: contract[0].start_date,
            contractLongTermEnd: contract[0].end_date,
            contractWork: contract[1].status,
            contractWorkStart: contract[1].start_date,
            contractWorkEnd: contract[1].end_date,
            contractFsc: contract[2].status,
            contractFscStart: contract[2].start_date,
            contractFscEnd: contract[2].end_date,
            tagDanchi: tag.danchi,
            tagManageType: tag.manage_type,
            options: "",
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
  },
};
</script>

<style lang="scss" scoped>
.forest {
  &__data-section {
    overflow: hidden;
  }
}
</style>
