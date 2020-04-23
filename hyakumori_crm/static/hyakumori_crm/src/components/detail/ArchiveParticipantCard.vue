<template>
  <v-card class="participant-card d-hover" outlined flat @click="onCardClick">
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
    <v-btn class="align-self-center mr-2" icon>
      <v-icon size="24" @click="onNavigation">mdi-chevron-right</v-icon>
    </v-btn>
  </v-card>
</template>

<script>
export default {
  name: "archive-participant-card",

  props: {
    isAuthor: {
      type: Boolean,
      default: false,
    },
    name: String,
  },

  methods: {
    onCardClick() {
      // TODO: handle card click
    },

    onNavigation() {
      // TODO: navigate
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../../styles/variables";

.participant-card {
  border-radius: 8px !important;
  min-height: 78px;
  display: flex;

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
