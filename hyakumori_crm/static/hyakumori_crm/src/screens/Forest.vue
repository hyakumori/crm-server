<template>
  <v-row class="px-7 pt-2">
    <v-col cols="3">
      <search-card />
    </v-col>

    <v-col cols="9">
      <table-action />

      <data-list
        class="mt-4"
        mode="forest"
        v-on:rowData="rowData"
        :headers="getHeaders"
        :data="getData"
        :showSelect="true"
        :negotiationCols="['status']"
        :serverItemsLength="getTotalForests"
      ></data-list>
    </v-col>
  </v-row>
</template>

<script>
import DataList from "../components/DataList";
import SearchCard from "../components/SearchCard";
import TableAction from "../components/TableAction";
import headers from "../assets/dump/table_header_forest.json";
import GetForestList from "../graphql/GetForestList.gql";

export default {
  name: "forest",

  components: {
    DataList,
    SearchCard,
    TableAction,
  },

  apollo: {
    forestsInfo: {
      query: GetForestList,
      update: data => data.list_forests,
    },
  },

  methods: {
    rowData() {
      // console.log(val);
    },
  },

  computed: {
    getHeaders() {
      return headers;
    },

    getData() {
      if (this.forestsInfo) {
        return this.forestsInfo.forests.map(element => {
          return {
            id: element.id,
            address: element.geo_data.address,
            ground: "",
            acreage: element.basic_info.acreage,
            status: element.basic_info.status,
            ownerName: `${element.owner.profile.first_name} ${element.owner.profile.last_name}`,
            customerId: element.customer.id,
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
  },
};
</script>
