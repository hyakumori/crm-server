<template>
  <main-section>
    <template #section class="archives-detail">
      <div class="archives-detail__section">
        <postal-history-info-container
          :isDetail="isDetail"
          :id="id"
          @input="archive = $event"
          toggleEditBtnContent="追加・編集"
          headerContent="書類送付情報"
          :allowEdit="allowEdit"
        />

        <postal-history-document-container
          addBtnContent="追加"
          class="mt-8"
          toggleEditBtnContent="追加・編集"
          headerContent="送付資料など"
          v-if="isDetail"
          :allowEdit="allowEdit"
        />

        <postal-history-participant-container
          addBtnContent="追加"
          class="mt-9"
          toggleEditBtnContent="追加・編集"
          headerContent="送付先"
          v-if="isDetail"
          @saved="fetchParticipants"
          :id="id"
          :participants="participants"
          :allowEdit="allowEdit"
        />

        <postal-history-related-user-container
          addBtnContent="追加"
          class="mt-9"
          toggleEditBtnContent="追加・編集"
          headerContent="送付者"
          v-if="isDetail"
          :allowEdit="allowEdit"
        />

        <postal-history-related-forest-container
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
          object-type="postalhistory"
          :object-id="$route.params.id"
          :tags="archiveTags"
          @input="archive.tags = $event"
        ></tag-detail-card>
        <action-log
          app-name="crm"
          object-type="postalhistory"
          :object-id="$route.params.id"
        ></action-log>
      </div>
    </template>
  </main-section>
</template>

<script>
import { get as _get } from "lodash";
import MainSection from "@/components/MainSection";
import ActionLog from "@/components/detail/ActionLog";
import TagDetailCard from "@/components/tags/TagDetailCard";
import { getDate } from "@/helpers/datetime";
import ScreenMixin from "@/screens/ScreenMixin";
import PostalHistoryInfoContainer from "./PostalHistoryInfoContainer";
import PostalHistoryDocumentContainer from "./PostalHistoryDocumentContainer";
import PostalHistoryParticipantContainer from "./PostalHistoryParticipantContainer";
import PostalHistoryRelatedForestContainer from "./PostalHistoryRelatedForestContainer";
import PostalHistoryRelatedUserContainer from "./PostalHistoryRelatedUserContainer";

export default {
  mixins: [ScreenMixin],

  components: {
    MainSection,
    PostalHistoryInfoContainer,
    PostalHistoryDocumentContainer,
    PostalHistoryParticipantContainer,
    PostalHistoryRelatedForestContainer,
    PostalHistoryRelatedUserContainer,
    TagDetailCard,
    ActionLog,
  },

  data() {
    return {
      pageIcon: this.$t("icon.archive_icon"),
      backBtnContent: this.$t("page_header.postalhistory_mgmt"),
      archiveTags: {},
      archive: null,
      headerInfo: {
        title: this.$t("page_header.postalhistory_new"),
        subTitle: "",
        backUrl: "/postal-histories",
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
      return;
      try {
        this.$rest.post(
          `/cache/postal-histories/${this.id}`,
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
          `/postal-histories/${this.id}/customers`,
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
        backUrl: "/postal-histories",
        tags: this.archive.tags,
      });
    },
  },
  computed: {
    id() {
      return this.$route.params.id;
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
