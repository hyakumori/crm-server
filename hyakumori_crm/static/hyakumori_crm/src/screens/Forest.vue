<template>
  <v-row class="main-section pl-5 pt-2 pr-5">
    <v-col cols="3">
      <search-card />
    </v-col>

    <v-col cols="9">
      <div class="list-header d-flex align-center">
        <p class="ml-4 mb-0 font-weight-bold caption">４件を選択済み</p>
        <p class="ml-12 mb-0 caption">アクションを選択</p>
        <v-icon>mdi-chevron-down</v-icon>
      </div>

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
import headers from "../assets/dump_table_header.json";
import datas from "../assets/dump_table_data.json";

export default {
  name: "forest",

  components: {
    DataList,
    SearchCard
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

<style lang="scss" scoped>
.main-section {
  background-color: #dddddd;
}

.list-header {
  background: #f7eaa5;
  border-radius: 4px;
  height: 56px;

  & p {
    color: #825929;
  }

  & .v-icon {
    cursor: pointer;
  }
}
</style>
