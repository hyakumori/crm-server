<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :update="isUpdate"
      @toggleEdit="val => (isUpdate = val)"
      :displayAdditionBtn="
        (contactType === 'FOREST' && !!selectingForestCustomerId) ||
          contactType !== 'FOREST'
      "
    />

    <customer-contact-list
      class="mt-4"
      :contacts="tempContacts"
      :isUpdate="isUpdate"
      isContactor
      @deleteContact="handleDelete"
      @undoDeleteContact="handleUndoDelete"
      @relationshipChange="handleRelationshipChange"
    />
    <addition-button
      class="my-2"
      v-if="isUpdate"
      :content="addBtnContent"
      :click="() => (showSelect = true)"
    />
    <SelectListModal
      :loading="loadContacts"
      :shown.sync="showSelect"
      :submitBtnText="$t('buttons.add')"
      submitBtnIcon="mdi-plus"
      :handleSubmitClick="handleAdd"
      @needToLoad="handleLoadMore"
      @search="debounceLoadInitContacts"
    >
      <template #list>
        <CustomerContactCard
          @click="
            (fId, inx) => {
              modalSelectingContactId = fId;
              modalSelectingContactIndex = inx;
            }
          "
          v-for="(item, indx) in contactitems.results || []"
          :key="item.id"
          :card_id="item.id"
          :contact="item"
          :isOwner="item.is_basic"
          :showAction="false"
          :index="indx"
          :selectedId="modalSelectingContactId"
          :selectedIndex="modalSelectingContactIndex"
          flat
          mode="search"
        />
      </template>
    </SelectListModal>
    <update-button
      v-if="isUpdate"
      :cancel="cancel"
      :save="handleSave"
      :saving="saving"
      :saveDisabled="saveDisabled"
    />
  </div>
</template>

<script>
import ContainerMixin from "./ContainerMixin";
import ContentHeader from "./ContentHeader";
import CustomerContactList from "./CustomerContactList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import CustomerContactCard from "../detail/CustomerContactCard";
import { reject, debounce, find } from "lodash";

export default {
  name: "customer-list-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    CustomerContactList,
    UpdateButton,
    AdditionButton,
    CustomerContactCard,
    SelectListModal,
  },

  props: {
    contacts: Array,
    selectingForestId: { type: String, default: null },
    selectingForestCustomerId: { type: String, default: null },
    id: String,
    customer: Object,
    contactType: String,
  },
  created() {
    this.debounceLoadInitContacts = debounce(this.loadInitContacts, 500);
  },
  data() {
    return {
      isUpdate: false,
      showSelect: false,
      loadContacts: false,
      contactitems: {},
      selectingContactId: null,
      modalSelectingContactId: null,
      modalSelectingContactIndex: null,
      contactsToAdd: [],
      contactsToDelete: [],
      saving: false,
      relationshipChanges: [],
    };
  },
  computed: {
    tempContacts() {
      return [...this.contacts, ...this.contactsToAdd];
    },
    contactIdsMap() {
      return Object.fromEntries(this.tempContacts.map(c => [c.id, true]));
    },
    contactsAddData() {
      return [...this.contactsToAdd, ...this.relationshipChanges].map(c => ({
        contact: c.id,
        forest_id: c.forest_id,
        contact_type: c.contact_type || "FOREST",
        relationship_type: c.relationship_type,
      }));
    },
    contactIdsToDelete() {
      return this.contactsToDelete.map(f => f.id);
    },
    saveDisabled() {
      return (
        this.contactIdsToDelete.length === 0 &&
        this.contactsAddData.length === 0
      );
    },
  },
  methods: {
    handleRelationshipChange(contact_id, val) {
      const contactItem = find(this.tempContacts, { id: contact_id });
      contactItem.relationship_type = val;
      if (!contactItem.added) {
        const others = reject(this.relationshipChanges, { id: contact_id });
        this.relationshipChanges = [...others, contactItem];
      }
    },
    handleAdd() {
      const contactItem = this.contactitems.results.splice(
        this.modalSelectingContactIndex,
        1,
      )[0];
      if (contactItem) {
        contactItem.added = true;
        contactItem.forest_id = this.selectingForestId;
        contactItem.forestcustomer_id = this.selectingForestCustomerId;
        contactItem.contact_type = this.contactType;
        this.contactsToAdd.push(contactItem);
        this.modalSelectingContactIndex = null;
        this.modalSelectingForestId = null;
      }
    },
    handleDelete(contact) {
      if (contact.added) {
        delete contact.added;
        this.contactsToAdd = reject(this.contactsToAdd, { id: contact.id });
        this.contactitems = { results: [] };
      } else {
        this.$set(contact, "deleted", true);
        this.$set(contact, "relationship_type", undefined);
        this.relationshipChanges = reject(this.relationshipChanges, {
          id: contact.id,
        });
        this.contactsToDelete.push(contact);
      }
    },
    handleUndoDelete(contact) {
      this.$set(contact, "deleted", undefined);
      this.contactsToDelete = reject(this.contactsToDelete, { id: contact.id });
    },
    async handleSave() {
      try {
        this.saving = true;
        await this.$rest.put(`/customers/${this.id}/contacts`, {
          adding: this.contactsAddData,
          deleting: this.contactIdsToDelete,
        });
        this.$emit("saved");
        this.saving = false;
        this.contactsToDelete = [];
        this.contactsToAdd = [];
        this.relationshipChanges = [];
        this.contactitems = { results: [] };
      } catch (error) {}
    },
    async handleLoadMore() {
      if (!this.contactitems.next || this.loadContacts) return;
      this.loadContacts = true;
      const resp = await this.$rest.get(this.contactitems.next);
      this.contactitems = {
        next: resp.next,
        previous: resp.previous,
        results: [
          ...this.contactitems.results,
          ...reject(
            resp.results,
            f =>
              !!this.contactIdsMap[f.id] ||
              f.id === this.customer.self_contact.id,
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
      let resp = { next: "/contacts" };
      while (resp.next) {
        resp = await this.$rest.get(resp.next, reqConfig);
        this.contactitems = {
          next: resp.next,
          previous: resp.previous,
          results: reject(
            resp.results,
            f =>
              !!this.contactIdsMap[f.id] ||
              f.id === this.customer.self_contact.id,
          ),
        };
        if (this.contactitems.results.length > 5) break;
        if (resp.next && resp.next.indexOf("page=") > -1) reqConfig = {};
      }
      this.loadContacts = false;
    },
  },
  watch: {
    async showSelect(val) {
      if (val && !this.contactitems.next) {
        await this.loadInitContacts("");
      }
    },
    isUpdate(val) {
      if (!val) {
        if (this.contactsToAdd.length > 0) {
          this.contactsToAdd = [];
          this.contactitems = { results: [] };
        }
        for (let contactToDelete of this.contactsToDelete) {
          this.$set(contactToDelete, "deleted", undefined);
        }
        if (this.contactsToDelete) {
          this.contactsToDelete = [];
          this.contactitems = { results: [] };
        }
        this.relationshipChanges = [];
      }
    },
    selectingForestCustomerId(val) {
      if (this.contactType === "FOREST" && !val) this.isUpdate = false;
    },
  },
};
</script>
