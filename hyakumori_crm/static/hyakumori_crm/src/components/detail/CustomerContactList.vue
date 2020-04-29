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
        @click="(card_id, indx) => isUpdate && $emit('selected', card_id, indx)"
        @toggleDefault="
          (val, customer_id) => $emit('toggleDefault', val, customer_id)
        "
        @toggleContactDefault="
          (val, customer_id, contact_id) =>
            $emit('toggleContactDefault', val, customer_id, contact_id)
        "
        :selectedId="selectingId"
        :customerName="getCustomerName(contact.customer_id)"
      />
    </v-col>
  </v-row>
</template>

<script>
import CustomerContactCard from "./CustomerContactCard";

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
    customerIdNameMap: Object,
  },
  methods: {
    getCustomerName(customer_id) {
      if (!this.customerIdNameMap) return null;
      const nameObj = this.customerIdNameMap[customer_id];
      return `${nameObj.last_name} ${nameObj.last_name}`;
    },
  },
};
</script>
