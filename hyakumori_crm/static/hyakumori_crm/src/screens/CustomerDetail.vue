<template>
  <main-section class="customer-detail">
    <template #section>
      <div class="customer-detail__section px-7">
        <basic-info-container
          headerContent="顧客情報"
          toggleEditBtnContent="追加・編集"
          :displayAdditionBtn="isDetail"
          :isLoading="customerLoading"
          :info="basicInfo"
          :id="pk"
          :businessId="id"
        >
          <template #form="props">
            <contact-form
              :id="pk"
              :formData="selfContactFormData"
              :toggleEditing="props.toggleEditing"
              :showCancel="isDetail"
              @updated="fetchCustomer"
            />
          </template>
        </basic-info-container>

        <forest-list-container
          v-if="pk"
          headerContent="所有林情報"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :displayAdditionBtn="true"
          :isLoading="forestsLoading"
          :forests="forests"
          :id="pk"
          @saved="handleForestsSaved"
          :selectingForestId.sync="selectingForestId"
          itemClickable
        />

        <map-container
          v-if="forests.length > 0"
          style="margin-top: -20px; margin-bottom: 62px"
          :forests="forests"
        >
        </map-container>

        <customer-list-container
          v-if="pk"
          class="mt-12"
          headerContent="連絡者情報"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :contacts="forestContacts"
          :isLoading="contactsLoading"
          :id="pk"
          :customer="customer"
          @saved="handleForestContactsSave"
          contactType="FOREST"
          :selectingForestId="selectingForestId"
          :selectingForestCustomerId="selectingForestCustomerId"
        />

        <attachment-container
          v-if="pk"
          class="consultation-history mt-12"
          headerContent="協議履歴"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :archives="archives"
          :isLoading="archivesLoading"
        />

        <attachment-container
          v-if="pk"
          v-acl-only="['manage_postalhistory', 'view_postalhistory']"
          class="postal-histories mt-12"
          headerContent="書類郵送記録"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :archives="postalHistories"
          routeName="postalHistoryDetail"
        />

        <customer-contacts-container
          v-if="id"
          class="mt-12"
          headerContent="家族情報"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :contacts="familyContacts"
          :isLoading="contactsLoading"
          :id="pk"
          :customer="customer"
          @saved="fetchContacts"
          contactType="FAMILY"
        />

        <customer-contacts-container
          v-if="pk"
          class="mt-12"
          headerContent="その他関係者情報"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :contacts="otherContacts"
          :isLoading="contactsLoading"
          :id="pk"
          :customer="customer"
          @saved="fetchContacts"
          contactType="OTHERS"
        />

        <forest-list-container
          class="mt-12"
          headerContent="顧客連絡者登録 森林"
          addBtnContent="追加"
          :displayAdditionBtn="false"
          :isLoading="contactsForestsLoading"
          :forests="contactsForests"
          v-if="pk"
          :itemClickable="false"
        />

        <basic-info-container
          v-if="pk"
          class="mt-12"
          headerContent="口座情報"
          toggleEditBtnContent="編集"
          addBtnContent="口座情報を編集"
          :isLoading="customerLoading"
          :info="bankingInfo"
          :businessId="id"
          :id="pk"
        >
          <template #form="props">
            <banking-info-form
              :id="pk"
              :formData="bankingInfoFormData"
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
          :api-url="`/customers/${pk}/memo`"
          object-type="customer"
          v-model="customer"
          v-if="pk"
        ></memo-input>
        <tag-detail-card
          class="ml-6 mb-6"
          app-name="crm"
          object-type="customer"
          :object-id="pk"
          :tags="customer && customer.tags"
          @input="customer.tags = $event"
          title="顧客タグ情報"
        ></tag-detail-card>
        <div class="mb-6" v-if="taggedForests.length > 0">
          <h4 class="ml-6">森林タグ情報</h4>
          <div style="overflow-y:auto;">
            <tag-detail-card
              class="ml-6"
              v-for="f in taggedForests"
              :key="f.id"
              app-name="crm"
              object-type="forest"
              :tags="f.tags"
              :editable="false"
            >
              <h5 class="my-2">
                {{ getForestDisplayName(f) }}
              </h5>
            </tag-detail-card>
          </div>
        </div>
        <action-log
          v-if="pk"
          app-name="crm"
          object-type="customer"
          :object-id="pk"
        ></action-log>
      </div>
    </template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import BasicInfoContainer from "../components/detail/BasicInfoContainer";
import AttachmentContainer from "../components/detail/AttachmentContainer";
import ForestListContainer from "../components/detail/ForestListContainer";
import CustomerListContainer from "../components/detail/CustomerListContainer";
import CustomerContactsContainer from "../components/detail/CustomerContactsContainer";
import ActionLog from "../components/detail/ActionLog";
import MemoInput from "../components/detail/MemoInput";
import TagDetailCard from "../components/tags/TagDetailCard";
import ContactForm from "../components/forms/ContactForm";
import BankingInfoForm from "../components/forms/BankingInfoForm";
import { filter, find, some } from "lodash";
import { tags_to_array } from "../helpers/tags";
import { getForestDisplayName } from "../helpers/forest";
import MapContainer from "../components/MapContainer";

export default {
  mixins: [ScreenMixin],

  components: {
    MainSection,
    BasicInfoContainer,
    AttachmentContainer,
    ForestListContainer,
    CustomerListContainer,
    CustomerContactsContainer,
    ContactForm,
    BankingInfoForm,
    ActionLog,
    MemoInput,
    TagDetailCard,
    MapContainer,
  },
  props: ["id"],
  data() {
    return {
      headerInfo: {
        title: "",
        desc: "",
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
      archives: [],
      archivesLoading: this.checkAndShowLoading(),
      postalHistories: [],
      postalHistoriesLoading: this.checkAndShowLoading(),
      contactsForests: [],
      contactsForestsLoading: this.checkAndShowLoading(),
    };
  },

  async created() {
    await this.fetchInitialData();
  },

  mounted() {
    let info = {};
    if (!this.isDetail) {
      info = {
        title: this.$t("page_header.customer_new"),
        subTitle: "",
        backUrl: "/customers",
      };
    } else {
      info = {
        title: this.$t("page_header.customer_mgmt"),
        subTitle: "",
        backUrl: "/customers",
      };
    }

    this.$store.dispatch("setHeaderInfo", info);
  },

  methods: {
    getForestDisplayName,
    async resolveBusinessId() {
      if (!this.isDetail) {
        return;
      }
      try {
        const customer = await this.$rest.get("/customers/by-business-id", {
          params: { business_id: this.id },
        });
        if (customer && customer.business_id && customer.id) {
          this.customer = customer;
        } else {
          this.$router.replace({ name: "not-found" });
        }
      } catch {
        this.$router.replace({ name: "not-found" });
      }
    },
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
    async fetchInitialData() {
      if (this.isDetail) {
        await this.resolveBusinessId();
        this.fetchForests();
        this.fetchContacts();
        this.fetchArchives();
        this.fetchPostalHistories();
        this.fetchContactsForests();
      }
    },
    fetchCustomer() {
      this.$rest.get(`/customers/${this.pk}`).then(data => {
        this.customer = data;
        this.customerLoading = false;
      });
    },
    fetchForests() {
      this.forestsLoading = true;
      this.$rest.get(`/customers/${this.pk}/forests`).then(async data => {
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
      this.$rest.get(`/customers/${this.pk}/contacts`).then(async data => {
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
    async fetchArchives() {
      this.archivesLoading = true;
      this.archives = await this.$rest.get(`/customers/${this.pk}/archives`);
      this.archivesLoading = false;
    },
    async fetchPostalHistories() {
      this.postalHistoriesLoading = true;
      this.postalHistories = await this.$rest.get(
        `/customers/${this.pk}/postal-histories`,
      );
      this.postalHistoriesLoading = false;
    },
    async fetchContactsForests() {
      this.contactsForestsLoading = true;
      this.contactsForests = await this.$rest.get(
        `/customers/${this.pk}/contacts-forests`,
      );
      this.contactsForestsLoading = false;
    },
    handleForestContactsSave() {
      this.fetchContacts();
      this.fetchContactsForests();
    },
    handleForestsSaved() {
      this.fetchForests();
      this.fetchContacts();
      this.fetchContactsForests();
    },
  },

  computed: {
    pk() {
      return this.customer && this.customer.id;
    },

    isDetail() {
      return !!this.id;
    },

    forestContacts() {
      if (!this.selectingForestCustomerId)
        return filter(this.contacts, c => c.forestcustomer_id);
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
        account_designator: this.customer?.banking?.account_designator || "",
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
          value:
            (this.customer?.self_contact.address.prefecture || "") +
            " " +
            (this.customer?.self_contact.address.municipality || "") +
            " " +
            (this.customer?.self_contact.address.sector || ""),
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
          value: this.customer?.banking?.account_designator || "",
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
    taggedForests() {
      if (this.forests.length === 0) return [];
      return this.forests.filter(f => some(Object.values(f.tags), Boolean));
    },
  },

  watch: {
    $route: "fetchInitialData",
    customer: {
      deep: true,
      handler: function() {
        this.headerInfo = {
          ...this.headerInfo,
          title: this.getPersonFullname(this.customer?.self_contact.name_kanji),
          desc: this.customer.business_id,
          tags: tags_to_array(this.customer?.tags),
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
