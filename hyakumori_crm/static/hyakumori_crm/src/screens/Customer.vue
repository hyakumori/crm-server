<template>
  <main-section class="customer">
    <template #top>
      <page-header>
        <template #bottom-right>
          <div>
            <v-menu offset-y nudge-bottom="4">
              <template v-slot:activator="{ on }">
                <outline-round-btn
                  icon="mdi-download"
                  :content="$t('buttons.csv_download')"
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
      <data-list
        ref="table"
        class="ml-7"
        itemKey="id"
        :headers="headers"
        :data="customers"
        showSelect
        :options.sync="options"
        :serverItemsLength="totalCustomers"
        :tableRowIcon="tableRowIcon"
        :autoHeaders="false"
        @rowData="rowData"
        :isLoading="$apollo.queries.customerList.loading"
      ></data-list>
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

export default {
  components: {
    MainSection,
    SearchCard,
    DataList,
    PageHeader,
    OutlineRoundBtn,
  },
  mixins: [ScreenMixin],
  data() {
    return {
      customerList: {},
      pageIcon: "mdi-account-outline",
      pageHeader: this.$t("page_header.customer_mgmt"),
      options: {},
      filter: null,
      tableRowIcon: this.$t("icon.customer_icon"),
      headers: [],
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
  methods: {
    downloadCsv(fileName, url) {
      const fileStream = streamSaver.createWriteStream(fileName);

      fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
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
      });
    },
    handleDownloadSelected() {
      const ids = Object.keys(this.$refs.table.$refs.dataTable.selection);
      const qStr = ids.map(id => `ids=${id}`).join("&");
      this.downloadCsv(
        "customers_filtered.csv",
        `${this.$rest.defaults.baseURL}/customers/download_csv?` + qStr,
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
        params: { id: val },
      });
    },
    onSearch() {
      this.filter = { ...this.filter, filters: this.requestFilters };
      this.$apollo.queries.customerList.refetch();
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
              internal_id
              fullname_kana
              fullname_kanji
              postal_code
              prefecture
              municipality
              address
              telephone
              mobilephone
              email
              status
              ranking
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
