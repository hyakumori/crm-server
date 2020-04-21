<template>
  <v-row dense>
    <template v-for="(contact, index) in contacts">
      <v-col cols="6" :key="index">
        <customer-contact-card
          :card_id="contact.customer_id"
          :fullname="contact.fullname"
          :address="contact.address"
          :email="contact.email"
          :forestCount="contact.forest_count"
          :phone="contact.telephone"
          :cellphone="contact.mobilephone"
          :isOwner="isOwner"
          :isUpdate="isUpdate"
        />
      </v-col>
    </template>
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
  },
};
</script>
