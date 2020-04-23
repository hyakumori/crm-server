<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      :update="isUpdate"
      @update="val => (isUpdate = val)"
    />
    <archive-basic-info class="mt-6" :isUpdate="isUpdate" />
    <update-button
      class="mb-12 mt-4"
      v-if="isUpdate"
      :cancel="cancel.bind(this)"
    />
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import ArchiveBasicInfo from "./ArchiveBasicInfo";
import UpdateButton from "./UpdateButton";

export default {
  name: "archive-basic-info-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    ArchiveBasicInfo,
    UpdateButton,
  },

  data() {
    return {
      isUpdate: false,
    };
  },
};
</script>
