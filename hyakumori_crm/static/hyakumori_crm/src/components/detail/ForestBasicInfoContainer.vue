<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      :update="isUpdate"
      @update="setUpdate"
    >
      <template v-slot:right="{ click, editBtnContent }">
        <addition-button
          v-acl-only="['manage_forest']"
          :content="editBtnContent"
          :click="click"
        />
      </template>
    </content-header>

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
        :saving="isSave"
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
import AdditionButton from "../AdditionButton";
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
    AdditionButton,
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
          this.$emit("forest:basic-info-updated", res);
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
