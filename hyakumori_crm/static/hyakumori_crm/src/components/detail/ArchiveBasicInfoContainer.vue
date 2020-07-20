<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :loading="loading"
      @toggleEdit="setUpdate"
      :display-addition-btn="isDetail"
      :displayAdditionBtn="allowEdit"
    />
    <archive-basic-info
      class="mt-6"
      :isUpdate="isUpdate"
      :isDetail="isDetail"
      :info="info"
      :isSave="isSave"
      @archive:save-disable="val => (saveDisabled = val)"
      @archive:update-basic-info="updateBasicInfo"
    >
      <template v-if="!isDetail" v-slot:create-btn="props">
        <v-btn
          color="primary"
          depressed
          :disabled="props.invalid"
          :loading="createLoading"
          @click="submit(props.info)"
        >
          {{ $t("buttons.continue") }}
        </v-btn>
      </template>
    </archive-basic-info>
    <update-button
      class="mb-12 mt-4"
      v-if="isUpdate"
      :saving="updateLoading"
      :save-disabled="saveDisabled"
      :cancel="cancel.bind(this)"
      :save="save.bind(this)"
    />
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import ArchiveDetailMixin from "./ArchiveDetailMixin";
import ArchiveBasicInfo from "./ArchiveBasicInfo";
import UpdateButton from "./UpdateButton";
import { cloneDeep } from "lodash";
import { toUtcDatetime } from "../../helpers/datetime";

export default {
  name: "archive-basic-info-container",

  mixins: [ContainerMixin, ArchiveDetailMixin],

  components: {
    ContentHeader,
    ArchiveBasicInfo,
    UpdateButton,
  },

  props: {
    isDetail: {
      type: Boolean,
      default: true,
    },
    id: String,
  },

  data() {
    return {
      isUpdate: false,
      isSave: false,
      loading: false,
      createLoading: false,
      updateLoading: false,
      saveDisabled: false,
      info: {},
      immutableInfo: {},
    };
  },

  async mounted() {
    if (this.isDetail && !this.info.author) {
      await this.$store.dispatch("setHeaderInfo", { title: "" });
      await this.fetchBasicInfo();
    }
  },

  methods: {
    cancel() {
      this.isUpdate = false;
      this.saveDisabled = false;
      this.info = this.immutableInfo;
    },

    setUpdate(val) {
      this.isUpdate = val;
      this.immutableInfo = cloneDeep(this.info);
    },

    dataMapping(basicInfo) {
      this.info = {
        id: basicInfo.id,
        archive_date: basicInfo.archive_date,
        location: basicInfo.location,
        future_action: basicInfo.future_action,
        author_id: basicInfo.author.id,
        author: basicInfo.author.full_name,
        content: basicInfo.content,
        title: basicInfo.title,
        attributes: basicInfo.attributes,
        tags: basicInfo.tags,
      };
    },

    async fetchBasicInfo() {
      if (!this.id) return;
      this.loading = true;
      const basicInfo = await this.$rest.get(`archives/${this.id}`);

      if (basicInfo) {
        this.loading = false;
        this.$emit("input", basicInfo.data);
        this.dataMapping(basicInfo.data);
      }
    },

    async submit(data) {
      this.createLoading = true;
      data.archive_date = toUtcDatetime(data.archive_date);
      try {
        const newData = await this.$rest.post("/archives", data);
        if (newData) {
          await this.$router.push(`/archives/${newData.id}`);
        }
      } catch (err) {}
      this.createLoading = false;
    },

    save() {
      this.isSave = true;
    },

    updateBasicInfo(val) {
      if (val) {
        this.updateLoading = true;
        val.archive_date = toUtcDatetime(val.archive_date);
        this.$rest
          .put(`/archives/${val.id}`, val)
          .then(res => {
            this.updateLoading = false;
            this.dataMapping(res.data);
            this.isUpdate = false;
            this.isSave = false;
            this.$emit("input", this.info);
          })
          .catch(() => {
            this.updateLoading = false;
            this.isSave = false;
          });
      }
    },
  },
  watch: {
    $route: "fetchBasicInfo",
  },
};
</script>
