<template>
  <v-data-table
    item-key="internal_id"
    ref="dataTable"
    v-model="selected"
    :loading="isLoading"
    :headers="dynamicHeaders"
    :items="data"
    :show-select="showSelect"
    :options.sync="options"
    :server-items-length="serverItemsLength"
    :footer-props="{
      itemsPerPageOptions: [10, 20, 50, 100],
      itemsPerPageText: $t('raw_text.rows_per_page'),
    }"
    @click:row="clickRow"
  >
    <template v-slot:header.options>
      <v-icon @click="viewMore">mdi-dots-vertical</v-icon>
    </template>

    <template v-slot:item.internal_id="{ item }">
      <div class="d-flex align-center justify-space-between">
        <v-icon class="icon-mode mr-4" small>{{ iconMode }}</v-icon>

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
</template>

<script>
import { selectAll } from "d3";

export default {
  name: "data-list",
  props: {
    mode: String,
    isLoading: Boolean,
    showSelect: Boolean,
    data: Array,
    headers: Array,
    negotiationCols: Array,
    serverItemsLength: Number,
  },

  data() {
    return {
      selected: [],
      options: {},
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
          .classed("mdi-chevron-down", true)
          .classed("mdi-arrow-up", false);
      }
    },

    clickRow(value) {
      this.$emit("rowData", value.internal_id);
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

    // addOptionHeader(headers) {
    //   const optionHeader = {
    //     value: "options",
    //     align: "center",
    //     sortable: false,
    //   };
    //   headers.push(optionHeader);
    // },

    viewMore() {
      // Add more column to the table
    },
  },

  watch: {
    options: {
      handler() {
        this.$emit("optionsChange", this.options);
      },
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
