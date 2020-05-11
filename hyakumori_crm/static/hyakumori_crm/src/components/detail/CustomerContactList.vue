<template>
  <v-row dense>
    <v-col v-for="(contact, index) in contacts" cols="6" :key="index">
      <customer-contact-card
        :card_id="contact.customer_id || contact.id"
        :contact="contact"
        :isOwner="isOwner"
        :isContactor="isContactor"
        :isUpdate="isUpdate"
        :index="index"
        @deleteContact="$emit('deleteContact', contact, index)"
        @undoDeleteContact="$emit('undoDeleteContact', contact, index)"
        :added="contact.added"
        :deleted="contact.deleted"
        :showRelationshipSelect="showRelationshipSelect"
        @click="
          (contact_id, indx) => isUpdate && $emit('selected', contact_id, indx)
        "
        @toggleDefault="handleToggleCustomerDefault"
        @toggleContactDefault="handleToggleContactDefault"
        @relationshipChange="handleRelationshipChange"
        :selectedId="selectingId"
        :selectedIndex="selectingIndex"
        :customerName="
          (!contact.is_basic && getCustomerName(contact.customer_id)) || ''
        "
        :mode="mode"
        :showDefaultBadge="showDefaultBadge"
      />
    </v-col>
  </v-row>
</template>

<script>
import CustomerContactCard from "./CustomerContactCard";
import { isEmpty } from "lodash";

export default {
  name: "customer-contact-list",

  components: {
    CustomerContactCard,
  },

  props: {
    contacts: Array,
    isUpdate: Boolean,
    isOwner: Boolean,
    isContactor: Boolean,
    showRelationshipSelect: { type: Boolean, default: true },
    selectingId: String,
    selectingIndex: Number,
    customerIdNameMap: Object,
    mode: String,
    showDefaultBadge: { type: Boolean, default: false },
  },
  methods: {
    getCustomerName(customer_id) {
      if (isEmpty(this.customerIdNameMap)) return null;
      const nameObj = this.customerIdNameMap[customer_id];
      if (!nameObj) return null;
      return `${nameObj.last_name} ${nameObj.first_name}`;
    },
    handleToggleCustomerDefault(val, customer_id) {
      this.$emit("toggleDefault", val, customer_id);
    },
    handleToggleContactDefault(val, customer_id, contact_id) {
      this.$emit("toggleContactDefault", val, customer_id, contact_id);
    },
    handleRelationshipChange(contact_id, val) {
      this.$emit("relationshipChange", contact_id, val);
    },
  },
};
</script>
