<template>
  <div>
    <content-header
      class="mb-4"
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      @toggleEdit="val => (isUpdate = val)"
    />
    <slot name="participants" :isUpdate="isUpdate"></slot>
    <template v-if="isUpdate">
      <addition-button class="my-2" :content="addBtnContent" />
      <update-button :cancel="cancel.bind(this)" />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";

export default {
  name: "archive-participant-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    UpdateButton,
    AdditionButton,
  },

  data() {
    return {
      isUpdate: false,
    };
  },
};
</script>
