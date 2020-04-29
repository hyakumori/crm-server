<template>
  <v-card
    :color="selected ? '#f5f5f5' : undefined"
    class="forest-info-card d-flex d-hover"
    :class="{ flat: flat, deleted: deleted, added: added }"
    outlined
    :ripple="mode != 'view'"
    @click="$emit('selected', card_id, index)"
  >
    <v-icon class="forest-info-card__icon">{{ $t("icon.forest_icon") }}</v-icon>

    <div class="forest-info-card__name d-flex ml-4 flex-column">
      <div v-if="forestId" class="d-flex justify-space-between">
        <h4 class="body-2">
          {{ forestId }}
          <span class="caption">{{ customerCount }} 人の所有者</span>
        </h4>
      </div>

      <div v-if="address" class="text-truncate">
        <v-icon small>mdi-map-marker</v-icon>
        <span class="ml-1 caption">{{ address }}</span>
      </div>
    </div>
    <v-btn
      v-if="deleted"
      class="align-self-center"
      icon
      @click.stop="$emit('undoDeleteForest')"
    >
      <v-icon>mdi-undo</v-icon>
    </v-btn>
    <router-link
      v-if="showAction && !deleted"
      :to="{ name: 'forest-detail', params: { id: card_id } }"
      v-slot="{ href }"
    >
      <v-btn
        class="align-self-center"
        icon
        @click.stop="isUpdate ? $emit('deleteForest') : undefined"
        :href="isUpdate ? null : href"
      >
        <v-icon>{{ actionIcon }}</v-icon>
      </v-btn>
    </router-link>
  </v-card>
</template>

<script>
export default {
  name: "forest-info-card",

  props: {
    card_id: String,
    forestId: String,
    customerCount: Number,
    address: String,
    isUpdate: Boolean,
    showAction: { type: Boolean, default: true },
    flat: { type: Boolean, default: false },
    deleted: { type: Boolean, default: false },
    added: { type: Boolean, default: false },
    selectedId: String,
    index: Number,
    mode: { type: String, default: "view" },
    handleDeleteClick: Function,
  },
  computed: {
    actionIcon() {
      return this.isUpdate ? "mdi-close" : "mdi-chevron-right";
    },
    selected() {
      return this.selectedId === this.card_id;
    },
  },
};
</script>

<style lang="scss" scoped>
$border-radius: 8px;
$background-color: #f5f5f5;

.forest-info-card::before {
  border-radius: $border-radius;
}

.forest-info-card.flat {
  border: none !important;
  border-radius: 0 !important;
  border-bottom: 1px solid #e1e1e1 !important;
}

.forest-info-card.deleted {
  border: 1px solid #ff5252 !important;
}

.forest-info-card.added {
  border: 1px solid #12c7a6 !important;
}

.forest-info-card {
  width: 100%;
  height: 80px;
  padding: 10px;
  border-radius: $border-radius !important;
  border: 1px solid #e1e1e1 !important;
  position: relative;

  &:focus::before {
    opacity: 0 !important;
  }

  &__icon {
    padding: 10px;
    background-color: $background-color;
    align-self: center;
    border-radius: 50% !important;
  }

  &__name {
    width: 100%;
    max-width: 234px;
    align-self: center;

    span {
      color: #999999;
    }
  }

  &__tag {
    position: absolute;
    right: 0;
    top: 0;
    height: 30px;
    width: 30px;
    border-radius: unset !important;
    border-top-right-radius: $border-radius !important;
    clip-path: polygon(0 0, 100% 100%, 100% 0);
  }

  & .owner {
    background-color: #12c7a6;
  }

  & .contactor {
    background-color: #f36c69;
  }

  &__related-info {
    background-color: $background-color;
    padding: 4px;
    width: fit-content;
    border-radius: 2px;
  }

  &__select-relationship ::v-deep {
    width: 220px;

    fieldset {
      border: 1px solid #eeeeee;
      border-radius: 4px;
    }

    .v-icon {
      margin-top: 0 !important;
    }

    .v-select__selection {
      color: #999999;
    }
  }
}
</style>
