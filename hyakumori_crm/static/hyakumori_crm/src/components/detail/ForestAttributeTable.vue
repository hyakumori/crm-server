<template>
  <v-data-table
    class="attribute-table"
    hide-default-footer
    disable-sort
    :items-per-page="12"
    :headers="getHeaders"
    :items="attributes"
  >
    <template v-slot:item.unit="{ item }">
      <h4 class="attribute-table__item-unit">{{ item.unit }}</h4>
    </template>

    <template v-slot:item.first_area="{ item }">
      <h4 class="attribute-table__item-forest">{{ item.first_area }}</h4>
    </template>

    <template v-slot:item.second_area="{ item }">
      <h4 class="attribute-table__item-forest">{{ item.second_area }}</h4>
    </template>

    <template v-slot:item.third_area="{ item }">
      <h4 class="attribute-table__item-forest">{{ item.third_area }}</h4>
    </template>
  </v-data-table>
</template>

<script>
import headers from "../../assets/dump/forest_attribute_header.json";

export default {
  name: "forest-attribute-table",

  props: {
    attributes: Array,
  },

  computed: {
    getHeaders() {
      return headers;
    },
  },
};
</script>

<style lang="scss" scoped>
$font-weight: 500;

.attribute-table ::v-deep {
  th {
    font-size: 14px;
    font-weight: bold;
    color: #444444 !important;
  }

  .attribute-table__item-area {
    font-size: 16px;
    color: #333333;
    font-weight: $font-weight;
  }

  .attribute-table__item-unit {
    font-size: 14px;
    color: #579513;
    font-weight: $font-weight;
  }

  .attribute-table__item-forest {
    font-size: 18px;
    color: #579513;
    font-weight: $font-weight;
  }
}
</style>
