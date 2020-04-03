<template>
  <v-data-table
    item-key="id"
    ref="dataTable"
    v-model="selected"
    :headers="dynamicHeaders"
    :items="data"
    :loading="isLoading"
    :sort-by="['id']"
    :sort-desc="[true]"
    :show-select="showSelect"
    :server-items-length="serverItemsLength"
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

    <template
      v-for="(nego, index) in negotiationCols"
      v-slot:[`item.${nego}`]="{ item }"
    >
      <p class="negotiation" v-if="isNegotiation(item[nego])" :key="index">
        {{ $t("raw_text.in_negotiation") }}
      </p>
      <p class="d-inline" v-else :key="index">{{ item[nego] }}</p>
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
    data: Array,
    headers: Array,
    negotiationCols: Array,
    serverItemsLength: Number,
  },

  data() {
    return {
      selected: [],
    };
  },

  mounted() {
    this.changeSortIcon();
  },

  computed: {
    iconMode() {
      if (this.isForestMode) {
        return this.$t("icon.forest_icon");
      } else if (this.isCustomerMode) {
        return this.$t("icon.customer_icon");
      } else {
        return this.$t("icon.archive_icon");
      }
    },

    isLoading() {
      return !this.data;
    },

    dynamicHeaders() {
      if (this.data && this.headers) {
        for (let i = 0; i < this.headers.length; i++) {
          const element = this.headers[i];
          element.value = Object.keys(this.data[0])[i];
        }
      }
      return this.headers;
    },
  },

  methods: {
    changeSortIcon() {
      if (this.$refs.dataTable) {
        selectAll("i.mdi-arrow-up")
          .classed("mdi-chevron-up", true)
          .classed("mdi-arrow-up", false);
      }
    },

    clickRow(value) {
      this.$emit("rowData", value.id);
    },

    isForestMode() {
      return this.mode === "forest";
    },

    isCustomerMode() {
      return this.mode === "customer";
    },

    isNegotiation(val) {
      return val === "negotiation";
    },
  },
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

  & .negotiation {
    display: inline;
    padding: 5px;
    background: #ffa726;
    border-radius: 2px;
    color: white;
  }

  & ::v-deep tr {
    cursor: pointer;

    td {
      text-align: center;
      @extend %text-overflow-shared;
    }

    th {
      position: relative;
      @extend %text-overflow-shared;

      & .mdi-chevron-up {
        position: absolute;
        right: 0;
      }
    }
  }
}
</style>
