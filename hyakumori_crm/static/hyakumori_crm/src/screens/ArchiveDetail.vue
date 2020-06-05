<template>
  <main-section>
    <template #section class="archives-detail">
      <div class="archives-detail__section">
        <archive-basic-info-container
          :isDetail="isDetail"
          :id="id"
          @input="archive = $event"
          toggleEditBtnContent="追加・編集"
          headerContent="協議情報"
          :allowEdit="allowEdit"
        />

        <archive-document-container
          addBtnContent="追加"
          class="mt-8"
          toggleEditBtnContent="追加・編集"
          headerContent="配布資料等"
          v-if="isDetail"
          :allowEdit="allowEdit"
        />

        <archive-participant-container
          addBtnContent="追加"
          class="mt-9"
          toggleEditBtnContent="追加・編集"
          headerContent="先方参加者"
          v-if="isDetail"
          @saved="fetchParticipants"
          :id="id"
          :participants="participants"
          :allowEdit="allowEdit"
        />

        <archive-related-user-container
          addBtnContent="追加"
          class="mt-9"
          toggleEditBtnContent="追加・編集"
          headerContent="当方参加者"
          v-if="isDetail"
          :allowEdit="allowEdit"
        />

        <archive-related-forest-container
          addBtnContent="追加"
          class="mt-9"
          toggleEditBtnContent="追加・編集"
          headerContent="関連する森林"
          v-if="isDetail"
          :allowEdit="allowEdit"
        />
      </div>
    </template>
    <template #right>
      <div class="right-column" v-if="isDetail">
        <tag-detail-card
          app-name="crm"
          object-type="archive"
          :object-id="$route.params.id"
          :tags="archiveTags"
          @input="archive.tags = $event"
        ></tag-detail-card>
        <action-log
          app-name="crm"
          object-type="archive"
          :object-id="$route.params.id"
        ></action-log>
      </div>
    </template>
  </main-section>
</template>

<script>
import actionLogs from "../assets/dump/action_log.json";
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import ArchiveBasicInfoContainer from "../components/detail/ArchiveBasicInfoContainer";
import ArchiveDocumentContainer from "../components/detail/ArchiveDocumentContainer";
import ArchiveParticipantContainer from "../components/detail/ArchiveParticipantContainer";
import ArchiveRelatedForestContainer from "../components/detail/ArchiveRelatedForestContainer";
import ActionLog from "../components/detail/ActionLog";
import TagDetailCard from "../components/tags/TagDetailCard";
import ArchiveRelatedUserContainer from "../components/detail/ArchiveRelatedUserContainer";
import { getDate } from "../helpers/datetime";
import { get as _get } from "lodash";

export default {
  name: "archive-detail",

  mixins: [ScreenMixin],

  components: {
    MainSection,
    ArchiveBasicInfoContainer,
    ArchiveDocumentContainer,
    ArchiveParticipantContainer,
    ArchiveRelatedForestContainer,
    ActionLog,
    TagDetailCard,
    ArchiveRelatedUserContainer,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      backBtnContent: this.$t("page_header.archive_mgmt"),
      archiveTags: {},
      archive: null,
      headerInfo: {
        title: this.$t("page_header.archive_new"),
        subTitle: "",
        backUrl: "/archives",
      },
      participants: [],
      participantsLoading: false,
    };
  },
  created() {
    if (this.isDetail) {
      this.fetchParticipants();
    } else {
      this.$store.dispatch("setHeaderInfo", this.headerInfo);
    }
  },
  mounted() {
    if (this.isDetail) {
      this.forceRefreshCache();
    }
  },

  methods: {
    forceRefreshCache() {
      try {
        this.$rest.post(
          `/cache/archives/${this.id}`,
          {},
          { no_activity: true },
        );
      } catch {
        //ignore
      }
    },
    async fetchParticipants() {
      this.participantsLoading = true;
      try {
        this.participants = await this.$rest.get(
          `/archives/${this.id}/customers`,
        );
      } catch (error) {}
      this.participantsLoading = false;
    },
    renderParticipants(data) {
      const list = _get(data, "attributes.customer_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "customer__name_kanji.last_name", "");
        results += " " + _get(list[0], "customer__name_kanji.first_name", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_human_kanji", {
              count: list.length - 1,
            });
        }
        return results;
      }
      return "";
    },
    setHeaderInfo() {
      this.$store.dispatch("setHeaderInfo", {
        title: this.archive.title,
        subTitle:
          getDate(this.archive.archive_date) +
          " " +
          this.renderParticipants(this.archive),
        backUrl: "/archives",
        tags: this.archive.tags,
      });
    },
  },
  computed: {
    id() {
      return this.$route.params.id;
    },

    getActionLogs() {
      return actionLogs;
    },

    isDetail() {
      return !!this.id;
    },
    user() {
      return JSON.parse(localStorage.getItem("user"));
    },
    allowEdit() {
      if (!this.archive) return false;
      if (
        this.user.groups.includes("限定ユーザ") &&
        this.user.id !== this.archive.author.id
      )
        return false;
      return true;
    },
  },
  watch: {
    archive: {
      deep: true,
      handler() {
        this.archiveTags = this.archive.tags;
        this.setHeaderInfo();
      },
    },
  },
};
</script>

<style lang="scss" scoped>
.archives-detail {
  &__section {
    margin: 0 0 30px 0;
    padding: 35px;
    width: 785px;
    background: white;
    border-radius: 4px;
    box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
  }
}
.right-column {
  min-width: 400px;
}
</style>
