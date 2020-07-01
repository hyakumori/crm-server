<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :loading="isLoading"
      @toggleEdit="setUpdate"
      :permissions="['manage_forest']"
    />

    <div class="mt-4">
      <forest-basic-info
        :info="info"
        :isUpdate.sync="isUpdate"
        :isSave="isSave"
        @updateInfo="updateData"
        :formErrors.sync="formErrors"
      />
    </div>
  </div>
</template>

<script>
import ForestBasicInfo from "./ForestBasicInfo";
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import { updateBasicInfo } from "../../api/forest";

export default {
  name: "forest-basic-info-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    ForestBasicInfo,
  },

  props: {
    info: Object,
  },

  data() {
    return {
      isUpdate: false,
      isSave: false,
      saveDisabled: false,
      formErrors: null,
    };
  },

  methods: {
    setUpdate(val) {
      this.isUpdate = val;
    },

    updateData(updateInfo) {
      updateBasicInfo(this.info.id, updateInfo)
        .then(res => {
          this.$emit("forest:basic-info-updated", res);
          this.isSave = false;
          this.isUpdate = false;
        })
        .catch(e => {
          if (e.response.status === 400 && e.response.data?.errors) {
            this.formErrors = e.response.data.errors;
          } else {
            this.$dialog.notify.error(
              this.$t("messages.api_update_general_error"),
            );
          }
          this.isSave = false;
          this.isLoading = false;
        });
    },
  },
};
</script>
