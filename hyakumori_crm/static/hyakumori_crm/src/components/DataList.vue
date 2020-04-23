<template>
  <v-layout v-resize="onResize">
    <v-data-table
      class="pa-0"
      ref="dataTable"
      v-model="selected"
      :dense="dense"
      light
      :height="tableHeight"
      :fixed-header="true"
      :mobile-breakpoint="0"
      :item-key="itemKey"
      :multi-sort="multiSort"
      :loading="isLoading"
      :headers="dynamicHeaders"
      :items="data"
      :no-data-text="$t('tables.no_data')"
      :show-select="showSelect"
      :options.sync="innerOptions"
      :server-items-length="serverItemsLength"
      :footer-props="{
        itemsPerPageOptions: [25, 50, 100, 150],
        itemsPerPageText: $t('raw_text.rows_per_page'),
      }"
      @click:row="clickRow"
    >
      <template v-slot:header.options>
        <v-icon @click="viewMore">mdi-dots-vertical</v-icon>
      </template>

      <template v-if="tableRowIcon" v-slot:item.internal_id="{ item }">
        <div class="d-flex align-center justify-space-between">
          <v-icon class="icon-mode mr-4 f14 mt-1 mb-1" small>{{
            tableRowIcon
          }}</v-icon>
          <p class="mb-0">{{ item.internal_id }}</p>
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
  </v-layout>
</template>

<script>
import { selectAll } from "d3-selection";

const headerSelection = { value: "options", align: "center", sortable: false };

export default {
  name: "data-list",
  props: {
    mode: String,
    dense: { type: Boolean, default: true },
    isLoading: Boolean,
    showSelect: Boolean,
    data: Array,
    headers: Array,
    negotiationCols: Array,
    serverItemsLength: Number,
    options: Object,
    tableRowIcon: String,
    itemKey: {
      type: String,
      default: "id",
    },
    multiSort: {
      type: Boolean,
      default: false,
    },
    autoHeaders: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      selected: [],
      innerOptions: {},
      tableHeight: window.innerHeight,
    };
  },

  mounted() {
    this.changeSortIcon();
  },

  computed: {
    dynamicHeaders() {
      if (this.data && this.headers.length > 1 && this.autoHeaders) {
        const headers = [];
        // pass id to data but ignore it when mapping header value
        for (let i = 0; i < this.headers.length; i++) {
          const header = { ...this.headers[i] };
          header.value = Object.keys(this.data[0])[i + 1];
          headers.push(header);
        }
        headers.push(headerSelection);
        return headers;
      }
      return [...this.headers, headerSelection];
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
      window.scrollTo(0, 0);
    },

    isNegotiation(val) {
      return val === "negotiation";
    },

    viewMore() {
      // Add more column to the table
    },

    onResize() {
      this.tableHeight = window.innerHeight - 280;
    },
  },

  watch: {
    innerOptions: {
      handler() {
        this.$emit("update:options", this.innerOptions);
      },
    },

    selected(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.$emit("selectedRow", newVal);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
%text-overflow-shared {
  text-overflow: ellipsis;
  white-space: nowrap;
}

.v-data-table {
  padding: 10px;
  width: 100%;
  height: fit-content;
  overflow: hidden;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);

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
    td {
      text-align: center;
      @extend %text-overflow-shared;
      &:hover {
        cursor: pointer;
      }
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
