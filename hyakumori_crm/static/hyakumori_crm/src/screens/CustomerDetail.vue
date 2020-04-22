<template>
  <main-section class="customer-detail">
    <template #section>
      <div class="customer-detail__section px-7">
        <basic-info-container
          headerContent="顧客情報"
          editBtnContent="所有地を追加・編集"
          :isLoading="customerLoading"
          :info="basicInfo"
        />

        <forest-list-container
          headerContent="所有林情報"
          editBtnContent="フォレストの追加/編集"
          addBtnContent="所有地情報を追加"
          :isLoading="forestsLoading"
          :forests="forests"
        />

        <customer-list-container
          class="mt-12"
          headerContent="連絡者情報"
          editBtnContent="連絡者を追加・編集"
          addBtnContent="連絡者を追加"
          :contacts="forestContacts"
          :isLoading="contactsLoading"
        />

        <attachment-container
          class="consultation-history mt-12"
          headerContent="協議履歴"
          editBtnContent="協議記録を追加・編集"
          addBtnContent="協議履歴を追加"
          :attaches="[]"
          :isLoading="false"
        />

        <customer-list-container
          class="mt-12"
          headerContent="家族情報"
          editBtnContent="家族を追加・編集"
          addBtnContent="連絡者を追加"
          :contacts="familyContacts"
          :isLoading="contactsLoading"
        />

        <customer-list-container
          class="mt-12"
          headerContent="その他関係者情報"
          editBtnContent="その他関係者を追加・編集"
          addBtnContent="連絡者を追加"
          :contacts="otherContacts"
          :isLoading="contactsLoading"
        />

        <forest-list-container
          class="mt-12"
          headerContent="顧客連絡者登録 森林"
          addBtnContent="所有地情報を追加"
          :displayAdditionBtn="false"
          :isLoading="false"
          :forests="[]"
        />

        <banking-info-container
          class="banking-info mt-12"
          headerContent="口座情報"
          editBtnContent="アカウント情報の追加/編集"
          :isLoading="customerLoading"
          :info="bankingInfo"
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
import ownersForest from "../assets/dump/owners_forest_info.json";
import discussions from "../assets/dump/history_discussion.json";
import actionLogs from "../assets/dump/action_log.json";
import LogCard from "../components/detail/LogCard";
import BasicInfoContainer from "../components/detail/BasicInfoContainer";
import BankingInfoContainer from "../components/detail/BankingInfoContainer";
import AttachmentContainer from "../components/detail/AttachmentContainer";
import ForestListContainer from "../components/detail/ForestListContainer";
import CustomerListContainer from "../components/detail/CustomerListContainer";
import { filter } from "lodash";

export default {
  mixins: [ScreenMixin],

  components: {
    MainSection,
    LogCard,
    BasicInfoContainer,
    AttachmentContainer,
    ForestListContainer,
    CustomerListContainer,
    BankingInfoContainer,
  },
  props: ["id"],
  data() {
    return {
      headerInfo: {
        title: "",
        subtitle: "",
        tag: "",
        backUrl: { name: "customers" },
      },
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
        bankingInfo: false,
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
    this.$rest.get(`/customers/${this.id}`).then(data => {
      this.customer = data;
      this.customerLoading = false;
    });
    this.$rest.get(`/customers/${this.id}/forests`).then(async data => {
      let forests = data.results;
      let next = data.next;
      //TODO: implement UI pagination
      while (!!next) {
        let nextForests = await this.$rest.get(data.next);
        forests.push(...nextForests.results);
        next = nextForests.next;
      }
      this.forests = forests;
      this.forestsLoading = false;
    });
    this.$rest.get(`/customers/${this.id}/contacts`).then(async data => {
      let contacts = data.results;
      let next = data.next;
      //TODO: implement UI pagination
      while (!!next) {
        let nextContacts = await this.$rest.get(data.next);
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
      if (nameObj && nameObj.last_name && nameObj.first_name) {
        return `${nameObj.last_name} ${nameObj.first_name}`;
      }

      return (nameObj && (nameObj.last_name || nameObj.first_name)) || "";
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

  watch: {
    customer: {
      deep: true,
      handler: function() {
        const tags = [];

        Object.keys(this.customer?.tags).forEach(k => {
          const tagValue = this.customer?.tags[k];
          tagValue && tags.push(`${tagValue}`);
        });
        this.headerInfo = {
          ...this.headerInfo,
          title: this.getPersonFullname(this.customer?.self_contact.name_kanji),
          tag: tags,
        };
      },
    },
    forests: {
      deep: true,
      handler: function() {
        this.headerInfo = {
          ...this.headerInfo,
          subTitle: `${(this.forests && this.forests.length) ||
            0}件の森林を所有`,
        };
      },
    },
    headerInfo: {
      deep: true,
      handler: function() {
        if (this.headerInfo.title && this.headerInfo.subTitle) {
          this.$store.dispatch("setHeaderInfo", this.headerInfo);
        }
      },
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
    font-size: 14px;
    color: #999;
    width: fit-content;

    &:hover {
      cursor: pointer;
    }
  }
}
</style>
