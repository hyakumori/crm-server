<template>
  <div class="d-flex align-center table-action">
    <p class="ml-4 mb-0 table-action__text">
      {{ selectedCount }} {{ $t("search.selected_action") }}
    </p>

    <select-list
      class="ml-12 table-action__select"
      :actions="getActions"
      :placeHolder="$t('search.select_action')"
      @selectedAction="onSelected"
    />
  </div>
</template>

<script>
import actions from "../assets/dump/table_actions.json";
import SelectList from "./SelectList";

export default {
  name: "table-action",

  components: {
    SelectList,
  },

  props: {
    selectedCount: Number,
  },

  methods: {
    onSelected() {
      // console.log(val)
    },
  },

  computed: {
    getActions() {
      return actions;
    },
  },
};
</script>

<style lang="scss" scoped>
$action-list-color: #825929;

.table-action {
  background: #f7eaa5;
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

    .v-select__slot,
    .v-select__selections,
    .v-select__selection,
    input::placeholder {
      color: $action-list-color;
    }

    .mdi-chevron-down {
      color: $action-list-color !important;
      margin-top: 4px !important;
    }
  }
}
</style>
