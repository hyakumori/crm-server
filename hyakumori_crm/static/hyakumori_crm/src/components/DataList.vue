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
      fixed-header
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
      <template v-if="tableRowIcon" v-slot:[`item.${iconRowValue}`]="{ item }">
        <div class="d-flex align-center justify-center">
          <v-icon class="icon-mode f14 mt-1 mb-1" small>
            {{ tableRowIcon }}
          </v-icon>
          <p
            class="mb-0"
            :class="{
              'ml-4':
                item[iconRowValue] &&
                (!iconRowValueSlice.shouldSlice ||
                  (iconRowValueSlice.shouldSlice &&
                    iconRowValueSlice.length !== 0)),
            }"
          >
            {{
              item[iconRowValue]
                ? iconRowValueSlice.shouldSlice
                  ? item[iconRowValue].slice(0, iconRowValueSlice.length)
                  : item[iconRowValue]
                : ""
            }}
          </p>
        </div>
      </template>
      <template
        v-if="showSelect"
        v-slot:header.data-table-select="{ on, props }"
      >
        <v-simple-checkbox
          :ripple="false"
          v-bind="props"
          v-on="on"
        ></v-simple-checkbox>
      </template>
      <template
        v-if="showSelect"
        v-slot:item.data-table-select="{ isSelected, select }"
      >
        <v-simple-checkbox
          :ripple="false"
          :value="isSelected"
          @input="select($event)"
          class="datalist__checkbox"
        ></v-simple-checkbox>
      </template>
      <template v-slot:item.tags="{ item }" class="text-truncate">
        <template v-for="(tag, name, index) in item['tags']">
          <p class="tag" v-if="tag && name" :key="index">
            {{ `${name}: ${tag}` }}
          </p>
        </template>
      </template>

      <!--      TODO: need a way to inject this instead of writing customized logic here    -->
      <template v-slot:item.contract_status="{ item }" class="text-truncate">
        <v-chip
          v-if="item['contract_status']"
          small
          outlined
          :color="colorMaps[item['contract_status']]"
        >
          {{ item["contract_status"] }}
        </v-chip>
      </template>

      <template v-slot:item.fsc_status="{ item }" class="text-truncate">
        <v-chip
          v-if="item['fsc_status']"
          small
          outlined
          :color="colorMaps[item['fsc_status']]"
        >
          {{ item["fsc_status"] }}
        </v-chip>
      </template>
    </v-data-table>
  </v-layout>
</template>

<script>
import { throttle } from "lodash";

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
      isRowMouseDown: false,
      isRowDrag: false,
    };
  },

  computed: {
    colorMaps() {
      return {
        未契約: "grey--lighten",
        期限切: "orange lighten-2",
        契約済: "primary",
      };
    },
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
      return this.showSelect
        ? [
            { value: "data-table-select", width: 100, align: "center" },
            ...this.headers,
            headerSelection,
          ]
        : [...this.headers, headerSelection];
    },
  },
  created() {
    this.throttleRowMouseMoveHandler = throttle(this.rowMouseMoveHandler, 50);
  },

  methods: {
    rowMouseDownHandler() {
      this.isRowMouseDown = true;
    },
    rowMouseMoveHandler() {
      if (this.isRowMouseDown) {
        this.isRowDrag = true;
      } else this.isRowDrag = false;
    },
    rowMouseUpHandler() {
      this.isRowMouseDown = false;
    },
    registerMouseEventToRows() {
      const rows = this.$refs.dataTable.$el.querySelectorAll("table tbody tr");
      rows.forEach(row => {
        row.addEventListener("mousedown", this.rowMouseDownHandler);
        row.addEventListener("mousemove", this.throttleRowMouseMoveHandler);
        row.addEventListener("mouseup", this.rowMouseUpHandler);
      });
    },
    unregisterMouseEventToRows() {
      const rows = this.$refs.dataTable.$el.querySelectorAll("table tbody tr");
      rows.forEach(row => {
        row.removeEventListener("mousedown", this.rowMouseDownHandler);
        row.removeEventListener("mousemove", this.throttleRowMouseMoveHandler);
        row.removeEventListener("mouseup", this.rowMouseUpHandler);
      });
    },

    clickRow(value) {
      this.isRowMouseDown = false;
      if (this.isRowDrag) {
        this.isRowDrag = false;
        return;
      }
      this.$emit("rowData", value[this.itemKey]);
      this.$emit("rowDataItem", value);
      window.scrollTo(0, 0);
    },

    isNegotiation(val) {
      return val === "negotiation";
    },

    onResize() {
      // dirty work
      // search bar min-height 625
      // container padding top 28, bottom 12
      // page banner height 170
      // action bar height 56, margin bottom 16
      const innerHeight = window.innerHeight < 835 ? 835 : window.innerHeight;
      this.tableHeight =
        innerHeight - 270 <= 625 ? innerHeight : innerHeight - 270 - (56 + 16);
    },
  },
  beforeUpdate() {
    this.unregisterMouseEventToRows();
  },
  beforeDestroy() {
    this.unregisterMouseEventToRows();
  },
  updated() {
    this.registerMouseEventToRows();
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

%row-text-style {
  font-size: 12px;
  line-height: 10px;
  color: #444444;
  font-weight: normal;
}
.datalist__checkbox {
  // only work on chrome
  width: 100%;
  height: 100%;
  i {
    top: 50%;
    transform: translateY(-50%);
  }
}
.v-data-table {
  padding: 10px;
  width: 100%;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);

  & .icon-mode {
    padding: 10px;
    background: rgb(245, 245, 245);
    border-radius: 50%;
  }

  & .icon-mode:before {
    color: #aaaaaa;
  }

  & .tag {
    display: inline-block;
    background: #12c7a6;
    border-radius: 4px;
    color: white;
    margin: 0 2px;
    padding: 4px 6px !important;
  }

  & ::v-deep tr {
    td:first-child i:before {
      color: #aaaaaa;
    }
    td {
      @extend %row-text-style;
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
      @extend %text-overflow-shared;

      span {
        font-weight: bold;
        @extend %row-text-style;
      }

      & .mdi-chevron-up {
        position: absolute;
        right: 0;
      }
    }
    th:first-child i:before {
      color: #aaaaaa;
    }
    th:nth-child(2) {
      text-align: center !important;
    }
  }
  .v-input--selection-controls__ripple {
    border-radius: 0 !important;
  }
}
</style>
