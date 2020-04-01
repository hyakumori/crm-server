<template>
  <v-row class="px-7 pt-2">
    <v-col cols="3">
      <search-card />
    </v-col>

    <v-col cols="9">
      <table-action />

      <data-list
        class="mt-4"
        mode="client"
        v-on:rowData="rowData"
        :headers="getHeaders"
        :datas="getDatas"
        :showSelect="true"
      ></data-list>
    </v-col>
  </v-row>
</template>

<script>
import DataList from "../components/DataList";
import SearchCard from "../components/SearchCard";
import TableAction from "../components/TableAction";
import headers from "../assets/dump/table_header_forest.json";
import datas from "../assets/dump/table_data_forest.json";

export default {
  name: "forest",

  components: {
    DataList,
    SearchCard,
    TableAction
  },

  methods: {
    rowData() {
      // console.log(val);
    }
  },

  computed: {
    getHeaders() {
      return headers;
    },

    getDatas() {
      return datas;
    }
  }
};
</script>
