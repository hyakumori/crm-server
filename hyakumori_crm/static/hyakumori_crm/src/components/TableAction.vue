<template>
  <div class="d-flex align-center table-action">
    <p class="ml-4 mb-0 table-action__text">
      {{ selectedCount }} {{ $t("search.selected_action") }}
    </p>

    <select-list
      class="ml-12 table-action__select"
      :actions="actions"
      :placeHolder="$t('search.select_action')"
      @selectedAction="onSelected"
      hide-details
      v-if="selectedCount > 0"
    />
  </div>
</template>

<script>
import SelectList from "./SelectList";

export default {
  name: "table-action",

  components: {
    SelectList,
  },

  props: {
    selectedCount: Number,
    actions: Array,
  },

  methods: {
    onSelected(val) {
      this.$emit("selected-action", val);
    },
  },
};
</script>

<style lang="scss" scoped>
.table-action {
  background: #ffffff;
  border-radius: 4px;
  height: 56px;

  &__text {
    font-size: 14px;
    font-weight: bold;
  }

  &__select ::v-deep {
    margin-top: 0;
    height: 100%;
    top: 25%;
    flex: none;

    .mdi-chevron-down {
      margin-top: 4px !important;
    }
  }
}
</style>
