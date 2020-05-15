<template>
  <v-card
    class="participant-card d-hover"
    outlined
    :ripple="!showAction"
    :color="selected ? '#dddddd' : undefined"
    :class="{
      flat: flat,
      deleted: deleted,
      added: added,
      'show-pointer': showPointer,
    }"
    @click="$emit('selected', card_id, index)"
  >
    <v-card-title class="participant-card__title pa-0">{{
      isAuthor ? "作成者" : ""
    }}</v-card-title>
    <div class="participant-card__person text-truncate">
      <v-icon class="participant-card__person__icon" size="24">{{
        $t("icon.customer_icon")
      }}</v-icon>
      <span class="ml-3">{{ name }}</span>
    </div>
    <v-spacer></v-spacer>
    <v-btn
      class="align-self-center mr-2"
      v-if="isUpdate && !deleted"
      icon
      @click="$emit('deleteParticipant')"
    >
      <v-icon size="24">mdi-close</v-icon>
    </v-btn>
    <v-btn
      class="align-self-center mr-2"
      v-if="deleted"
      icon
      @click.stop="$emit('undoDeletedParticipant')"
    >
      <v-icon size="24">mdi-undo</v-icon>
    </v-btn>
    <v-btn
      class="align-self-center mr-2"
      v-if="!isUpdate && !deleted && !added && hasPermission"
      icon
      @click="onNavigation"
    >
      <v-icon size="24" v-show="showAction">mdi-chevron-right</v-icon>
    </v-btn>
  </v-card>
</template>

<script>
import { hasScope } from "../../helpers/security";

export default {
  name: "archive-participant-card",

  props: {
    isAuthor: { type: Boolean, default: false },
    name: String,
    card_id: String,
    selectedId: String,
    isUpdate: Boolean,
    showAction: { type: Boolean, default: true },
    flat: { type: Boolean, default: false },
    deleted: { type: Boolean, default: false },
    added: { type: Boolean, default: false },
    index: Number,
    showPointer: { type: Boolean, default: false },
  },

  methods: {
    onNavigation() {
      this.$router.push(`/users/${this.card_id}`);
    },
  },

  computed: {
    selected() {
      return this.selectedId === this.card_id;
    },
    hasPermission() {
      return hasScope("admin") || hasScope("group_admin");
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../../styles/variables";

.participant-card.flat {
  border: none !important;
  border-radius: 0 !important;
  border-bottom: 1px solid #e1e1e1 !important;
}

.participant-card.deleted {
  border: 1px solid #ff5252 !important;
}

.participant-card.added {
  border: 1px solid #12c7a6 !important;
}

.participant-card:hover {
  cursor: default;
}

.participant-card.show-pointer:hover {
  cursor: pointer;
}

.participant-card {
  border-radius: 8px !important;
  min-height: 78px;
  display: flex;

  &:focus::before {
    opacity: 0 !important;
  }

  &__title {
    min-width: 43px;
    color: #444444;
    font-size: 14px;
    font-weight: bold;
    margin-left: 7px;
    align-self: flex-start;
  }

  &__person {
    padding-left: 8px;
    height: 100%;
    align-self: center;

    &__icon {
      @include round-icon(48px);
    }

    span {
      font-size: 14px;
      color: #444444;
    }
  }
}
</style>
