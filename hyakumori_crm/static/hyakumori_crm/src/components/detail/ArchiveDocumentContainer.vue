<template>
  <div>
    <content-header
      class="mb-3"
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      @toggleEdit="val => (isUpdate = val)"
    />
    <document-card
      class="my-2"
      v-for="(doc, index) in documents"
      :key="index"
      :fileName="doc"
    />
    <template v-if="isUpdate">
      <addition-button class="mb-2" :content="addBtnContent" />
      <update-button :cancel="cancel.bind(this)" />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import DocumentCard from "./DocumentCard";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";

export default {
  name: "archive-document-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    DocumentCard,
    UpdateButton,
    AdditionButton,
  },

  data() {
    return {
      isUpdate: false,
      documents: ["20200224_山田様議事録.docx", "20200225_山田様議事録.docx"],
    };
  },
};
</script>
