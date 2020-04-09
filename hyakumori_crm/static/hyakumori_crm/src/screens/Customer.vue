<template>
  <v-container fluid class="pa-7">
    <v-row>
      <v-col md="3">
        <search-card />
      </v-col>

      <v-col cols="12" md="9">
        <data-list
          :headers="headers"
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
          text: "Internal ID",
          value: "internal_id",
        },
        {
          text: "Fullname Kana",
          value: "fullname_kana",
        },
        {
          text: "Fullname Kanji",
          value: "fullname_kanji",
        },
        { text: "Postal Code", value: "postal_code" },
        { text: "Address", value: "address" },
        { text: "Telephone", value: "telephone" },
        { text: "Mobilephone", value: "mobilephone" },
        { text: "Representative", value: "representative" },
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
              address
              telephone
              mobilephone
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
