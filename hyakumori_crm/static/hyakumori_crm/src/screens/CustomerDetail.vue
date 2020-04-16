<template>
  <main-section class="customer-detail">
    <template #section>
      <div class="customer-detail__section px-7">
        <content-header
          content="顧客情報"
          editBtnContent="所有地を追加・編集"
          :update="isUpdate.basicInfo"
          @update="val => (isUpdate.basicInfo = val)"
        />
        <div class="my-4">
          <basic-info :infos="getBasicInfo" :isUpdate="isUpdate.basicInfo" />
          <update-button
            class="mt-n3 mb-12"
            v-if="isUpdate.basicInfo"
            :cancel="cancel.bind(this, 'basicInfo')"
          />
        </div>

        <content-header
          content="所有林情報"
          editBtnContent="フォレストの追加/編集"
          :update="isUpdate.ownersForest"
          @update="val => (isUpdate.ownersForest = val)"
        />
        <v-row class="mt-4">
          <template v-for="(ownerF, index) in getOwnersForest">
            <v-col cols="6" :key="index">
              <contact-card
                mode="forest"
                :title="ownerF.title"
                :subTitle="ownerF.sub_title"
                :address="ownerF.address"
              />
            </v-col>
          </template>
        </v-row>
        <addition-button
          class="mb-3"
          v-if="isUpdate.ownersForest"
          content="所有地情報を追加"
        />
        <update-button
          v-if="isUpdate.ownersForest"
          :cancel="cancel.bind(this, 'ownersForest')"
        />

        <content-header
          class="mt-12"
          content="連絡者情報"
          editBtnContent="連絡者を追加・編集"
          :update="isUpdate.contactors"
          @update="val => (isUpdate.contactors = val)"
        />
        <v-row class="mt-4">
          <template v-for="(contactor, index) in getContactors">
            <v-col cols="6" :key="index">
              <contact-card
                mode="customer"
                :title="contactor.name"
                :address="contactor.address"
                :email="contactor.email"
                :subTitle="contactor.forest_count"
                :phone="contactor.phone"
                :cellphone="contactor.cell_phone"
                :isUpdate="isUpdate.contactors"
                :isCustomer="true"
              />
            </v-col>
          </template>
        </v-row>
        <addition-button
          class="mb-3"
          v-if="isUpdate.contactors"
          content="連絡者を追加 "
        />
        <update-button
          v-if="isUpdate.contactors"
          :cancel="cancel.bind(this, 'contactors')"
        />

        <content-header
          class="mt-12"
          content="家族情報"
          editBtnContent="家族を追加・編集"
          :update="isUpdate.archive"
          @update="val => (isUpdate.archive = val)"
        />
        <template v-if="isExpand">
          <history-discussion
            class="mt-4"
            :isUpdate="isUpdate.archive"
            :discussions="getDiscussionsExpand"
          />
        </template>
        <template v-else>
          <history-discussion
            class="mt-4"
            :isUpdate="isUpdate.archive"
            :discussions="getDiscussionsNotExpand"
          />
        </template>
        <addition-button
          class="mb-3"
          v-if="isUpdate.archive"
          content="協議履歴を追加"
        />
        <update-button
          v-if="isUpdate.archive"
          :cancel="cancel.bind(this, 'archive')"
        />
        <p class="customer-detail__expand" @click="expandDiscussionList">
          すべて表示する
        </p>

        <content-header
          class="mt-12"
          content="連絡者情報"
          editBtnContent="連絡者を追加・編集"
          :update="isUpdate.family"
          @update="val => (isUpdate.family = val)"
        />
        <v-row class="mt-4">
          <template v-for="(contactor, index) in getContactors">
            <v-col cols="6" :key="index">
              <contact-card
                mode="customer"
                :title="contactor.name"
                :address="contactor.address"
                :email="contactor.email"
                :subTitle="contactor.forest_count"
                :phone="contactor.phone"
                :relationship="contactor.relationship"
                :cellphone="contactor.cell_phone"
                :isUpdate="isUpdate.family"
                :isCustomer="true"
              />
            </v-col>
          </template>
        </v-row>
        <addition-button
          class="mb-3"
          v-if="isUpdate.family"
          content="連絡者を追加 "
        />
        <update-button
          v-if="isUpdate.family"
          :cancel="cancel.bind(this, 'family')"
        />

        <content-header
          class="mt-12"
          content="その他関係者情報"
          editBtnContent="その他関係者を追加・編集"
          :update="isUpdate.otherRelated"
          @update="val => (isUpdate.otherRelated = val)"
        />
        <v-row class="mt-4">
          <template v-for="(contactor, index) in getContactors">
            <v-col cols="6" :key="index">
              <contact-card
                mode="customer"
                :title="contactor.name"
                :address="contactor.address"
                :email="contactor.email"
                :subTitle="contactor.forest_count"
                :phone="contactor.phone"
                :relationship="contactor.relationship"
                :cellphone="contactor.cell_phone"
                :isUpdate="isUpdate.otherRelated"
                :isCustomer="true"
              />
            </v-col>
          </template>
        </v-row>
        <addition-button
          class="mb-3"
          v-if="isUpdate.otherRelated"
          content="連絡者を追加 "
        />
        <update-button
          v-if="isUpdate.otherRelated"
          :cancel="cancel.bind(this, 'otherRelated')"
        />

        <content-header
          class="mt-12"
          content="顧客連絡者登録 森林"
          :displayAdditionBtn="false"
        />
        <v-row class="mt-4">
          <template v-for="(ownerF, index) in getOwnersForest">
            <v-col cols="6" :key="index">
              <contact-card
                mode="forest"
                :title="ownerF.title"
                :subTitle="ownerF.sub_title"
                :address="ownerF.address"
              />
            </v-col>
          </template>
        </v-row>

        <content-header
          class="mt-12"
          content="口座情報"
          editBtnContent="アカウント情報の追加/編集"
          :update="isUpdate.accountInfo"
          @update="val => (isUpdate.accountInfo = val)"
        />
        <basic-info :infos="getAccountInfo" :isUpdate="isUpdate.accountInfo" />
        <update-button
          v-if="isUpdate.accountInfo"
          :cancel="cancel.bind(this, 'accountInfo')"
        />
      </div>
    </template>

    <template #right>
      <div class="customer-detail__log ml-6">
        <h4 class="mb-1">更新履歴</h4>
        <log-card
          v-for="(log, index) in getActionLogs"
          :key="index"
          :action="log.action"
          :date="log.date"
          :editor="log.editor"
        />
      </div>
    </template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import ContentHeader from "../components/detail/ContentHeader";
import BasicInfo from "../components/detail/BasicInfo";
import UpdateButton from "../components/detail/UpdateButton";
import ownersForest from "../assets/dump/owners_forest_info.json";
import contactors from "../assets/dump/contact_card.json";
import discussions from "../assets/dump/history_discussion.json";
import actionLogs from "../assets/dump/action_log.json";
import ContactCard from "../components/detail/ContactCard";
import AdditionButton from "../components/AdditionButton";
import HistoryDiscussion from "../components/detail/HistoryDiscussionCard";
import LogCard from "../components/detail/LogCard";

export default {
  name: "forest-detail",

  mixins: [ScreenMixin],

  components: {
    MainSection,
    ContentHeader,
    BasicInfo,
    UpdateButton,
    ContactCard,
    AdditionButton,
    HistoryDiscussion,
    LogCard,
  },

  data() {
    return {
      pageIcon: this.$t("icon.customer_icon"),
      backBtnContent: this.$t("page_header.customer_list"),
      headerTagColor: "#12C7A6",
      isExpand: false,
      isUpdate: {
        basicInfo: false,
        ownersForest: false,
        contactors: false,
        archive: false,
        family: false,
        otherRelated: false,
        registrationForest: false,
        accountInfo: false,
      },
    };
  },

  mounted() {
    const headerInfo = {
      title: "山田 太郎",
      subTitle: "4件の森林を所有",
      tag: "登録済",
    };
    this.$store.dispatch("setHeaderInfo", headerInfo);
  },

  methods: {
    expandDiscussionList() {
      this.isExpand = !this.isExpand;
    },

    cancel(val) {
      this.isUpdate[val] = false;
    },
  },

  computed: {
    getOwnersForest() {
      return ownersForest;
    },

    getContactors() {
      return contactors;
    },

    getDiscussionsNotExpand() {
      const discuss = discussions.slice(0, 3);
      return discuss;
    },

    getDiscussionsExpand() {
      return discussions;
    },

    getActionLogs() {
      return actionLogs;
    },

    getBasicInfo() {
      return [
        {
          label: "郵便番号",
          value: "100-1111",
        },
        {
          label: "住所",
          value: "ヤマダタロウ",
        },
        {
          label: "電話番号",
          value: "04-2555-000",
        },
        {
          label: "住所",
          value: "ヤマダタロウ",
        },
        {
          label: "郵便番号",
          value: "100-1111",
        },
      ];
    },

    getAccountInfo() {
      return [
        {
          label: "口座指定者",
          value: "山田 花子",
        },
        {
          label: "銀行名|検索",
          value: "三井住友銀行",
        },
        {
          label: "支店名|検索",
          value: "424-0023",
        },
        {
          label: "預金種類|選択式",
          value: "岡山県倉敷市大谷4-1-3",
        },
        {
          label: "口座番号",
          value: "090-1242-2122",
        },
        {
          label: "口座名義",
          value: "03-1212-4131",
        },
      ];
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.customer-detail {
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
