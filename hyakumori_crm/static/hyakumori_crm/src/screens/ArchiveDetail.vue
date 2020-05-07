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
        >
          <template v-slot:participants="props">
            <customer-contact-list
              :contacts="participants"
              :isUpdate="props.isUpdate"
            />
          </template>
        </archive-participant-container>

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
      <action-log
        v-if="isDetail"
        app-name="crm"
        object-type="archive"
        :object-id="$route.params.id"
      ></action-log>
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
import CustomerContactList from "../components/detail/CustomerContactList";
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
    CustomerContactList,
    ArchiveRelatedForestContainer,
    ActionLog,
    ArchiveRelatedUserContainer,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      backBtnContent: this.$t("page_header.archive_mgmt"),
      participants: [],
    };
  },

  mounted() {
    if (this.isDetail) {
      this.forceRefreshCache();
    }
  },

  methods: {
    forceRefreshCache() {
      this.$rest.post(`/archives/${this.id}/cache`);
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
</style>
