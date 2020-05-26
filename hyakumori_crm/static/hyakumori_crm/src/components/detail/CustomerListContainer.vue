<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      @toggleEdit="val => (isEditing = val)"
      :displayAdditionBtn="
        (contactType === 'FOREST' && !!selectingForestCustomerId) ||
          contactType !== 'FOREST'
      "
    />

    <customer-contact-list
      class="mt-4"
      :contacts="tempContacts"
      :isUpdate="isEditing"
      isContactor
      @deleteContact="handleDelete"
      @undoDeleteContact="handleUndoDelete"
      @relationshipChange="handleRelationshipChange"
    />
    <addition-button
      class="my-2"
      v-if="isEditing"
      :content="addBtnContent"
      :click="() => (showSelect = true)"
    />
    <SelectListModal
      :loading="itemsForAddingLoading"
      :shown.sync="showSelect"
      :submitBtnText="$t('buttons.add')"
      submitBtnIcon="mdi-plus"
      :handleSubmitClick="handleAdd"
      @needToLoad="handleLoadMore"
      @search="debounceLoadInitItemsForAdding"
      ref="selectListModal"
    >
      <template #list>
        <CustomerContactCard
          @click="
            (fId, inx) => {
              modalSelectingId = fId;
              modalSelectingIndex = inx;
            }
          "
          v-for="(item, indx) in itemsForAdding.results || []"
          :key="item.id"
          :contact="item"
          :isOwner="item.is_basic"
          :showAction="false"
          :index="indx"
          :selectedId="modalSelectingId"
          :selectedIndex="modalSelectingIndex"
          flat
          mode="search"
          clickable
        />
      </template>
    </SelectListModal>
    <update-button
      v-if="isEditing"
      :cancel="cancel"
      :save="handleSave"
      :saving="saving"
      :saveDisabled="saveDisabled"
    />
  </div>
</template>

<script>
import ContainerMixin from "./ContainerMixin";
import SelectListModalMixin from "./SelectListModalMixin";
import ContentHeader from "./ContentHeader";
import CustomerContactList from "./CustomerContactList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import CustomerContactCard from "../detail/CustomerContactCard";
import { reject, debounce, find, cloneDeep } from "lodash";

export default {
  name: "customer-list-container",

  mixins: [ContainerMixin, SelectListModalMixin],

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
  data() {
    return {
      selectingContactId: null,
      contactsToAdd: [],
      contactsToDelete: [],
      relationshipChanges: [],
      contacts_: [],
      itemsForAddingUrl: "/contacts",
    };
  },
  computed: {
    tempContacts() {
      return [...this.contacts_, ...this.contactsToAdd];
    },
    contactIdsMap() {
      return Object.fromEntries(this.tempContacts.map(c => [c.id, true]));
    },
    contactsAddData() {
      return [...this.contactsToAdd, ...this.relationshipChanges].map(c => ({
        contact: c.id,
        forest_id: c.forest_id,
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
    itemsForAddingResultFilter(c) {
      return (
        !!this.contactIdsMap[c.id] || c.id === this.customer.self_contact.id
      );
    },
    handleRelationshipChange(contact_id, val) {
      const contactItem = find(this.tempContacts, { id: contact_id });
      contactItem.relationship_type = val;
      const others = reject(this.relationshipChanges, { id: contact_id });
      this.relationshipChanges = [...others, contactItem];
    },
    handleAdd() {
      const contactItem = this.itemsForAdding.results.splice(
        this.modalSelectingIndex,
        1,
      )[0];
      if (contactItem) {
        contactItem.added = true;
        contactItem.forest_id = this.selectingForestId;
        contactItem.forestcustomer_id = this.selectingForestCustomerId;
        contactItem.contact_type = this.contactType;
        this.contactsToAdd.push(contactItem);
        this.modalSelectingIndex = null;
        this.modalSelectingForestId = null;
        if (this.itemsForAdding.results.length <= 3) this.handleLoadMore();
      }
    },
    handleDelete(contact, index) {
      if (contact.added) {
        delete contact.added;
        this.contactsToAdd = reject(this.contactsToAdd, { id: contact.id });
        this.itemsForAdding = { results: [] };
      } else {
        this.$set(contact, "deleted", true);
        this.$set(contact, "relationship_type", undefined);
        this.$set(this.contacts, index, contact);
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
          contact_type: this.contactType || "FOREST",
        });
        this.$emit("saved");
        this.saving = false;
        this.contactsToDelete = [];
        this.contactsToAdd = [];
        this.relationshipChanges = [];
        this.itemsForAdding = { results: [] };
      } catch (error) {
        this.saving = false;
      }
    },
  },
  watch: {
    contacts: {
      deep: true,
      handler(val) {
        this.contacts_ = cloneDeep(val);
      },
    },
    isEditing(val) {
      if (!val) {
        if (this.contactsToAdd.length > 0) {
          this.contactsToAdd = [];
          this.itemsForAdding = { results: [] };
        }
        for (let contactToDelete of this.contactsToDelete) {
          this.$set(contactToDelete, "deleted", undefined);
        }
        if (this.contactsToDelete) {
          this.contactsToDelete = [];
          this.itemsForAdding = { results: [] };
        }
        this.relationshipChanges = [];
      }
    },
    selectingForestCustomerId(val) {
      if (this.contactType === "FOREST" && !val) this.isEditing = false;
    },
  },
};
</script>
