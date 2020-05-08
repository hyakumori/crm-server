<template>
  <v-card
    :color="mode != 'view' && selected ? '#dddddd' : undefined"
    class="customer-contact-card d-flex d-hover"
    :class="{ flat: flat, deleted: deleted, added: added }"
    outlined
    active-class="selected"
    :ripple="mode != 'view'"
    @click="$emit('click', contact.id, index)"
  >
    <v-icon class="customer-contact-card__icon">{{
      $t("icon.customer_icon")
    }}</v-icon>

    <div class="customer-contact-card__name d-flex ml-4 flex-column">
      <div class="d-flex justify-space-between">
        <h4 class="body-2">
          {{ fullname }}
          <span class="caption">{{ forestsCount || 0 }} 件の森林</span>
        </h4>

        <p class="green--text mb-0 ml-2 caption">{{ relationshipType }}</p>
      </div>

      <div class="text-truncate">
        <v-icon small>mdi-map-marker</v-icon>
        <span class="ml-1 caption min-width-90">
          {{ address || $t("not_available_field") }}
        </span>
      </div>

      <div class="d-flex text-truncate">
        <v-icon small>mdi-email</v-icon>
        <span class="ml-1 caption min-width-90">
          {{ email || $t("not_available_field") }}
        </span>
      </div>

      <div class="d-flex">
        <template>
          <v-icon small>mdi-phone</v-icon>
          <span class="ml-1 pr-2 caption min-width-90">
            {{ phone || $t("not_available_field") }}
          </span>
        </template>

        <template>
          <v-icon small>mdi-cellphone</v-icon>
          <span class="ml-1 caption min-width-90">
            {{ cellphone || $t("not_available_field") }}
          </span>
        </template>
      </div>

      <div
        class="customer-contact-card__related-info caption black--text mt-1"
        v-if="relatedInfo"
      >
        {{ relatedInfo }}
      </div>

      <v-select
        v-if="isUpdate && showRelationshipSelect"
        class="customer-contact-card__select-relationship mt-2"
        outlined
        dense
        hide-details
        placeholder="続き柄を選択"
        :items="RELATIONSHIP"
        @change="val => $emit('relationshipChange', contact.id, val)"
        :value="relationshipType"
      ></v-select>
      <p class="ma-0 pt-2 caption text-truncate" v-if="forestId">
        {{ forestId }}
      </p>
      <p class="ma-0 pt-2 caption text-truncate" v-if="customerName">
        <span style="background-color:#f5f5f5;color: black">
          {{ customerName.replace("null", "") }}の関係連絡先
        </span>
      </p>
    </div>
    <v-btn
      v-if="deleted"
      class="align-self-center"
      icon
      @click.stop="$emit('undoDeleteContact')"
    >
      <v-icon>mdi-undo</v-icon>
    </v-btn>
    <router-link
      v-if="showAction && !deleted"
      :to="{ name: 'customer-detail', params: { id: card_id } }"
      v-slot="{ href }"
    >
      <v-btn
        class="align-self-center"
        icon
        @click.stop="isUpdate ? $emit('deleteContact') : undefined"
        :href="isUpdate ? null : href"
      >
        <v-icon>{{ actionIcon }}</v-icon>
      </v-btn>
    </router-link>

    <div
      v-if="
        mode !== 'search' &&
          !contact.deleted &&
          (isUpdate || this.contact.default)
      "
      class="customer-contact-card__tag"
      :title="$t('buttons.set_as_default')"
      :class="{
        owner: isOwner,
        contactor: isContactor,
        default: this.contact.default,
      }"
      @click.stop="onTagClick"
    ></div>
  </v-card>
</template>

<script>
export default {
  name: "customer-contact-card",

  props: {
    card_id: String,
    relatedInfo: String,
    isOwner: Boolean,
    isContactor: Boolean,
    isUpdate: Boolean,
    showAction: { type: Boolean, default: true },
    flat: { type: Boolean, default: false },
    deleted: { type: Boolean, default: false },
    added: { type: Boolean, default: false },
    selectedId: String,
    selectedIndex: Number,
    index: Number,
    handleDeleteClick: Function,
    mode: { type: String, default: "view" },
    showRelationshipSelect: { type: Boolean, default: true },
    contact: Object,
    customerName: String,
  },

  data() {
    return {
      RELATIONSHIP: [
        "本人",
        "両親",
        "夫",
        "妻",
        "息子",
        "娘",
        "孫",
        "友人",
        "その他親族",
        "その他",
      ],
    };
  },

  methods: {
    onTagClick() {
      if (!this.isUpdate) return;
      if (this.isOwner)
        this.$emit("toggleDefault", !this.contact.default, this.card_id);
      else if (this.isContactor)
        this.$emit(
          "toggleContactDefault",
          !this.contact.default,
          this.contact.customer_id,
          this.contact.id,
        );
    },
    onClickCard() {},
  },

  computed: {
    contact_() {
      return this.contact.self_contact
        ? this.contact.self_contact
        : this.contact;
    },
    fullname() {
      if (
        this.contact_.name_kanji.last_name &&
        this.contact_.name_kanji.first_name
      ) {
        return `${this.contact_.name_kanji.last_name} ${this.contact_.name_kanji.first_name}`;
      }
      return (
        this.contact_.name_kanji.last_name ||
        this.contact_.name_kanji.first_name ||
        this.$t("not_available_field")
      );
    },
    address() {
      return `${this.contact_.postal_code || ""} ${this.contact_.address
        .sector || ""} ${this.contact_.address.municipality || ""} ${this
        .contact_.address.prefecture || ""}`;
    },
    email() {
      return this.contact_.email;
    },
    phone() {
      return this.contact_.telephone;
    },
    cellphone() {
      return this.contact_.mobilephone;
    },
    forestId() {
      return this.contact.forest_id;
    },
    forestsCount() {
      return this.contact.forests_count;
    },
    actionIcon() {
      return this.isUpdate ? "mdi-close" : "mdi-chevron-right";
    },
    selected() {
      return (
        this.selectedId === this.contact.id && this.selectedIndex === this.index
      );
    },
    relationshipType() {
      return this.isContactor ? this.contact.cc_attrs?.relationship_type : "";
    },
  },
};
</script>

<style lang="scss" scoped>
$border-radius: 8px;
$background-color: #f5f5f5;

.min-width-90 {
  min-width: 90px;
}

.customer-contact-card::before {
  border-radius: $border-radius;
}

.customer-contact-card.flat {
  border: none !important;
  border-radius: 0 !important;
  border-bottom: 1px solid #e1e1e1 !important;
}

.customer-contact-card.deleted {
  border: 1px solid #ff5252 !important;
}

.customer-contact-card.added {
  border: 1px solid #12c7a6 !important;
}

.customer-contact-card {
  width: 100%;
  min-height: 116px;
  max-height: 100%;
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
    height: inherit;
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
    background-color: #e1e1e1;
    opacity: 0.45;
    &:hover {
      opacity: 1;
    }
  }

  & .owner.default {
    background-color: #12c7a6;
    opacity: 1;
  }

  & .contactor.default {
    opacity: 1;
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
