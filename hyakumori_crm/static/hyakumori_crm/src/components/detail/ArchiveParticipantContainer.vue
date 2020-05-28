<template>
  <div>
    <content-header
      class="mb-4"
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :loading="isLoading"
      @toggleEdit="val => (isEditing = val)"
    />
    <customer-contact-list
      :contacts="tempParticipants"
      :isUpdate="isEditing"
      :showRelationshipSelect="false"
      @deleteContact="handleDelete"
      @undoDeleteContact="handleUndoDelete"
      :customerIdNameMap="customerIdNameMap"
      isContactor
    />
    <addition-button
      ref="addBtn"
      class="my-2"
      v-if="isEditing"
      :content="addBtnContent"
      :click="() => (showSelect = true)"
    />
    <select-list-modal
      :loading="itemsForAddingLoading"
      :shown.sync="showSelect"
      :submitBtnText="$t('buttons.add')"
      submitBtnIcon="mdi-plus"
      :handleSubmitClick="handleAdd"
      :handleCancelClick="onCancel"
      :disableAdditionBtn="!modalSelectingId"
      @needToLoad="handleLoadMore"
      @search="debounceLoadInitItemsForAdding"
      ref="selectListModal"
    >
      <template #list>
        <div
          v-if="itemsForAdding.results.length === 0 && !itemsForAddingLoading"
          class="text-center"
        >
          {{ $t("messages.not_found") }}
        </div>
        <customer-contact-card
          v-else
          @click="
            (cId, inx) => {
              modalSelectingId = cId;
              modalSelectingIndex = inx;
            }
          "
          v-for="(item, indx) in itemsForAdding.results"
          :key="`${indx},${item.id}`"
          :card_id="item.id"
          :contact="item"
          :showAction="false"
          :index="indx"
          :selectedId="modalSelectingId"
          :selectedIndex="modalSelectingIndex"
          flat
          clickable
          mode="search"
          :showRelationshipSelect="false"
          :customerName="renderCustomerName(item)"
        />
      </template>
    </select-list-modal>
    <update-button
      v-if="isEditing"
      :cancel="() => (isEditing = !isEditing)"
      :save="handleSave"
      :saving="saving"
      :saveDisabled="saveDisabled"
    />
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import SelectListModalMixin from "./SelectListModalMixin";
import UpdateButton from "./UpdateButton";
import CustomerContactList from "./CustomerContactList";
import CustomerContactCard from "./CustomerContactCard";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import { reject } from "lodash";

export default {
  name: "archive-participant-container",

  mixins: [ContainerMixin, SelectListModalMixin],

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
  data() {
    return {
      contactsToAdd: [],
      contactsToDelete: [],
      selectingContactId: null,
      selectingCustomerId: null,
      customerIdNameMap: {},
      itemsForAddingUrl: "/customercontacts",
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
    itemsForAddingResultFilter(c) {
      return !!this.contactIdsMap[`${c.id},${c.customer_id}`];
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
        this.itemsForAdding = { results: [] };
      } catch (error) {
        this.saving = false;
      }
    },
    async handleAdd() {
      const item = this.itemsForAdding.results.splice(
        this.modalSelectingIndex,
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
      this.modalSelectingIndex = null;
      this.modalSelectingId = null;
      // side-effect
      if (this.itemsForAdding.results.length <= 3) {
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
        this.itemsForAdding = { results: [] };
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
  },
  watch: {
    isEditing(val) {
      if (!val) {
        if (this.contactsToAdd.length > 0) {
          this.contactsToAdd = [];
          this.itemsForAdding = { results: [] };
        }
        for (let contactToDelete of this.contactsToDelete) {
          this.$set(contactToDelete, "deleted", undefined);
        }
        if (this.contactsToDelete.length > 0) {
          this.contactsToDelete = [];
          this.itemsForAdding = { results: [] };
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
