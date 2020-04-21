<template>
  <div class="forest-info">
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="ownerContacts.length === 0"
      :update="isUpdate"
      @update="val => (isUpdate = val)"
    />
    <contact-tab
      class="mt-5"
      :class="{ 'mb-10': !isUpdate }"
      :ownerContacts="ownerContacts"
      :isUpdate="isUpdate"
    />
    <template v-if="isUpdate">
      <addition-button class="my-2" :content="addBtnContent" />
      <update-button class="mb-9" :cancel="cancel.bind(this)" />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContactTab from "./ContactTab";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import ContainerMixin from "./ContainerMixin";

export default {
  name: "forest-contact-tab-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    ContactTab,
    UpdateButton,
    AdditionButton,
  },

  props: {
    ownerContacts: Array,
    contactorContacts: Array,
  },

  data() {
    return {
      isUpdate: false,
    };
  },
};
</script>
