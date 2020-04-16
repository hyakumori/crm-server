<template>
  <main-section class="customer">
    <template #section>
      <search-card
        :searchCriteria="filterFields"
        :onSearch="onSearch"
        ref="filter"
      />
      <data-list
        class="ml-7"
        :headers="headers"
        :multiSort="true"
        :data="customers"
        :showSelect="true"
        :options.sync="options"
        :serverItemsLength="totalCustomers"
        :tableRowIcon="tableRowIcon"
        :autoHeaders="false"
        :isLoading="$apollo.queries.result.loading"
      ></data-list>
    </template>
  </main-section>
</template>

<script>
import gql from "graphql-tag";
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import SearchCard from "../components/SearchCard";
import DataList from "../components/DataList";
import BusEvent from "../BusEvent";

export default {
  components: {
    MainSection,
    SearchCard,
    DataList,
  },
  mixins: [ScreenMixin],
  data() {
    return {
      result: {},
      pageIcon: "mdi-account-outline",
      pageHeader: this.$t("page_header.customer_info_list"),
      options: {},
      filter: null,
      tableRowIcon: this.$t("icon.customer_icon"),
      headers: [],
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
    filterFields() {
      return this.headers
        .map(h => ({ text: h.text, value: h.filter_name }))
        .filter(f => f.value !== undefined);
    },
  },
  methods: {
    onSearch() {
      this.filter = { ...this.filter, filters: this.$refs.filter.conditions };
      this.$apollo.queries.result.refetch();
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
          filters: this.$refs.filter.conditions,
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
        return !this.filter || this.headers.length === 0;
      },
    },
  },
};
</script>
