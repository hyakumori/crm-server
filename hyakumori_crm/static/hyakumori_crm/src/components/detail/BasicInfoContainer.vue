<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :displayAdditionBtn="displayAdditionBtn"
      :loading="isLoading"
      @toggleEdit="val => (isUpdate = val)"
    />
    <div class="my-4">
      <slot
        v-if="isUpdate || !businessId"
        name="form"
        :toggleEditing="handleToggleEdit"
      ></slot>
      <basic-info v-if="!!businessId && !isUpdate" :infos="info" />
    </div>
  </div>
</template>

<script>
import BasicInfo from "./BasicInfo";
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";

export default {
  name: "basic-info-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    BasicInfo,
  },
  props: {
    businessId: String,
    id: String,
    info: Array,
    displayAdditionBtn: { type: Boolean, default: true },
  },
  data() {
    return {
      isUpdate: false,
      isSave: false,
    };
  },

  methods: {
    save() {
      this.isSave = true;
    },

    handleToggleEdit() {
      this.isUpdate = !this.isUpdate;
    },
  },
};
</script>
