<template>
  <main-section class="customer">
    <template #top>
      <page-header>
        <template #bottom-right>
          <div>
            <outline-round-btn
              v-acl-only="[
                'admin',
                'group_admin',
                'group_normal_user',
                'manage_customer',
              ]"
              icon="mdi-upload"
              :content="
                selectedFileName
                  ? `${selectedFileName}`
                  : $t('buttons.csv_upload')
              "
              class="mr-2"
              @click="handleUploadBtnClick"
              :loading="uploadCsvLoading"
            />
            <input
              v-acl-only="[
                'admin',
                'group_admin',
                'group_normal_user',
                'manage_customer',
              ]"
              ref="csvUploadInput"
              type="file"
              style="height:0;width:0;"
              accept=".csv"
              @change="handleFileChange"
            />
            <v-menu
              offset-y
              nudge-bottom="4"
              v-acl-only="[
                'admin',
                'group_admin',
                'group_normal_user',
                'manage_customer',
              ]"
            >
              <template v-slot:activator="{ on }">
                <outline-round-btn
                  icon="mdi-download"
                  :content="$t('buttons.csv_download')"
                  :loading="downloadCsvLoading"
                  class="mr-2"
                  v-on="on"
                />
              </template>
              <v-list dense class="pa-0">
                <v-list-item
                  v-if="$refs.table && $refs.table.selected.length > 0"
                  @click="handleDownloadSelected"
                >
                  <v-list-item-title>{{
                    $t("buttons.download_selected")
                  }}</v-list-item-title>
                </v-list-item>
                <v-list-item @click="handleDownloadAll">
                  <v-list-item-title>{{
                    $t("buttons.download_all")
                  }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <outline-round-btn
              :icon="$t('icon.add')"
              @click="$router.push({ name: 'customer-new' })"
              :content="$t('buttons.add_customer')"
            />
          </div>
        </template>
      </page-header>
    </template>

    <template #section>
      <search-card
        :searchCriteria="filterFields"
        :onSearch="onSearch"
        ref="filter"
      />
      <div class="ml-7 customer__data-section">
        <table-action
          ref="actionRef"
          :actions="actions"
          :selectedCount="tableSelectedRows.length"
          @selected-action="selectedAction"
          class="mb-4"
          v-if="tableSelectedRows.length > 0"
        />

        <data-list
          ref="table"
          itemKey="id"
          :headers="headers"
          :data="customers"
          showSelect
          :options.sync="options"
          :serverItemsLength="totalCustomers"
          :tableRowIcon="tableRowIcon"
          :icon-row-value-slice="{ shouldSlice: false }"
          iconRowValue="business_id"
          :autoHeaders="false"
          @rowDataItem="rowData"
          @selectedRow="selectedRows"
          :isLoading="$apollo.queries.customerList.loading"
        />
      </div>
      <update-actions-dialog
        :items="tagKeys"
        :isDisableUpdate="!selectedTagForUpdate"
        :showDialog="showChangeTagDialog"
        :loadingItems="fetchTagsLoading"
        :updating="updatingTags"
        :cancel="resetActionChoices"
        :updateData="updateTagForSelectedCustomers"
        @update-value="val => (newTagValue = val)"
        @selected-tag="val => (selectedTagForUpdate = val)"
        @toggle-show-dialog="val => (showChangeTagDialog = val)"
      />
    </template>
  </main-section>
</template>

<script>
import gql from "graphql-tag";
import MainSection from "../components/MainSection";
import PageHeader from "../components/PageHeader";
import ScreenMixin from "./ScreenMixin";
import SearchCard from "../components/SearchCard";
import OutlineRoundBtn from "../components/OutlineRoundBtn";
import DataList from "../components/DataList";
import BusEvent from "../BusEvent";
import streamSaver from "../plugins/streamsaver";
import UpdateActionsDialog from "../components/dialogs/UpdateActionsDialog";
import TableAction from "../components/TableAction";
import ErrorCard from "../components/ErrorsCard";

export default {
  components: {
    MainSection,
    SearchCard,
    DataList,
    PageHeader,
    OutlineRoundBtn,
    UpdateActionsDialog,
    TableAction,
  },
  mixins: [ScreenMixin],
  data() {
    return {
      actions: [
        {
          text: this.$t("action.change_tag_value"),
          value: 0,
        },
      ],
      customerList: {},
      pageIcon: "mdi-account-outline",
      pageHeader: this.$t("page_header.customer_mgmt"),
      options: {},
      filter: null,
      tableRowIcon: this.$t("icon.customer_icon"),
      headers: [],
      downloadCsvLoading: false,
      newTagValue: null,
      selectedFileName: "",
      uploadCsvLoading: false,
    };
  },
  mounted() {
    BusEvent.$on("customersChanged", () => {
      this.$apollo.queries.customerList.refetch();
    });
  },
  computed: {
    customers() {
      return this.customerList.customers;
    },
    totalCustomers() {
      return this.customerList.total;
    },
    filterFields() {
      return this.headers
        .map(h => ({ text: h.text, value: h.filter_name }))
        .filter(f => f.value !== undefined);
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
    async handleUploadBtnClick() {
      if (this.selectedFileName !== "") {
        const confirmUpload = confirm(this.$t("messages.confirm_upload_csv"));
        if (!confirmUpload) {
          this.$refs.csvUploadInput.value = null;
          this.selectedFileName = "";
          return;
        }
        this.uploadCsvLoading = true;
        window.addEventListener("beforeunload", this.confirmReload);
        const formData = new FormData();
        formData.append("file", this.$refs.csvUploadInput.files[0]);
        try {
          await this.$rest.post("/customers/upload_csv", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          this.$apollo.queries.customerList.refetch();
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
        }
        this.uploadCsvLoading = false;
        this.$refs.csvUploadInput.value = null;
        this.selectedFileName = "";
      } else {
        this.$refs.csvUploadInput.click();
      }
    },
    handleFileChange(e) {
      if (e.target.files[0]) this.selectedFileName = e.target.files[0].name;
      else this.selectedFileName = "";
    },
    downloadCsv(fileName, url, config = {}) {
      this.downloadCsvLoading = true;
      const fileStream = streamSaver.createWriteStream(fileName);

      fetch(url, {
        ...config,
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          ...(config.headers || {}),
        },
      }).then(res => {
        window.writer = fileStream.getWriter();

        const reader = res.body.getReader();
        const pump = () =>
          reader
            .read()
            .then(res =>
              res.done ? writer.close() : writer.write(res.value).then(pump),
            );

        pump();
        this.downloadCsvLoading = false;
      });
    },
    handleDownloadSelected() {
      const ids = Object.keys(this.$refs.table.$refs.dataTable.selection);
      this.downloadCsv(
        "customers_filtered.csv",
        `${this.$rest.defaults.baseURL}/customers/download_csv`,
        {
          method: "POST",
          body: JSON.stringify({ ids }),
          headers: { "Content-Type": "application/json" },
        },
      );
    },
    handleDownloadAll() {
      this.downloadCsv(
        "customers.csv",
        `${this.$rest.defaults.baseURL}/customers/download_csv`,
      );
    },
    rowData(val) {
      this.$router.push({
        name: "customer-detail",
        params: { id: val.business_id },
      });
    },
    onSearch() {
      this.filter = { ...this.filter, page: 1, filters: this.requestFilters };
      this.options = { ...this.options, page: 1 };
      this.$apollo.queries.customerList.refetch();
    },
    async updateTagForSelectedCustomers() {
      const params = {
        ids: this.selectedRowIds,
        key: this.selectedTagForUpdate,
        value: this.newTagValue,
      };
      try {
        this.updatingTags = true;
        await this.$rest.put("/customers/tags", params);
      } catch (e) {
        await this.$dialog.notify.error(e);
      } finally {
        this.updatingTags = false;
        this.showChangeTagDialog = false;
        this.selectedTagForUpdate = null;
        this.resetActionChoices();
        await this.$apollo.queries.customerList.refetch();
      }
    },
    selectedAction(index) {
      switch (index) {
        case 0:
          this.showChangeTagDialog = true;
          this.fetchTagsLoading = true;
          this.getSelectedObject("/customers/ids");
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
  apollo: {
    headers: {
      query: gql`
        query CustomerTableHeaders {
          customertable_headers {
            headers
          }
        }
      `,
      update(data) {
        return data.customertable_headers.headers;
      },
    },
    customerList: {
      query: gql`
        query ListCustomers($filter: TableCustomerFilterInput!) {
          list_customers(data: $filter) {
            ok
            items {
              id
              business_id
              fullname_kana
              fullname_kanji
              postal_code
              prefecture
              municipality
              sector
              telephone
              mobilephone
              email
              tags
            }
            total
          }
        }
      `,
      variables() {
        return {
          filter: this.filter,
        };
      },
      update: data => {
        return {
          customers: data.list_customers.items,
          total: data.list_customers.total,
        };
      },
      skip() {
        return !this.filter || this.headers.length === 0;
      },
    },
  },
};
</script>

<style lang="scss" scoped>
.customer {
  &__data-section {
    flex: 1;
    overflow: hidden;
  }
}
</style>
