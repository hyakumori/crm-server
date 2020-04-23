<template>
  <div>
    <content-header
      class="mb-4"
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      :update="isUpdate"
      @update="val => (isUpdate = val)"
    />

    <forest-info-list :forests="relatedForests" :isUpdate="isUpdate" />
    <template v-if="isUpdate">
      <addition-button class="my-2" :content="addBtnContent" />
      <update-button :cancel="cancel.bind(this)" />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import ForestInfoList from "./ForestInfoList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";

export default {
  name: "archive-related-forest-container",

  mixins: [ContainerMixin],

  components: {
    ForestInfoList,
    ContentHeader,
    UpdateButton,
    AdditionButton,
  },

  data() {
    return {
      isUpdate: false,
      relatedForests: [
        {
          id: "123",
          internal_id: "456",
          customers_count: 12,
          cadastral: {
            prefecture: "newyork",
            municipality: "detroit",
            sector: "london",
            subsector: "321",
          },
        },
        {
          id: "123",
          internal_id: "456",
          customers_count: 12,
          cadastral: {
            prefecture: "newyork",
            municipality: "detroit",
            sector: "london",
            subsector: "321",
          },
        },
        {
          id: "123",
          internal_id: "456",
          customers_count: 12,
          cadastral: {
            prefecture: "newyork",
            municipality: "detroit",
            sector: "london",
            subsector: "321",
          },
        },
      ],
    };
  },
};
</script>
