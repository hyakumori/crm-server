<template>
  <main-section>
    <template #section class="archives-detail">
      <div class="archives-detail__section">
        <archive-basic-info-container
          :isDetail="isDetail"
          :id="id"
          editBtnContent="所有地を追加・編集"
          headerContent="協議情報"
        />

        <archive-document-container
          addBtnContent="さらに追加"
          class="mt-8"
          editBtnContent="配布資料を追加・編集"
          headerContent="配布資料等"
          v-if="isDetail"
        />

        <archive-participant-container
          addBtnContent="さらに追加"
          class="mt-9"
          editBtnContent="参加者を追加・編集"
          headerContent="先方参加者"
          v-if="isDetail"
          @saved="fetchParticipants"
          :id="id"
          :participants="participants"
        />

        <archive-related-user-container
          addBtnContent="さらに追加"
          class="mt-9"
          editBtnContent="参加者を追加・編集"
          headerContent="当方参加者"
          v-if="isDetail"
        />

        <archive-related-forest-container
          addBtnContent="さらに追加"
          class="mt-9"
          editBtnContent="森林を追加・編集"
          headerContent="関連する森林"
          v-if="isDetail"
        />
      </div>
    </template>
    <template #right>
      <div class="right-column">
        <action-log
          v-if="isDetail"
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
import ArchiveRelatedUserContainer from "../components/detail/ArchiveRelatedUserContainer";

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
    ArchiveRelatedUserContainer,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      backBtnContent: this.$t("page_header.archive_mgmt"),
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
      this.$rest.post(`/archives/${this.id}/cache`, {}, { no_activity: true });
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
