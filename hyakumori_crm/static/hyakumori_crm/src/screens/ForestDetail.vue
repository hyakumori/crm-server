<template>
  <main-section class="forest-detail">
    <template #section>
      <div class="forest-detail__section px-7">
        <content-header
          content="基本情報 (登記情報)"
          editBtnContent="所有地を追加・編集"
          :update="isUpdate.basicInfo"
          @update="(val) => isUpdate.basicInfo = val"
        />
        <div class="my-4">
          <forest-basic-info :info="getInfo" :isUpdate="isUpdate.basicInfo" />
          <update-button
            class="mt-n3 mb-12"
            v-if="isUpdate.basicInfo"
            :cancel="cancel.bind(this, 'basicInfo')"
          />
        </div>

        <content-header
          content="所有林情報"
          editBtnContent="所有者を追加・編集"
          :update="isUpdate.contact"
          @update="(val) => isUpdate.contact = val"
        />
        <contact-tab
          class="mt-5"
          :class="{ 'mb-9': !isUpdate.contact }"
          :ownerContacts="getContacts"
          :contactorContacts="getContacts"
          :isUpdate="isUpdate.contact"
        />
        <addition-button v-if="isUpdate.contact" content="連絡者を追加" />
        <update-button
          class="mb-9 mt-2"
          v-if="isUpdate.contact"
          :cancel="cancel.bind(this, 'contact')"
        />

        <content-header
          content="協議履歴"
          editBtnContent="協議記録を追加・編集"
          :update="isUpdate.discussion"
          @update="(val) => isUpdate.discussion = val"
        />
        <template v-if="isExpand">
          <history-discussion
            class="mt-4"
            :isUpdate="isUpdate.discussion"
            :discussions="getDiscussionsExpand"
          />
        </template>
        <template v-else>
          <history-discussion
            class="mt-4"
            :isUpdate="isUpdate.discussion"
            :discussions="getDiscussionsNotExpand"
          />
        </template>
        <addition-button
          class="mb-3"
          v-if="isUpdate.discussion"
          content="協議履歴を追加"
          :click="addDiscussion.bind(this)"
        />
        <update-button
          v-if="isUpdate.discussion"
          :cancel="cancel.bind(this, 'discussion')"
        />
        <p class="forest-detail__expand" @click="expandDiscussionList">
          すべて表示する
        </p>

        <content-header
          content="書類郵送記録"
          editBtnContent="書類郵送記録を追加・編集"
          :update="isUpdate.archive"
          @update="(val) => isUpdate.archive = val"
        />
        <history-discussion
          class="mt-4"
          :class="{ 'pb-9': !isUpdate.archive }"
          :discussions="getDiscussionsNotExpand"
          :isUpdate="isUpdate.archive"
        />
        <update-button
          v-if="isUpdate.archive"
          :cancel="cancel.bind(this, 'archive')"
        />

        <content-header
          class="mt-9"
          content="森林情報"
          :displayAdditionBtn="false"
        />
        <forest-attribute-table :attributes="generateForestAttributeData" />
      </div>
    </template>

    <template #right>
      <div class="forest-detail__log-section ml-6">
        <h4 class="mb-1">更新履歴</h4>
        <log-card
          action="森に紐づく交渉履歴が更新されました"
          date="2020/2/31"
        />
        <log-card
          action="人が追加されました。"
          date="2020/2/23"
          editor="山田太郎"
        />
        <log-card
          action="顧客データが作成されました。"
          date="2020/2/23"
          editor="山田太郎"
        />
      </div>
    </template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";
import ContentHeader from "../components/detail/ContentHeader";
import ContactTab from "../components/detail/ContactTab";
import info from "../assets/dump/forest_detail.json";
import contacts from "../assets/dump/contact_card.json";
import discussions from "../assets/dump/history_discussion.json";
import HistoryDiscussion from "../components/detail/HistoryDiscussionCard";
import LogCard from "../components/detail/LogCard";
import UpdateButton from "../components/detail/UpdateButton";
import AdditionButton from "../components/AdditionButton";
import ForestBasicInfo from "../components/detail/ForestBasicInfo";
import ForestAttributeTable from "../components/detail/ForestAttributeTable";

export default {
  name: "forest-detail",

  components: {
    MainSection,
    ContentHeader,
    ContactTab,
    HistoryDiscussion,
    LogCard,
    UpdateButton,
    AdditionButton,
    ForestBasicInfo,
    ForestAttributeTable,
  },

  data() {
    return {
      isExpand: false,
      isUpdate: {
        basicInfo: false,
        contact: false,
        discussion: false,
        archive: false,
      },
    };
  },

  methods: {
    expandDiscussionList() {
      this.isExpand = !this.isExpand;
    },

    cancel(val) {
      this.isUpdate[val] = false;
    },

    addDiscussion() {
      console.log("add dis");
    },
  },

  computed: {
    getContacts() {
      return contacts;
    },

    getDiscussionsNotExpand() {
      const discuss = discussions.slice(0, 3);
      return discuss;
    },

    getDiscussionsExpand() {
      return discussions;
    },

    getInfo() {
      return info;
    },

    generateForestAttributeData() {
      const attr = info.forest_attributes;
      return [
        {
          area: "面積",
          unit: "ha",
          first_area: attr["第1面積_ha"],
          second_area: attr["第2面積_ha"],
          third_area: attr["第3面積_ha"],
        },
        {
          area: "樹種",
          unit: "",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "立木本数",
          unit: "",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "立木密度",
          unit: "本/ha",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "平均樹高",
          unit: "m",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "樹冠長率",
          unit: "%",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "平均胸高直径",
          unit: "cm",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "合計材積",
          unit: "m2",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "ha材積",
          unit: "m2/ha",
          first_area: attr["第1ha材積"],
          second_area: attr["第2ha材積"],
          third_area: attr["第3ha材積"],
        },
        {
          area: "収量比数",
          unit: "",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "相対幹距比",
          unit: "",
          first_area: "",
          second_area: "",
          third_area: "",
        },
        {
          area: "形状比",
          unit: "",
          first_area: attr["第1形状比"],
          second_area: attr["第2形状比"],
          third_area: attr["第3形状比"],
        },
      ];
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.forest-detail {
  &__section {
    @extend %detail-section-shared;
  }

  &__expand {
    margin-top: 20px;
    margin-bottom: 50px;
    width: fit-content;

    &:hover {
      cursor: pointer;
    }
  }
}
</style>
