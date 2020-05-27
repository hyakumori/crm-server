<template>
  <v-layout v-resize="onResize">
    <v-data-table
      class="pa-0"
      ref="dataTable"
      v-model="selected"
      disable-sort
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
        itemsPerPageOptions: [25, 50, 100, 250, 500, 1000],
        itemsPerPageText: $t('raw_text.rows_per_page'),
      }"
      @click:row="clickRow"
    >
      <!--   For now it has no function, so remove it temporary  -->
      <!--      <template v-slot:header.options>-->
      <!--        <v-icon @click="viewMore">mdi-dots-vertical</v-icon>-->
      <!--      </template>-->

      <template v-if="tableRowIcon" v-slot:[`item.${iconRowValue}`]="{ item }">
        <div class="d-flex align-center justify-space-between">
          <v-icon class="icon-mode mr-4 f14 mt-1 mb-1" small>
            {{ tableRowIcon }}
          </v-icon>
          <p class="mb-0">
            {{
              item[iconRowValue]
                ? (iconRowValueSlice.shouldSlice &&
                    item[iconRowValue].slice(0, iconRowValueSlice.length)) ||
                  item[iconRowValue]
                : ""
            }}
          </p>
        </div>
      </template>

      <template v-slot:item.tags="{ item }" class="text-truncate">
        <template v-for="(tag, name, index) in item['tags']">
          <p class="tag" v-if="tag && name" :key="index">
            {{ `${name}: ${tag}` }}
          </p>
        </template>
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
    tagCols: Array,
    serverItemsLength: Number,
    options: Object,
    tableRowIcon: String,
    iconRowValue: {
      type: String,
      default: "internal_id",
    },
    iconRowValueSlice: {
      type: Object,
      default: () => ({
        shouldSlice: true,
        length: 8,
      }),
    },
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
      this.$emit("rowData", value[this.itemKey]);
      this.$emit("rowDataItem", value);
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
    "options.page"(val) {
      this.innerOptions = { ...this.innerOptions, page: val };
    },

    innerOptions: {
      handler() {
        this.$emit("update:options", this.innerOptions);
      },
    },

    "innerOptions.page": {
      handler() {
        var table = this.$refs.dataTable;
        var wrapper = table.$el.querySelector("div.v-data-table__wrapper");
        this.$vuetify.goTo(table, { container: wrapper });
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

  & .tag {
    display: inline-block;
    background: #12c7a6;
    border-radius: 4px;
    color: white;
    margin: 0 2px;
    padding: 1px 4px !important;
    font-size: 12px;
  }

  & ::v-deep tr {
    td {
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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
    th:nth-child(2) {
      text-align: center !important;
    }
  }
}
</style>
