<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :update="isUpdate"
      :loading="isLoading"
      @update="val => (isUpdate = val)"
    />

    <customer-contact-list
      class="mt-4"
      :contacts="tempContacts"
      :isUpdate="isUpdate"
      @deleteContact="handleDelete"
      @undoDeleteContact="handleUndoDelete"
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
          @selected="
            (fId, inx) => {
              modalSelectingContactId = fId;
              modalSelectingContactIndex = inx;
            }
          "
          v-for="(item, indx) in contactitems.results || []"
          :key="item.id"
          :card_id="item.id"
          :fullname="
            `${item.name_kanji.last_name} ${item.name_kanji.first_name}`
          "
          :address="item.address.sector"
          :email="item.email"
          :forestCount="item.forest_count"
          :phone="item.telephone"
          :cellphone="item.mobilephone"
          :isOwner="item.is_basic"
          :showAction="false"
          :index="indx"
          :selectedId="modalSelectingContactId"
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
import { reject, debounce } from "lodash";

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
    };
  },
  computed: {
    tempContacts() {
      return [...this.contacts, ...this.contactsToAdd];
    },
    contactIdsMap() {
      return Object.fromEntries(this.tempContacts.map(f => [f.id, true]));
    },
    contactIdsToAdd() {
      return this.contactsToAdd.map(f => f.id);
    },
    contactsAddData() {
      return this.contactsToAdd.map(f => ({
        contact: f.id,
        forest_id: f.forest_id,
        contact_type: f.contact_type,
      }));
    },
    contactIdsToDelete() {
      return this.contactsToDelete.map(f => f.id);
    },
    saveDisabled() {
      return (
        this.contactIdsToDelete.length === 0 &&
        this.contactIdsToAdd.length === 0
      );
    },
  },
  methods: {
    handleAdd() {
      const contactItem = this.contactitems.results.splice(
        this.modalSelectingContactIndex,
        1,
      )[0];
      if (contactItem) {
        contactItem.added = true;
        contactItem.forest_id = this.selectingForestId;
        contactItem.contact_type = this.contactType;
        this.contactsToAdd.push(contactItem);
        this.modalSelectingContactIndex = null;
        this.modalSelectingForestId = null;
      }
    },
    handleDelete(contact) {
      if (contact.added) {
        delete contact.added;
        // delete contactItem.forest_id;
        // delete contactItem.contact_type;
        this.contactsToAdd = reject(this.contactsToAdd, { id: contact.id });
      } else {
        this.$set(contact, "deleted", true);
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
      } catch (error) {}
    },
    async handleLoadMore() {
      if (!this.contactitems.next) return;
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
      this.loadContacts = true;
      const resp = await this.$rest.get("/contacts", {
        params: {
          search: keyword,
        },
      });
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
        this.contactsToAdd.length > 0 && (this.contactsToAdd = []);
        for (let contactToDelete of this.contactsToDelete) {
          this.$set(contactToDelete, "deleted", undefined);
        }
        this.contactsToDelete && (this.contactsToDelete = []);
      }
    },
  },
};
</script>
