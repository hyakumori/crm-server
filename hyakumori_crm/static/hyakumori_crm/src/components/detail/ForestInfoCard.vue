<template>
  <v-card
    class="forest-info-card d-flex d-hover"
    outlined
    :ripple="false"
    @click.self="onClickCard"
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

    <v-btn class="align-self-center" icon @click="onClick">
      <v-icon>{{ toggleUpdateIcon }}</v-icon>
    </v-btn>
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
  },

  methods: {
    onClick() {
      // Do click card
      if (this.card_id) {
        this.$router.push({
          name: "forest-detail",
          params: { id: this.card_id },
        });
        window.scrollTo(0, 0);
      }
    },

    onClickCard() {},
  },

  computed: {
    toggleUpdateIcon() {
      if (this.isUpdate) {
        return "mdi-close";
      } else {
        return "mdi-chevron-right";
      }
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

.forest-info-card {
  width: 100%;
  height: 100%;
  padding: 10px;
  border-radius: $border-radius !important;
  border: 1px solid #e1e1e1 !important;
  position: relative;

  &__icon {
    padding: 10px;
    background-color: $background-color;
    align-self: center;
    border-radius: 50% !important;
  }

  &__name {
    height: inherit;
    width: 100%;
    max-width: 234px;

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
