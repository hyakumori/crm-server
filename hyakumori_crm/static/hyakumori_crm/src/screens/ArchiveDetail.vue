<template>
  <main-section>
    <template #section class="archives-detail">
      <div class="archives-detail__section">
        <archive-basic-info-container
          headerContent="協議情報"
          editBtnContent="所有地を追加・編集"
        />

        <archive-document-container
          class="mt-8"
          headerContent="配布資料等"
          editBtnContent="配布資料を追加・編集"
          addBtnContent="さらに追加"
        />

        <archive-participant-container
          class="mt-9"
          headerContent="先方参加者"
          editBtnContent="参加者を追加・編集"
          addBtnContent="さらに追加"
        >
          <template v-slot:participants="props">
            <customer-contact-list
              :contacts="participants"
              :isUpdate="props.isUpdate"
            />
          </template>
        </archive-participant-container>

        <archive-participant-container
          class="mt-9"
          headerContent="当方参加者"
          editBtnContent="参加者を追加・編集"
          addBtnContent="さらに追加"
        >
          <template v-slot:participants="props">
            <archive-participant-list
              :participants="names"
              :isUpdate="props.isUpdate"
            />
          </template>
        </archive-participant-container>

        <archive-related-forest-container
          class="mt-9"
          headerContent="関連する森林"
          editBtnContent="森林を追加・編集"
          addBtnContent="さらに追加"
        />
      </div>
    </template>
    <template #right>
      <action-log
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
import ArchiveParticipantList from "../components/detail/ArchiveParticipantList";
import ArchiveRelatedForestContainer from "../components/detail/ArchiveRelatedForestContainer";
import ActionLog from "../components/detail/ActionLog";

export default {
  name: "archive-detail",

  mixins: [ScreenMixin],

  components: {
    MainSection,
    ArchiveBasicInfoContainer,
    ArchiveDocumentContainer,
    ArchiveParticipantContainer,
    CustomerContactList,
    ArchiveParticipantList,
    ArchiveRelatedForestContainer,
    ActionLog,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      backBtnContent: this.$t("page_header.archive_mgmt"),
      participants: [
        {
          customer_id: "123",
          fullname: "山田太郎",
          address: "424-0023 岡山県倉敷市大谷4-1-3",
          email: "hanako.yamada@gmail.com",
          forest_count: 4,
          telephone: "03-1313-4443",
          mobilephone: "090-2211-6654",
        },
        {
          customer_id: "123",
          fullname: "山田太郎",
          address: "424-0023 岡山県倉敷市大谷4-1-3",
          email: "hanako.yamada@gmail.com",
          forest_count: 4,
          telephone: "03-1313-4443",
          mobilephone: "090-2211-6654",
        },
      ],
      names: ["John Wick", "Marshmello"],
    };
  },
  computed: {
    getActionLogs() {
      return actionLogs;
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
