<template>
  <v-container fluid class="pa-7">
    <v-row>
      <v-col md="3">
        <search-card />
      </v-col>

      <v-col cols="12" md="9">
        <data-list
          :headers="headers"
          :autoHeaders="false"
          :multiSort="true"
          :data="customers"
          :showSelect="true"
          :options.sync="options"
          :serverItemsLength="totalCustomers"
          :tableRowIcon="tableRowIcon"
          :isLoading="$apollo.queries.result.loading"
        ></data-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import gql from "graphql-tag";
import ScreenMixin from "./ScreenMixin";
import SearchCard from "../components/SearchCard";
import DataList from "../components/DataList";
import BusEvent from "../BusEvent";

export default {
  components: {
    SearchCard,
    DataList,
  },
  mixins: [ScreenMixin],
  data() {
    return {
      result: {},
      pageIcon: "mdi-account-outline",
      pageHeader: this.$t("page_header.customer_list"),
      options: {},
      filter: null,
      tableRowIcon: this.$t("icon.customer_icon"),
      headers: [
        {
          text: this.$t("tables.headers.customerlist.internal_id"),
          value: "internal_id",
        },
        {
          text: this.$t("tables.headers.customerlist.fullname_kanji"),
          value: "fullname_kanji",
        },
        {
          text: this.$t("tables.headers.customerlist.fullname_kana"),
          value: "fullname_kana",
        },
        {
          text: this.$t("tables.headers.customerlist.postal_code"),
          value: "postal_code",
        },
        {
          text: this.$t("tables.headers.customerlist.address"),
          value: "address",
        },
        {
          text: this.$t("tables.headers.customerlist.prefecture"),
          value: "prefecture",
        },
        {
          text: this.$t("tables.headers.customerlist.municipality"),
          value: "municipality",
        },
        {
          text: this.$t("tables.headers.customerlist.ranking"),
          value: "ranking",
        },
        {
          text: this.$t("tables.headers.customerlist.status"),
          value: "status",
        },
        {
          text: this.$t("tables.headers.customerlist.telephone"),
          value: "telephone",
        },
        {
          text: this.$t("tables.headers.customerlist.mobilephone"),
          value: "mobilephone",
        },
        {
          text: this.$t("tables.headers.customerlist.email"),
          value: "email",
        },
        {
          text: this.$t("tables.headers.customerlist.representative"),
          value: "representative",
        },
      ],
    };
  },
  mounted() {
    BusEvent.$on("customersChanged", () => {
      this.$apollo.queries.result.refetch();
    });
  },
  computed: {
    customers() {
      return this.result.customers;
    },
    totalCustomers() {
      return this.result.total;
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
  apollo: {
    result: {
      query: gql`
        query ListCustomers($filter: TableCustomerFilterInput!) {
          list_customers(data: $filter) {
            ok
            items {
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
              representative
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
        return !this.filter;
      },
    },
  },
};
</script>
