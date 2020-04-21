<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :update="isUpdate"
      :loading="isLoading"
      @update="val => (isUpdate = val)"
    />

    <customer-contact-list
      class="mt-4"
      :contacts="contacts"
      :isUpdate="isUpdate"
    />
    <addition-button class="my-2" v-if="isUpdate" :content="addBtnContent" />
    <update-button v-if="isUpdate" :cancel="cancel.bind(this)" />
  </div>
</template>

<script>
import ContainerMixin from "./ContainerMixin";
import ContentHeader from "./ContentHeader";
import CustomerContactList from "./CustomerContactList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";

export default {
  name: "customer-list-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    CustomerContactList,
    UpdateButton,
    AdditionButton,
  },

  props: {
    contacts: Array,
  },

  data() {
    return {
      isUpdate: false,
    };
  },
};
</script>
