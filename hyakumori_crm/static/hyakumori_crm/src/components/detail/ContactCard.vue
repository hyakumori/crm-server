<template>
  <v-card
    class="contact-card d-flex d-hover"
    outlined
    @click.self="onClickCard"
  >
    <v-icon class="contact-card__icon">{{ iconMode }}</v-icon>
    <div class="contact-card__name d-flex ml-4 flex-column">
      <div v-if="title" class="d-flex justify-space-between">
        <h4 class="body-2">
          {{ title }}
          <span class="caption">{{ subTitle }}</span>
        </h4>

        <p class="green--text mb-0 ml-2 caption">{{ getRelationship }}</p>
      </div>

      <div v-if="address" class="text-truncate">
        <v-icon small>mdi-map-marker</v-icon>
        <span class="ml-1 caption">{{ address }}</span>
      </div>

      <div class="d-flex text-truncate" v-if="email">
        <v-icon small>mdi-email</v-icon>
        <span class="ml-1 caption">{{ email }}</span>
      </div>

      <div class="d-flex">
        <template v-if="phone">
          <v-icon small>mdi-phone</v-icon>
          <span class="ml-1 pr-2 caption">{{ phone }}</span>
        </template>

        <template v-if="cellphone">
          <v-icon small>mdi-cellphone</v-icon>
          <span class="ml-1 caption">{{ cellphone }}</span>
        </template>
      </div>

      <div
        class="contact-card__related-info caption black--text mt-1"
        v-if="relatedInfo"
      >
        {{ relatedInfo }}
      </div>

      <v-select
        v-if="isUpdate && isCustomer"
        class="contact-card__select-relationship mt-2"
        outlined
        dense
        placeholder="続き柄を選択"
        :items="RELATIONSHIP"
        @change="selectedRelationship"
      ></v-select>
    </div>

    <v-btn class="align-self-center" icon @click="onClick">
      <v-icon>{{ toggleUpdateIcon }}</v-icon>
    </v-btn>

    <div
      class="contact-card__tag"
      v-bind:class="{ owner: isOwner, contactor: isContactor }"
    ></div>
  </v-card>
</template>

<script>
export default {
  name: "contact-card",

  props: {
    mode: String,
    customer_id: String,
    title: String,
    subTitle: String,
    address: String,
    email: String,
    phone: String,
    cellphone: String,
    relationship: String,
    relatedInfo: String,
    isOwner: Boolean,
    isContactor: Boolean,
    isUpdate: Boolean,
    isCustomer: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      RELATIONSHIP: [
        this.$t("detail.tabs.relationship.owner"),
        this.$t("detail.tabs.relationship.parent"),
        this.$t("detail.tabs.relationship.husband"),
        this.$t("detail.tabs.relationship.wife"),
        this.$t("detail.tabs.relationship.son"),
        this.$t("detail.tabs.relationship.daughter"),
        this.$t("detail.tabs.relationship.grand_child"),
        this.$t("detail.tabs.relationship.friend"),
        this.$t("detail.tabs.relationship.relatives"),
        this.$t("detail.tabs.relationship.others"),
      ],
      innerRelationship: "",
    };
  },

  methods: {
    onClick() {
      // this.$emit("onClick", this.id);
    },

    onClickCard() {
      // Do click card
    },

    selectedRelationship(val) {
      this.innerRelationship = val;
    },
  },

  computed: {
    iconMode() {
      if (this.mode === "forest") {
        return this.$t("icon.forest_icon");
      } else {
        return this.$t("icon.customer_icon");
      }
    },

    toggleUpdateIcon() {
      if (this.isUpdate) {
        return "mdi-close";
      } else {
        return "mdi-chevron-right";
      }
    },

    getRelationship() {
      if (this.relationship) {
        return this.relationship;
      } else {
        return this.innerRelationship;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$border-radius: 8px;
$background-color: #f5f5f5;

.contact-card::before {
  border-radius: $border-radius;
}

.contact-card {
  width: 100%;
  height: auto;
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
