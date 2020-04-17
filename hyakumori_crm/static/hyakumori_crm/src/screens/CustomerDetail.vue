<template>
  <main-section class="customer-detail">
    <template #section>
      <div class="customer-detail__section px-7">
        <content-header
          content="顧客情報"
          editBtnContent="所有地を追加・編集"
          :update="isUpdate.basicInfo"
          @update="val => (isUpdate.basicInfo = val)"
          :loading="customerLoading"
        />
        <div class="my-4">
          <basic-info :infos="basicInfo" :isUpdate="isUpdate.basicInfo" />
          <update-button
            class="mb-12"
            v-if="isUpdate.basicInfo"
            :cancel="cancel.bind(this, 'basicInfo')"
          />
        </div>

        <content-header
          content="所有林情報"
          editBtnContent="フォレストの追加/編集"
          :update="isUpdate.ownersForest"
          @update="val => (isUpdate.ownersForest = val)"
          :loading="forestsLoading"
        />
        <v-row class="mt-4">
          <template v-for="(forest, index) in forests">
            <v-col cols="6" :key="index">
              <contact-card
                mode="forest"
                :title="forest.internal_id"
                :subTitle="`${forest.customers_count}人の所有者`"
                :address="
                  `${forest.cadastral.subsector} ${forest.cadastral.sector} ${forest.cadastral.municipality} ${forest.cadastral.prefecture}`
                "
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
          :loading="contactsLoading"
        />
        <v-row class="mt-4">
          <template v-for="(contactor, index) in forestContacts">
            <v-col cols="6" :key="index">
              <contact-card
                mode="customer"
                :title="
                  `${contactor.name_kanji.last_name} ${contactor.name_kanji.first_name}`
                "
                :address="
                  `${contactor.postal_code} ${contactor.address.sector}`
                "
                :email="contactor.email"
                subTitle=""
                :phone="contactor.telephone"
                :cellphone="contactor.mobilephone"
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
          :loading="false"
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
          :loading="contactsLoading"
        />
        <v-row class="mt-4">
          <template v-for="(contactor, index) in familyContacts">
            <v-col cols="6" :key="index">
              <contact-card
                mode="customer"
                :title="
                  `${contactor.name_kanji.last_name} ${contactor.name_kanji.first_name}`
                "
                :address="
                  `${contactor.postal_code} ${contactor.address.sector}`
                "
                :email="contactor.email"
                subTitle=""
                :phone="contactor.telephone"
                :cellphone="contactor.mobilephone"
                :isUpdate="isUpdate.contactors"
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
          :loading="contactsLoading"
        />
        <v-row class="mt-4">
          <template v-for="(contactor, index) in otherContacts">
            <v-col cols="6" :key="index">
              <contact-card
                mode="customer"
                :title="
                  `${contactor.name_kanji.last_name} ${contactor.name_kanji.first_name}`
                "
                :address="
                  `${contactor.postal_code} ${contactor.address.sector}`
                "
                :email="contactor.email"
                subTitle=""
                :phone="contactor.telephone"
                :cellphone="contactor.mobilephone"
                :isUpdate="isUpdate.contactors"
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
          :loading="false"
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
          :loading="customerLoading"
        />
        <basic-info :infos="bankingInfo" :isUpdate="isUpdate.accountInfo" />
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
import discussions from "../assets/dump/history_discussion.json";
import actionLogs from "../assets/dump/action_log.json";
import ContactCard from "../components/detail/ContactCard";
import AdditionButton from "../components/AdditionButton";
import HistoryDiscussion from "../components/detail/HistoryDiscussionCard";
import LogCard from "../components/detail/LogCard";
import axios from "../plugins/http";
import { filter } from "lodash";

export default {
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
  props: ["id"],
  data() {
    return {
      pageIcon: this.$t("icon.customer_icon"),
      backBtnContent: this.$t("page_header.customer_mgmt"),
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
      customer: null,
      customerLoading: true,
      forests: [],
      forestsLoading: true,
      contacts: [],
      contactsLoading: true,
      selectedForestId: null,
    };
  },

  mounted() {
    const headerInfo = {
      title: "山田 太郎",
      subTitle: "4件の森林を所有",
      tag: "登録済",
    };
    this.$store.dispatch("setHeaderInfo", headerInfo);
    axios.get(`/customers/${this.id}`).then(data => {
      this.customer = data;
      this.customerLoading = false;
    });
    axios.get(`/customers/${this.id}/forests`).then(async data => {
      let forests = data.results;
      let next = data.next;
      while (!!next) {
        let nextForests = await axios.get(data.next);
        forests.push(...nextForests.results);
        next = nextForests.next;
      }
      this.forests = forests;
      this.forestsLoading = false;
    });
    axios.get(`/customers/${this.id}/contacts`).then(async data => {
      let contacts = data.results;
      let next = data.next;
      while (!!next) {
        let nextContacts = await axios.get(data.next);
        contacts.push(...nextContacts.results);
        next = nextContacts.next;
      }
      this.contacts = contacts;
      this.contactsLoading = false;
    });
  },

  methods: {
    expandDiscussionList() {
      this.isExpand = !this.isExpand;
    },

    cancel(val) {
      this.isUpdate[val] = false;
    },
    getPersonFullname(nameObj) {
      return nameObj ? `${nameObj.last_name}\u3000${nameObj.first_name}` : "";
    },
  },

  computed: {
    getOwnersForest() {
      // TODO: remove this
      return ownersForest;
    },

    forestContacts() {
      if (!this.selectedForestId)
        return filter(
          this.contacts,
          c =>
            c.forest_id ||
            (c.attributes && c.attributes.relationship_type === "本人"),
        );
      return filter(this.contacts, { forest_id: this.selectedForestId });
    },

    familyContacts() {
      return filter(
        this.contacts,
        () =>
          attributes &&
          !["本人", "その他"].includes(attributes.relationship_type),
      );
    },
    otherContacts() {
      return filter(this.contacts, {
        attributes: { relationship_type: "その他" },
      });
    },

    getDiscussionsNotExpand() {
      // TODO: remove this
      const discuss = discussions.slice(0, 3);
      return discuss;
    },

    getDiscussionsExpand() {
      // TODO: remove this
      return discussions;
    },

    getActionLogs() {
      // TODO: remove this
      return actionLogs;
    },

    basicInfo() {
      return [
        {
          label: this.$t("forms.labels.customer.fullname_kanji"),
          value: this.getPersonFullname(this.customer?.self_contact.name_kanji),
        },
        {
          label: this.$t("forms.labels.customer.fullname_kana"),
          value: this.getPersonFullname(this.customer?.self_contact.name_kana),
        },
        {
          label: this.$t("forms.labels.customer.postal_code"),
          value: this.customer?.self_contact.postal_code || "",
        },
        {
          label: this.$t("forms.labels.address"),
          value: this.customer?.self_contact.address.sector || "",
        },
        {
          label: this.$t("forms.labels.customer.phone_number"),
          value: this.customer?.self_contact.telephone || "",
        },
        {
          label: this.$t("forms.labels.customer.mobile_number"),
          value: this.customer?.self_contact.mobilephone || "",
        },
        {
          label: this.$t("forms.labels.email"),
          value: this.customer?.self_contact.email || "",
        },
      ];
    },

    bankingInfo() {
      return [
        {
          label: "口座指定者",
          value: "",
        },
        {
          label: "銀行名",
          value: this.customer?.banking?.bank_name || "",
        },
        {
          label: "支店名",
          value: this.customer?.banking?.branch_name || "",
        },
        {
          label: "預金種類",
          value: this.customer?.banking?.account_type || "",
        },
        {
          label: "口座番号",
          value: this.customer?.banking?.account_number || "",
        },
        {
          label: "口座名義",
          value: this.customer?.banking?.account_name || "",
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
