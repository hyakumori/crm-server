<template>
  <v-row dense>
    <template v-for="(forest, index) in forests">
      <v-col cols="6" :key="index">
        <forest-info-card
          :forest="forest"
          :card_id="forest.id"
          :forestId="forest.internal_id"
          :customerCount="forest.customers_count"
          :address="
            `${forest.cadastral.prefecture} ${
              forest.cadastral.municipality
            } ${forest.cadastral.sector || ''} ${forest.cadastral.subsector ||
              ''}`
          "
          :isUpdate="isUpdate"
          :index="index"
          @deleteForest="$emit('deleteForest', forest, index)"
          @undoDeleteForest="$emit('undoDeleteForest', forest)"
          :added="forest.added"
          :deleted="forest.deleted"
          :selectedId="selectedId"
          @selected="(fId, inx) => $emit('selected', fId, inx)"
          :clickable="itemClickable"
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
    selectedId: String,
    itemClickable: { type: Boolean, default: false },
  },
};
</script>
