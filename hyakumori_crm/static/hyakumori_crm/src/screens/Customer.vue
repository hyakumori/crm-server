<template>
  <v-row class="px-7 pt-2">
    <v-col cols="3">
      <search-card />
    </v-col>

    <v-col cols="9">
      <v-data-table
        :headers="headers"
        :multi-sort="true"
        :items="customers"
        :options.sync="options"
        :server-items-length="totalCustomers"
        :loading="$apollo.queries.result.loading"
        class="elevation-1"
      ></v-data-table>
    </v-col>
  </v-row>
</template>

<script>
import ScreenMixin from "./ScreenMixin";
import SearchCard from "../components/SearchCard";
import gql from "graphql-tag";

export default {
  components: {
    SearchCard,
  },
  mixins: [ScreenMixin],
  data() {
    return {
      result: {},
      pageIcon: "mdi-account-outline",
      pageHeader: this.$t("page_header.customer_list"),
      options: {},
      filter: null,
      headers: [
        {
          text: "Fullname",
          value: "fullname",
        },
        { text: "Address", value: "address" },
        { text: "Phone", value: "phone" },
        { text: "Representative", value: "representative" },
      ],
    };
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
              fullname
              address
              phone
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
