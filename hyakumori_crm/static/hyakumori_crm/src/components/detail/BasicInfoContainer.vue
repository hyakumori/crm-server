<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      :update="isUpdate"
      @update="val => (isUpdate = val)"
    />
    <div class="my-4">
      <slot
        v-if="isUpdate || !id"
        name="form"
        :toggleEditing="
          () => {
            isUpdate = !isUpdate;
          }
        "
      ></slot>
      <basic-info v-if="!!id && !isUpdate" :infos="info" />
    </div>
  </div>
</template>

<script>
import BasicInfo from "./BasicInfo";
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import { updateBasicInfo } from "../../api/forest";
import { zipObjectDeep } from "lodash";

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

    updateData(updateInfo) {
      const key = updateInfo.map(info => info.attr);
      const val = updateInfo.map(info => info.value);
      const info = zipObjectDeep(key, val);
      updateBasicInfo(this.id, info);
    },
  },
};
</script>
