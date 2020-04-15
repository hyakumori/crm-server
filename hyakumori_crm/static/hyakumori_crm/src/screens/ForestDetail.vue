<template>
  <main-section class="forest-detail">
    <template #section>
      <div class="forest-detail__section px-7">
        <content-header
          content="基本情報 (登記情報)"
          editBtnContent="所有地を追加・編集"
          :update="isUpdate.basicInfo"
          @update="updateBasicInfo"
        />
        <div class="my-4">
          <v-row>
            <v-col cols="6">
              <text-info
                title="住所"
                info="岡山県倉敷市大谷4-1-3"
                :isUpdate="isUpdate.basicInfo"
              />
              <text-info
                title="地番"
                info="1111"
                :isUpdate="isUpdate.basicInfo"
              />
              <text-info
                title="契約期間"
                info="2013/12/3 - 2020/12/3"
                :isUpdate="isUpdate.basicInfo"
              />
            </v-col>
            <v-col cols="6">
              <text-info
                title="大字"
                info="長尾"
                :isUpdate="isUpdate.basicInfo"
              />
              <text-info
                title="契約形態"
                info="10年契約"
                :isUpdate="isUpdate.basicInfo"
              />
              <text-info
                title="施業履歴"
                info="山田花子"
                :isUpdate="isUpdate.basicInfo"
              />
            </v-col>
          </v-row>
          <update-button
            class="mt-n3 mb-5"
            v-if="isUpdate.basicInfo"
            :cancel="cancel.bind(this, 'basicInfo')"
          />
        </div>

        <content-header
          content="所有林情報"
          editBtnContent="所有者を追加・編集"
          :update="isUpdate.contact"
          @update="updateContact"
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
          class="mb-9"
          v-if="isUpdate.contact"
          :cancel="cancel.bind(this, 'contact')"
        />

        <content-header
          content="協議履歴"
          editBtnContent="協議記録を追加・編集"
          :update="isUpdate.discussion"
          @update="updateDiscussion"
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
          :update="isUpdate.attach"
          @update="updateAttach"
        />
        <history-discussion
          class="mt-4"
          :discussions="getDiscussionsNotExpand"
          :isUpdate="isUpdate.attach"
        />
        <update-button
          v-if="isUpdate.attach"
          :cancel="cancel.bind(this, 'attach')"
        />
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
import contacts from "../assets/dump/contact_card.json";
import discussions from "../assets/dump/history_discussion.json";
import HistoryDiscussion from "../components/detail/HistoryDiscussionCard";
import TextInfo from "../components/detail/TextInfo";
import LogCard from "../components/detail/LogCard";
import UpdateButton from "../components/detail/UpdateButton";
import AdditionButton from "../components/AdditionButton";

export default {
  name: "forest-detail",

  components: {
    MainSection,
    ContentHeader,
    ContactTab,
    HistoryDiscussion,
    TextInfo,
    LogCard,
    UpdateButton,
    AdditionButton,
  },

  data() {
    return {
      isExpand: false,
      isUpdate: {
        basicInfo: false,
        contact: false,
        discussion: false,
        attach: false,
      },
    };
  },

  methods: {
    expandDiscussionList() {
      this.isExpand = !this.isExpand;
    },

    updateBasicInfo(val) {
      this.isUpdate.basicInfo = val;
    },

    updateDiscussion(val) {
      this.isUpdate.discussion = val;
    },

    updateAttach(val) {
      this.isUpdate.attach = val;
    },

    updateContact(val) {
      this.isUpdate.contact = val;
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
  },
};
</script>

<style lang="scss" scoped>
.forest-detail {
  &__section {
    width: 785px;
    background-color: white;
    padding-top: 45px;
    padding-bottom: 45px;
    box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
    border-radius: 4px;
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
