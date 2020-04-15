<template>
  <v-tabs class="contact-tabs" height="35" hide-slider>
    <v-tab
      class="contact-tabs__owner"
      active-class="contact-tabs__owner--active"
      >{{ $t("detail.tabs.owner") }}</v-tab
    >

    <v-tab
      class="contact-tabs__contactor"
      active-class="contact-tabs__contactor--active"
      >{{ $t("detail.tabs.contactor") }}</v-tab
    >

    <v-tab-item>
      <v-row>
        <template v-for="(contact, index) in ownerContacts">
          <v-col :key="index">
            <contact-card
              mode="customer"
              :title="contact.name"
              :address="contact.address"
              :email="contact.email"
              :subTitle="contact.forest_count"
              :phone="contact.phone"
              :cellphone="contact.cell_phone"
              :isOwner="true"
              :isUpdate="isUpdate"
            />
          </v-col>
        </template>
      </v-row>
    </v-tab-item>

    <v-tab-item>
      <v-row>
        <template v-for="(contact, index) in contactorContacts">
          <v-col :key="index">
            <contact-card
              mode="customer"
              :title="contact.name"
              :address="contact.address"
              :email="contact.email"
              :subTitle="contact.forest_count"
              :phone="contact.phone"
              :cellphone="contact.cell_phone"
              :isContactor="true"
              :isUpdate="isUpdate"
            />
          </v-col>
        </template>
      </v-row>
    </v-tab-item>
  </v-tabs>
</template>

<script>
import ContactCard from "../detail/ContactCard";

export default {
  name: "contact-tab",

  components: {
    ContactCard,
  },

  props: {
    ownerContacts: Array,
    contactorContacts: Array,
    isUpdate: Boolean,
  },
};
</script>

<style lang="scss" scoped>
$owner-color: #12c7a6;
$contactor-color: #f36c69;
$border-tabs: 18px;

@mixin tab-default($color) {
  color: $color !important;
  font-size: 14px;
  font-weight: bold;
}

@mixin tab-active($color) {
  background-color: $color;
  border-radius: 18px;
  color: white !important;
  line-height: 14px;
}

.contact-tabs {
  width: 100%;
  height: fit-content;

  &__owner {
    @include tab-default($owner-color);

    &::before {
      border-radius: $border-tabs;
    }

    &:hover {
      border-radius: $border-tabs;
    }

    &--active {
      @include tab-active($owner-color);
    }
  }

  &__contactor {
    @include tab-default($contactor-color);

    &::before {
      border-radius: $border-tabs;
    }

    &:hover {
      border-radius: $border-tabs;
    }

    &--active {
      @include tab-active($contactor-color);
    }
  }
}
</style>
