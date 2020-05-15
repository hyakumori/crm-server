<template>
  <div>
    <content-header
      class="mb-4"
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      @toggleEdit="val => (isUpdate = val)"
    />
    <customer-contact-list
      :contacts="tempParticipants"
      :isUpdate="isUpdate"
      :showRelationshipSelect="false"
      @deleteContact="handleDelete"
      @undoDeleteContact="handleUndoDelete"
      :customerIdNameMap="customerIdNameMap"
    />
    <addition-button
      ref="addBtn"
      class="my-2"
      v-if="isUpdate"
      :content="addBtnContent"
      :click="() => (showSelect = true)"
    />
    <select-list-modal
      :loading="loadContacts"
      :shown.sync="showSelect"
      :submitBtnText="$t('buttons.add')"
      submitBtnIcon="mdi-plus"
      :handleSubmitClick="handleAdd"
      @needToLoad="handleLoadMore"
      @search="debounceLoadInitContactsForAdding"
    >
      <template #list>
        <div
          v-if="contactsForAdding.results.length === 0 && !loadContacts"
          class="text-center"
        >
          {{ $t("messages.not_found") }}
        </div>
        <customer-contact-card
          v-else
          @click="
            (cId, inx) => {
              modalSelectingContactId = cId;
              modalSelectingContactIndex = inx;
            }
          "
          v-for="(item, indx) in contactsForAdding.results"
          :key="`${indx},${item.id}`"
          :card_id="item.id"
          :contact="item"
          :showAction="false"
          :index="indx"
          :selectedId="modalSelectingContactId"
          :selectedIndex="modalSelectingContactIndex"
          flat
          clickable
          mode="search"
          :showRelationshipSelect="false"
          :customerName="renderCustomerName(item)"
        />
      </template>
    </select-list-modal>
    <update-button
      v-if="isUpdate"
      :cancel="() => (isUpdate = !isUpdate)"
      :save="handleSave"
      :saving="saving"
      :saveDisabled="saveDisabled"
    />
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import UpdateButton from "./UpdateButton";
import CustomerContactList from "./CustomerContactList";
import CustomerContactCard from "./CustomerContactCard";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import { debounce, reject } from "lodash";

export default {
  name: "archive-participant-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    UpdateButton,
    AdditionButton,
    SelectListModal,
    CustomerContactList,
    CustomerContactCard,
  },
  props: {
    id: { type: String },
    participants: { type: Array, default: () => [] },
  },
  created() {
    this.debounceLoadInitContactsForAdding = debounce(
      this.loadInitContacts,
      500,
    );
  },
  data() {
    return {
      isUpdate: false,
      loadContacts: false,
      contactsForAdding: { results: [] },
      saving: false,
      modalSelectingContactId: null,
      modalSelectingContactIndex: null,
      showSelect: false,
      contactsToAdd: [],
      contactsToDelete: [],
      selectingContactId: null,
      selectingCustomerId: null,
      customerIdNameMap: {},
    };
  },
  computed: {
    tempParticipants() {
      return [...this.participants, ...this.contactsToAdd];
    },
    saveDisabled() {
      return (
        this.contactsToAdd.length === 0 && this.contactsToDelete.length === 0
      );
    },
    contactsToAddData() {
      return this.contactsToAdd.map(c => ({
        contact_id: c.id,
        customer_id: c.customer_id,
      }));
    },
    contactsToDeleteData() {
      return this.contactsToDelete.map(c => ({
        contact_id: c.id,
        customer_id: c.customer_id,
      }));
    },
    contactIdsMap() {
      return Object.fromEntries(
        this.tempParticipants.map(c => [`${c.id},${c.customer_id}`, true]),
      );
    },
  },
  methods: {
    renderCustomerName(item) {
      return (
        (!item.is_basic &&
          item.customer_name_kanji &&
          `${item.customer_name_kanji.last_name} ${item.customer_name_kanji.first_name}`) ||
        ""
      );
    },
    handleContactCardSelect(contact_id, indx) {
      const contact = this.tempParticipants[indx];
      if (contact.is_basic && this.selectingContactId != contact_id) {
        this.selectingContactId = contact_id;
        this.selectingCustomerId = contact.customer_id;
      } else {
        this.selectingContactId = null;
        this.selectingCustomerId = null;
      }
    },
    async handleSave() {
      try {
        this.saving = true;
        await this.$rest.put(`/archives/${this.id}/customers`, {
          added: this.contactsToAddData,
          deleted: this.contactsToDeleteData,
        });
        this.$emit("saved");
        this.saving = false;
        this.contactsToDelete = [];
        this.contactsToAdd = [];
        this.contactsForAdding = { results: [] };
      } catch (error) {
        this.saving = false;
      }
    },
    async handleAdd() {
      const item = this.contactsForAdding.results.splice(
        this.modalSelectingContactIndex,
        1,
      )[0];
      this.$set(
        this.customerIdNameMap,
        item.customer_id,
        item.customer_name_kanji,
      );
      item.added = true;
      if (this.selectingCustomerId) {
        item.customer_id = this.selectingCustomerId;
      }
      this.contactsToAdd.push(item);
      this.modalSelectingContactIndex = null;
      this.modalSelectingContactId = null;
      // side-effect
      if (this.contactsForAdding.results.length <= 3) {
        this.handleLoadMore();
      }
    },
    handleDelete(contact) {
      if (contact.added) {
        delete contact.added;
        this.contactsToAdd = reject(this.contactsToAdd, {
          id: contact.id,
          customer_id: contact.customer_id,
        });
        this.contactsForAdding = { results: [] };
      } else {
        this.$set(contact, "deleted", true);
        this.contactsToDelete.push(contact);
      }
    },
    handleUndoDelete(contact) {
      this.$set(contact, "deleted", undefined);
      this.contactsToDelete = reject(this.contactsToDelete, {
        id: contact.id,
        customer_id: contact.customer_id,
      });
    },
    async handleLoadMore() {
      if (!this.contactsForAdding.next || this.loadContacts) return;
      this.loadContacts = true;
      const resp = await this.$rest.get(this.contactsForAdding.next);
      this.contactsForAdding = {
        next: resp.next,
        previous: resp.previous,
        results: [
          ...this.contactsForAdding.results,
          ...reject(
            resp.results,
            c => !!this.contactIdsMap[`${c.id},${c.customer_id}`],
          ),
        ],
      };
      this.loadContacts = false;
    },
    async loadInitContacts(keyword) {
      let reqConfig = keyword
        ? {
            params: {
              search: keyword || "",
            },
          }
        : {};
      this.loadContacts = true;
      let resp = { next: "/customercontacts" };
      while (resp.next) {
        resp = await this.$rest.get(resp.next, reqConfig);
        this.contactsForAdding = {
          next: resp.next,
          previous: resp.previous,
          results: reject(
            resp.results,
            c => !!this.contactIdsMap[`${c.id},${c.customer_id}`],
          ),
        };
        if (this.contactsForAdding.results.length > 5) break;
        if (resp.next && resp.next.indexOf("page=") > -1) reqConfig = {};
      }
      this.loadContacts = false;
    },
  },
  watch: {
    showSelect(val) {
      if (val && !this.contactsForAdding.next) {
        this.loadInitContacts();
      }
    },
    isUpdate(val) {
      if (!val) {
        if (this.contactsToAdd.length > 0) {
          this.contactsToAdd = [];
          this.contactsForAdding = { results: [] };
        }
        for (let contactToDelete of this.contactsToDelete) {
          this.$set(contactToDelete, "deleted", undefined);
        }
        if (this.contactsToDelete.length > 0) {
          this.contactsToDelete = [];
          this.contactsForAdding = { results: [] };
        }
      }
    },
    participants(val) {
      const customerIdNameMap = {};
      for (let c of val) {
        customerIdNameMap[c.customer_id] = c.customer_name_kanji;
      }
      this.customerIdNameMap = customerIdNameMap;
    },
  },
};
</script>
