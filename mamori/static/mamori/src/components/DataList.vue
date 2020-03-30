<template>
  <v-data-table
    item-key="id"
    ref="dataTable"
    v-model="selected"
    :headers="headers"
    :items="datas"
    :loading="isLoading"
    :sort-by="['id']"
    :sort-desc="[true]"
    :show-select="showSelect"
    @click:row="clickRow"
  >
    <template v-slot:header.options>
      <v-icon>mdi-dots-vertical</v-icon>
    </template>

    <template v-slot:item.id="{ item }">
      <div class="d-flex align-center justify-space-between">
        <v-icon class="icon-mode mr-2" small>{{ iconMode }}</v-icon>

        <p class="mb-0">{{ item.id }}</p>
      </div>
    </template>

    <template v-slot:item.owners="{ item }">
      <p class="owner-negotiation" v-if="isOwnerNegotiation(item.owners)">商談中</p>
      <p class="d-inline" v-else>{{ item.owners }}</p>
    </template>
  </v-data-table>
</template>

<script>
import { selectAll } from "d3";

export default {
  name: "data-list",
  props: {
    mode: String,
    showSelect: Boolean,
    datas: Array,
    headers: Array
  },

  data() {
    return {
      selected: []
    };
  },

  mounted() {
    this.changeSortIcon();
    this.createDynamicHeaderValue();
  },

  computed: {
    iconMode() {
      return this.isForestMode
        ? "mdi-image-filter-hdr"
        : this.isClientMode
        ? "mdi-account"
        : "mdi-book-account";
    },

    isLoading() {
      return !this.datas;
    }
  },

  methods: {
    changeSortIcon() {
      if (this.$refs.dataTable) {
        selectAll("i.mdi-arrow-up")
          .classed("mdi-chevron-up", true)
          .classed("mdi-arrow-up", false);
      }
    },

    createDynamicHeaderValue() {
      if (this.datas && this.headers) {
        for (let i = 0; i < this.headers.length; i++) {
          const element = this.headers[i];
          element.value = Object.keys(this.datas[0])[i];
        }
      }
    },

    clickRow(value) {
      this.$emit("rowData", value.id);
    },

    isForestMode() {
      return this.mode === "forest";
    },

    isClientMode() {
      return this.mode === "client";
    },

    isOwnerNegotiation(val) {
      return val === "negotiation";
    }
  }
};
</script>

<style lang="scss" scoped>
%text-overflow-shared {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.v-data-table {
  padding: 10px;

  & .icon-mode {
    padding: 10px;
    background: rgb(245, 245, 245);
    border-radius: 50%;
  }

  & .owner-negotiation {
    display: inline;
    padding: 5px;
    background: #ffa726;
    border-radius: 2px;
    color: white;
  }

  & tr:hover {
    cursor: pointer;
  }

  & tr p {
    @extend %text-overflow-shared;
  }

  & th {
    position: relative;
    @extend %text-overflow-shared;

    & .mdi-chevron-up {
      position: absolute;
      right: 0;
    }
  }
}
</style>
