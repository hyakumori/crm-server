<template>
  <v-row dense>
    <template v-for="(forest, index) in forests">
      <v-col cols="6" :key="index">
        <forest-info-card
          :card_id="forest.id"
          :forestId="forest.internal_id"
          :customerCount="forest.customers_count"
          :address="
            `${forest.cadastral.subsector} ${forest.cadastral.sector} ${forest.cadastral.municipality} ${forest.cadastral.prefecture}`
          "
          :isUpdate="isUpdate"
        />
      </v-col>
    </template>
  </v-row>
</template>

<script>
import ForestInfoCard from "./ForestInfoCard";

export default {
  name: "forest-info-list",

  components: {
    ForestInfoCard,
  },

  props: {
    forests: Array,
    isUpdate: Boolean,
  },
};
</script>
