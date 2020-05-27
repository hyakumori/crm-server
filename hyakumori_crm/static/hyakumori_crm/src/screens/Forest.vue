<template>
  <main-section class="forest">
    <template #top>
      <page-header>
        <template #bottom-right>
          <div class="forest__csv-section">
            <outline-round-btn
              v-acl-only="[
                'admin',
                'group_admin',
                'group_normal_user',
                'manage_forest',
              ]"
              :content="$t('buttons.csv_upload')"
              icon="mdi-upload"
              :loading="uploadCsvLoading"
              @click="uploadCsv"
              class="mr-2"
              v-show="true"
            />
            <input
              v-acl-only="[
                'admin',
                'group_admin',
                'group_normal_user',
                'manage_forest',
              ]"
              @change="onCsvInputChange"
              accept=".csv"
              class="forest__csv-section__upload"
              ref="uploadCsv"
              type="file"
            />
            <v-menu
              nudge-bottom="4"
              offset-y
              v-acl-only="[
                'admin',
                'group_admin',
                'group_normal_user',
                'manage_forest',
              ]"
            >
              <template v-slot:activator="{ on }">
                <outline-round-btn
                  :content="$t('buttons.csv_download')"
                  :loading="downloadCsvLoading"
                  class="mr-2"
                  icon="mdi-download"
                  v-on="on"
                />
              </template>
              <v-list class="pa-0" dense>
                <v-list-item
                  @click="downloadSelectedRows"
                  v-if="tableSelectedRows && tableSelectedRows.length > 0"
                >
                  <v-list-item-title
                    >{{ $t("buttons.download_selected") }}
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="downloadAllCsv">
                  <v-list-item-title
                    >{{ $t("buttons.download_all") }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </page-header>
    </template>

    <template #section>
      <search-card
        :onSearch="onSearch"
        :searchCriteria="filterFields"
        ref="filter"
      />

      <div class="ml-7 forest__data-section">
        <table-action
          ref="actionRef"
          :actions="actions"
          :selectedCount="tableSelectedRows.length"
          @selected-action="selectedAction"
          class="mb-4"
          v-if="tableSelectedRows.length > 0"
        />

        <data-list
          :autoHeaders="false"
          :data="getData"
          :headers="getHeaders"
          :isLoading="$apollo.queries.forestsInfo.loading"
          :options.sync="options"
          :serverItemsLength="getTotalForests"
          :showSelect="true"
          :tableRowIcon="tableRowIcon"
          @rowData="rowData"
          @selectedRow="selectedRows"
          itemKey="id"
          mode="forest"
        ></data-list>
      </div>

      <snack-bar
        :isShow="isShowErr"
        :msg="errMsg"
        :timeout="sbTimeout"
        @dismiss="onDismissSb"
        color="error"
      />

      <update-actions-dialog
        :items="tagKeys"
        :isDisableUpdate="!selectedTagForUpdate"
        :updateData="updateTagForSelectedForests"
        :showDialog="showChangeTagDialog"
        :loadingItems="fetchTagsLoading"
        :updating="updatingTags"
        :cancel="resetActionChoices"
        @update-value="val => (newTagValue = val)"
        @selected-tag="val => (selectedTagForUpdate = val)"
        @toggle-show-dialog="val => (showChangeTagDialog = val)"
      />
    </template>
  </main-section>
</template>

<script>
import gql from "graphql-tag";
import DataList from "../components/DataList";
import SearchCard from "../components/SearchCard";
import GetForestList from "../graphql/GetForestList.gql";
import SnackBar from "../components/SnackBar";
import ScreenMixin from "./ScreenMixin";
import MainSection from "../components/MainSection";
import PageHeader from "../components/PageHeader";
import OutlineRoundBtn from "../components/OutlineRoundBtn";
import ErrorCard from "../components/ErrorsCard";
import { saveAs } from "file-saver";
import { get as _get } from "lodash";
import UpdateActionsDialog from "../components/dialogs/UpdateActionsDialog";
import TableAction from "../components/TableAction";

export default {
  name: "forest",

  mixins: [ScreenMixin],

  components: {
    DataList,
    SearchCard,
    TableAction,
    SnackBar,
    MainSection,
    PageHeader,
    OutlineRoundBtn,
    UpdateActionsDialog,
  },

  data() {
    return {
      actions: [
        {
          text: this.$t("action.contract_status_to_contracted"),
          value: 0,
        },
        {
          text: this.$t("action.contract_status_to_unsigned"),
          value: 1,
        },
        {
          text: this.$t("action.contract_status_to_expired"),
          value: 2,
        },
        {
          text: this.$t("action.change_tag_value"),
          value: 3,
        },
      ],
      pageIcon: this.$t("icon.forest_icon"),
      pageHeader: this.$t("page_header.forest_mgmt"),
      tableRowIcon: this.$t("icon.forest_icon"),
      searchCriteria: [],
      isShowErr: false,
      errMsg: null,
      sbTimeout: 5000,
      filter: {},
      options: {},
      headers: [],
      downloadCsvLoading: false,
      newTagValue: null,
      uploadCsvLoading: false,
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
  beforeRouteLeave(to, from, next) {
    if (this.uploadCsvLoading && !confirm(this.$t("messages.confirm_leave")))
      next(false);
    else next();
  },
  methods: {
    confirmReload(e) {
      e.returnValue = this.$t("messages.confirm_leave");
    },
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

    onSearch() {
      this.filter = { ...this.filter, page: 1, filters: this.requestFilters };
      this.options = { ...this.options, page: 1 };
      this.$apollo.queries.forestsInfo.refetch();
    },

    uploadCsv() {
      if (this.$refs.uploadCsv) {
        const confirmUpload = confirm(this.$t("messages.confirm_upload_csv"));
        if (!confirmUpload) return;
        this.$refs.uploadCsv.click();
      }
    },

    checkCsvExtension(filename) {
      const filenameSplitByDot = filename.split(".");
      const fileExtension = filenameSplitByDot[filenameSplitByDot.length - 1];
      return fileExtension === "csv";
    },

    async onCsvInputChange(e) {
      const file = e.target.files[0];
      if (file.type === "text/csv" && this.checkCsvExtension(file.name)) {
        const requestFile = new FormData();
        requestFile.append("file", file);
        try {
          this.uploadCsvLoading = true;
          window.addEventListener("beforeunload", this.confirmReload);
          await this.$rest.post("/forests/upload-csv", requestFile);
          this.$apollo.queries.forestsInfo.refetch();
          this.$dialog.notify.success(this.$t("messages.upload_successfully"));
        } catch (error) {
          if (
            error.response &&
            error.response.status < 500 &&
            error.response.data
          ) {
            this.$dialog.show(ErrorCard, {
              line: error.response.data.line,
              errors: error.response.data.errors,
            });
          }
        } finally {
          window.removeEventListener("beforeunload", this.confirmReload);
          this.uploadCsvLoading = false;
        }
      } else {
        this.$dialog.notify.error("Invalid file input", {
          timeout: 5000,
        });
      }
      this.$refs.uploadCsv.value = "";
    },

    async downloadAllCsv() {
      try {
        this.downloadCsvLoading = true;
        let csvData = await this.$rest.get("/forests/download-csv");
        const blob = new Blob([csvData], { type: "text/csv;charset=UTF-8" });
        saveAs(blob, "all-forests.csv");
      } catch (e) {
      } finally {
        this.downloadCsvLoading = false;
      }
    },

    async downloadSelectedRows() {
      try {
        this.downloadCsvLoading = true;
        let csvData = await this.$rest.post(
          "/forests/download-csv",
          this.selectedRowIds,
        );
        const blob = new Blob([csvData], { type: "text/csv;charset=UTF-8" });
        saveAs(blob, "selected_forests.csv");
      } catch (e) {
      } finally {
        this.downloadCsvLoading = false;
      }
    },

    renderCustomers(data, nameType) {
      const list = _get(data, "attributes.customer_cache.list", {});
      const itemCount = Object.keys(list).length;
      if (itemCount > 0) {
        const firstKeyAsId = Object.keys(list)[0];
        let results = _get(
          list[firstKeyAsId],
          `name_${nameType}.last_name`,
          "",
        );

        const firstName = _get(
          list[firstKeyAsId],
          `name_${nameType}.first_name`,
          "",
        );

        if (firstName && firstName.length > 0) {
          results += " " + firstName;
        }

        if (itemCount > 1) {
          results +=
            " " +
            this.$t(`tables.another_item_human_${nameType}`, {
              count: itemCount - 1,
            });
        }
        return results;
      }
      return "";
    },

    async updateTagForSelectedForests() {
      const params = {
        ids: this.selectedRowIds,
        key: this.selectedTagForUpdate,
        value: this.newTagValue,
      };
      try {
        this.updatingTags = true;
        await this.$rest.put("/forests/tags", params);
      } catch (e) {
        await this.$dialog.notify.error(e);
      } finally {
        this.updatingTags = false;
        this.showChangeTagDialog = false;
        this.selectedTagForUpdate = null;
        this.resetActionChoices();
        await this.$apollo.queries.forestsInfo.refetch();
      }
    },

    selectedAction(index) {
      switch (index) {
        case 0:
          // update forest contract
          break;
        case 1:
          // update forest contract
          break;
        case 2:
          // update forest contract
          break;
        case 3:
          this.showChangeTagDialog = true;
          this.fetchTagsLoading = true;
          this.getSelectedObject("/forests/ids");
          break;
        default:
          return;
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
          const contract = element.contracts;
          const tags = element.tags;

          return {
            id: element.id,
            internal_id: element.internal_id,
            cadastral__prefecture: fCadastral.prefecture,
            cadastral__municipality: fCadastral.municipality,
            cadastral__sector: fCadastral.sector,
            cadastral__subsector: fCadastral.subsector,
            owner__name_kanji: this.renderCustomers(element, "kanji"),
            owner__name_kana: this.renderCustomers(element, "kana"),
            contracts__0__status: contract[0].status,
            contracts__0__start_date: contract[0].start_date,
            contracts__0__end_date: contract[0].end_date,
            contracts__1__status: contract[1] && contract[1].status,
            contracts__1__start_date: contract[1] && contract[1].start_date,
            contracts__1__end_date: contract[1] && contract[1].end_date,
            contracts__2__status: contract[2] && contract[2].status,
            contracts__2__start_date: contract[2] && contract[2].start_date,
            contracts__2__end_date: contract[2] && contract[2].end_date,
            tags: tags,
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

  &__csv-section {
    &__upload {
      height: 1px;
      width: 1px;
      visibility: hidden;
    }
  }
}
</style>
