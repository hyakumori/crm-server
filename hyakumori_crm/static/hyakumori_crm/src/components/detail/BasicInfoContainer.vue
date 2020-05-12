<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :displayAdditionBtn="displayAdditionBtn"
      :loading="isLoading"
      @toggleEdit="val => (isUpdate = val)"
    />
    <div class="my-4">
      <slot
        v-if="isUpdate || !id"
        name="form"
        :toggleEditing="handleToggleEdit"
      ></slot>
      <basic-info v-if="!!id && !isUpdate" :infos="info" />
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
