<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      :update="isUpdate"
      @update="setUpdate"
    />
    <div class="mt-4">
      <forest-basic-info
        :info="mutableInfo"
        :isUpdate="isUpdate"
        :isSave="isSave"
        @updateInfo="updateData"
      />
      <update-button
        class="mb-12"
        v-if="isUpdate"
        :isLoading="isSave"
        :save="save.bind(this)"
        :cancel="cancel.bind(this)"
      />
    </div>
  </div>
</template>

<script>
import ForestBasicInfo from "./ForestBasicInfo";
import ContentHeader from "./ContentHeader";
import UpdateButton from "./UpdateButton";
import ContainerMixin from "./ContainerMixin";
import { updateBasicInfo } from "../../api/forest";
import { cloneDeep } from "lodash";

export default {
  name: "forest-basic-info-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    ForestBasicInfo,
    UpdateButton,
  },

  props: {
    info: Object,
  },

  data() {
    return {
      isUpdate: false,
      isSave: false,
      immutableInfo: {},
      mutableInfo: null,
    };
  },

  methods: {
    save() {
      this.isSave = true;
    },

    cancel() {
      this.mutableInfo = this.immutableInfo;
      this.isUpdate = false;
    },

    setUpdate(val) {
      this.isUpdate = val;
      this.immutableInfo = cloneDeep(this.mutableInfo);
    },

    updateData(updateInfo) {
      updateBasicInfo(this.info.id, updateInfo)
        .then(res => {
          this.mutableInfo = res;
          this.isSave = false;
          this.isUpdate = false;
        })
        .catch(() => {
          // TODO: Handle error later
        });
    },
  },

  watch: {
    info(val) {
      this.mutableInfo = val;
    },
  },
};
</script>
