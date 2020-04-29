<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      @toggleEdit="val => (isUpdate = val)"
    />
    <div class="my-4">
      <basic-info :infos="info" :isUpdate="isUpdate" />
      <update-button
        class="mb-12"
        v-if="isUpdate"
        :cancel="cancel.bind(this)"
      />
    </div>
  </div>
</template>

<script>
import BasicInfo from "./BasicInfo";
import ContentHeader from "./ContentHeader";
import UpdateButton from "./UpdateButton";
import ContainerMixin from "./ContainerMixin";

export default {
  name: "banking-info-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    BasicInfo,
    UpdateButton,
  },

  props: {
    info: Array,
  },

  data() {
    return {
      isUpdate: false,
    };
  },
};
</script>
