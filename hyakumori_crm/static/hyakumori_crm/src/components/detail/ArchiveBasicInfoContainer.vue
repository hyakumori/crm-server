<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="loading"
      @toggleEdit="setUpdate"
      :display-addition-btn="isDetail"
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
import ArchiveBasicInfo from "./ArchiveBasicInfo";
import UpdateButton from "./UpdateButton";
import { cloneDeep } from "lodash";
import { toUtcDatetime, getDate } from "../../helpers/datetime";
import { get as _get } from "lodash";

export default {
  name: "archive-basic-info-container",

  mixins: [ContainerMixin],

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
      this.$store.dispatch("setHeaderInfo", { title: "" });
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
      };
    },

    async fetchBasicInfo() {
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
      const newData = await this.$rest.post("/archives", data);
      if (newData) {
        this.dataMapping(newData);
        this.createLoading = false;
        await this.$router.push(`/archives/${newData.id}`);
      }
    },

    save() {
      this.isSave = true;
    },

    updateBasicInfo(val) {
      if (val) {
        this.updateLoading = true;
        val.archive_date = toUtcDatetime(val.archive_date);
        this.$rest.put(`/archives/${val.id}`, val).then(res => {
          this.updateLoading = false;
          this.dataMapping(res.data);
          this.isUpdate = false;
          this.isSave = false;
        });
      }
    },
    renderParticipants(data) {
      const list = _get(data, "attributes.customer_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "customer__name_kanji.last_name", "");
        results += " " + _get(list[0], "customer__name_kanji.first_name", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_human", { count: list.length - 1 });
        }
        return results;
      }
      return "";
    },
  },
  watch: {
    info: {
      deep: true,
      handler() {
        if (this.isDetail) {
          this.$store.dispatch("setHeaderInfo", {
            title: this.info.title,
            subTitle:
              getDate(this.info.archive_date) +
              " " +
              this.renderParticipants(this.info),
            backUrl: "/archives",
          });
        }
      },
    },
  },
};
</script>
