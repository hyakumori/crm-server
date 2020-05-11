<template>
  <v-tabs class="contact-tabs" height="35" hide-slider>
    <v-tab
      class="contact-tabs__owner"
      active-class="contact-tabs__owner--active"
      @click="ownerTabClick"
      >{{ $t("detail.tabs.owner") }}</v-tab
    >

    <v-tab
      class="contact-tabs__contactor ml-1"
      active-class="contact-tabs__contactor--active"
      @click="contactorTabClick"
      >{{ $t("detail.tabs.contactor") }}</v-tab
    >

    <v-spacer></v-spacer>

    <v-switch
      class="contact-tabs__switch mt-0 pr-4"
      label="代表連絡者"
      :ripple="false"
      :color="switchColor"
    ></v-switch>

    <v-tab-item>
      <customer-contact-list
        :contacts="customers"
        :isUpdate="isEditing"
        :isOwner="true"
        :showRelationshipSelect="false"
        @deleteContact="
          (customer, index) => $emit('deleteCustomer', customer, index)
        "
        @undoDeleteContact="
          (customer, index) => $emit('undoDeleteCustomer', customer, index)
        "
        @selected="(card_id, indx) => $emit('customerSelected', card_id, indx)"
        @toggleDefault="
          (val, customer_id) => $emit('toggleDefault', val, customer_id)
        "
        :selectingId="selectingCustomerId"
        :showDefaultBadge="true"
      />
    </v-tab-item>

    <v-tab-item>
      <customer-contact-list
        :contacts="customersContacts"
        :isUpdate="isEditing"
        :isContactor="true"
        :showRelationshipSelect="false"
        :customerIdNameMap="customerIdNameMap"
        @toggleContactDefault="
          (val, customer_id, contact_id) =>
            $emit('toggleContactDefault', val, customer_id, contact_id)
        "
        :showDefaultBadge="true"
      />
    </v-tab-item>
  </v-tabs>
</template>

<script>
import CustomerContactList from "../detail/CustomerContactList";

export default {
  name: "contact-tab",

  components: {
    CustomerContactList,
  },

  data() {
    return {
      selectedTab: "owner",
    };
  },

  props: {
    customers: Array,
    customersContacts: Array,
    isEditing: Boolean,
    selectingCustomerId: String,
    customerIdNameMap: Object,
  },

  methods: {
    ownerTabClick() {
      this.selectedTab = "owner";
    },

    contactorTabClick() {
      this.selectedTab = "contactor";
    },
  },

  computed: {
    switchColor() {
      return this.selectedTab === "owner" ? "#12c7a6" : "#f36c69";
    },
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

.contact-tabs ::v-deep {
  .v-tabs-items {
    margin-top: 8px;
  }
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
    margin-left: 6px;

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

  &__switch ::v-deep {
    label {
      font-size: 14px;
      color: #444444;
    }
  }
}
</style>
