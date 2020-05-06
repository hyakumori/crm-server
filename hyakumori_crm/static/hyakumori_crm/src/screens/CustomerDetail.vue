<template>
  <main-section class="customer-detail">
    <template #section>
      <div class="customer-detail__section px-7">
        <basic-info-container
          headerContent="顧客情報"
          editBtnContent="所有地を追加・編集"
          :displayAdditionBtn="isDetail"
          :isLoading="customerLoading"
          :info="basicInfo"
          :id="id"
        >
          <template #form="props">
            <contact-form
              :id="id"
              :form="selfContactFormData"
              :toggleEditing="props.toggleEditing"
              :showCancel="isDetail"
              @updated="fetchCustomer"
            />
          </template>
        </basic-info-container>

        <forest-list-container
          v-if="id"
          headerContent="所有林情報"
          editBtnContent=" 所有林情報の追加・編集"
          addBtnContent="所有地情報を追加"
          :displayAdditionBtn="true"
          :isLoading="forestsLoading"
          :forests="forests"
          :id="id"
          @saved="fetchForests"
          :selectingForestId.sync="selectingForestId"
        />

        <customer-list-container
          v-if="id"
          class="mt-12"
          headerContent="連絡者情報"
          editBtnContent="連絡者を追加・編集"
          addBtnContent="連絡者を追加"
          :contacts="forestContacts"
          :isLoading="contactsLoading"
          :id="id"
          :customer="customer"
          @saved="fetchContacts"
          contactType="FOREST"
          :selectingForestId="selectingForestId"
          :selectingForestCustomerId="selectingForestCustomerId"
        />

        <!--        <attachment-container-->
        <!--          v-if="id"-->
        <!--          class="consultation-history mt-12"-->
        <!--          headerContent="協議履歴"-->
        <!--          editBtnContent="協議記録を追加・編集"-->
        <!--          addBtnContent="協議履歴を追加"-->
        <!--          :attaches="[]"-->
        <!--          :isLoading="false"-->
        <!--        />-->

        <customer-contacts-container
          v-if="id"
          class="mt-12"
          headerContent="家族情報"
          toggleEditBtnContent="家族を追加・編集"
          addBtnContent="連絡者を追加"
          :contacts="familyContacts"
          :isLoading="contactsLoading"
          :id="id"
          :customer="customer"
          @saved="fetchContacts"
          contactType="FAMILY"
        />

        <customer-contacts-container
          v-if="id"
          class="mt-12"
          headerContent="その他関係者情報"
          toggleEditBtnContent="その他関係者を追加・編集"
          addBtnContent="連絡者を追加"
          :contacts="otherContacts"
          :isLoading="contactsLoading"
          :id="id"
          :customer="customer"
          @saved="fetchContacts"
          contactType="OTHERS"
        />

        <forest-list-container
          class="mt-12"
          headerContent="顧客連絡者登録 森林"
          addBtnContent="所有地情報を追加"
          :displayAdditionBtn="false"
          :isLoading="false"
          :forests="[]"
          v-if="id"
        />

        <basic-info-container
          v-if="id"
          headerContent="口座情報"
          editBtnContent="口座情報を編集"
          addBtnContent="口座情報を編集"
          :isLoading="customerLoading"
          :info="bankingInfo"
          :id="id"
        >
          <template #form="props">
            <banking-info-form
              :id="id"
              :form="bankingInfoFormData"
              :toggleEditing="props.toggleEditing"
              @updated="fetchCustomer"
            />
          </template>
        </basic-info-container>
      </div>
    </template>

    <template #right v-if="isDetail">
      <div>
        <memo-input
          :api-url="`/customers/${$route.params.id}/memo`"
          :value="customer && customer.attributes['memo']"
          @input="customer.attributes['memo'] = $event"
        ></memo-input>
        <action-log
          app-name="crm"
          object-type="customer"
          :object-id="$route.params.id"
        ></action-log>
      </div>
    </template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import discussions from "../assets/dump/history_discussion.json";
import BasicInfoContainer from "../components/detail/BasicInfoContainer";
import AttachmentContainer from "../components/detail/AttachmentContainer";
import ForestListContainer from "../components/detail/ForestListContainer";
import CustomerListContainer from "../components/detail/CustomerListContainer";
import CustomerContactsContainer from "../components/detail/CustomerContactsContainer";
import ActionLog from "../components/detail/ActionLog";
import MemoInput from "../components/detail/MemoInput";
import ContactForm from "../components/forms/ContactForm";
import BankingInfoForm from "../components/forms/BankingInfoForm";
import { filter, find } from "lodash";

export default {
  mixins: [ScreenMixin],

  components: {
    MainSection,
    BasicInfoContainer,
    // AttachmentContainer,
    ForestListContainer,
    CustomerListContainer,
    CustomerContactsContainer,
    ContactForm,
    BankingInfoForm,
    ActionLog,
    MemoInput,
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
      selectingForestId: null,
      customer: null,
      customerLoading: this.checkAndShowLoading(),
      forests: [],
      forestsLoading: this.checkAndShowLoading(),
      contacts: [],
      contactsLoading: this.checkAndShowLoading(),
    };
  },

  created() {
    this.fetchInitialData();
  },

  mounted() {
    const info = {
      title: this.$t("page_header.customer_new"),
      subTitle: "",
      backUrl: "/customers",
    };
    this.$store.dispatch("setHeaderInfo", info);
  },

  methods: {
    checkAndShowLoading() {
      //only available under detail page
      return this.isDetail;
    },
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
    fetchInitialData() {
      if (this.isDetail) {
        this.fetchCustomer();
        this.fetchForests();
        this.fetchContacts();
      }
    },
    fetchCustomer() {
      this.$rest.get(`/customers/${this.id}`).then(data => {
        this.customer = data;
        this.customerLoading = false;
      });
    },
    fetchForests() {
      this.forestsLoading = true;
      this.$rest.get(`/customers/${this.id}/forests`).then(async data => {
        let forests = data.results;
        let next = data.next;
        while (!!next) {
          let nextForests = await this.$rest.get(next);
          forests.push(...nextForests.results);
          next = nextForests.next;
        }
        this.forests = forests;
        this.forestsLoading = false;
      });
    },
    fetchContacts() {
      this.contactsLoading = true;
      this.$rest.get(`/customers/${this.id}/contacts`).then(async data => {
        let contacts = data.results;
        let next = data.next;
        while (!!next) {
          let nextContacts = await this.$rest.get(next);
          contacts.push(...nextContacts.results);
          next = nextContacts.next;
        }
        this.contacts = contacts;
        this.contactsLoading = false;
      });
    },
  },

  computed: {
    isDetail() {
      return !!this.id;
    },

    forestContacts() {
      if (!this.selectingForestCustomerId)
        return filter(
          this.contacts,
          c => c.forestcustomer_id && c.cc_attrs.contact_type === "FOREST",
        );
      return filter(this.contacts, {
        forestcustomer_id: this.selectingForestCustomerId,
      });
    },

    familyContacts() {
      return filter(this.contacts, {
        cc_attrs: { contact_type: "FAMILY" },
      });
    },
    otherContacts() {
      return filter(this.contacts, {
        cc_attrs: { contact_type: "OTHERS" },
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
    selfContactFormData() {
      return {
        last_name_kanji: this.customer?.self_contact.name_kanji.last_name || "",
        first_name_kanji:
          this.customer?.self_contact.name_kanji.first_name || "",
        last_name_kana: this.customer?.self_contact.name_kana.last_name || "",
        first_name_kana: this.customer?.self_contact.name_kana.first_name || "",
        postal_code: this.customer?.self_contact.postal_code || "",
        sector: this.customer?.self_contact.address.sector || "",
        prefecture: this.customer?.self_contact.address.prefecture || "",
        municipality: this.customer?.self_contact.address.municipality || "",
        telephone: this.customer?.self_contact.telephone || "",
        mobilephone: this.customer?.self_contact.mobilephone || "",
        email: this.customer?.self_contact.email || "",
      };
    },
    bankingInfoFormData() {
      return {
        bank_name: this.customer?.banking?.bank_name || "",
        branch_name: this.customer?.banking?.branch_name || "",
        account_type: this.customer?.banking?.account_type || "",
        account_number: this.customer?.banking?.account_number || "",
        account_name: this.customer?.banking?.account_name || "",
      };
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
    selectingForestCustomerId() {
      const forest = find(this.forests, { id: this.selectingForestId });
      return forest ? forest.forestcustomer_id : null;
    },
  },

  watch: {
    $route: "fetchInitialData",
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
