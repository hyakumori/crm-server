<template>
  <section-container-wrapper
    :headerContent="headerContent"
    :toggleEditBtnContent="toggleEditBtnContent"
    :addBtnContent="addBtnContent"
    :isLoading="isLoading"
    :permissions="['manage_customer']"
    :isEditing="isEditing"
    @toggleEdit="val => (isEditing = val)"
    :cancelEdit="handleCancelEdit"
    :addBtnClickHandler="
      () => {
        showNewContactDialog = true;
      }
    "
    :saveDisabled="saveDisabled"
    :save="handleSave"
    :saving="saving"
  >
    <template>
      <customer-contact-list
        class="mt-4"
        :contacts="tempContacts"
        :isUpdate="isEditing"
        :isContactor="true"
        @deleteContact="handleDelete"
        @undoDeleteContact="handleUndoDelete"
        @relationshipChange="handleRelationshipChange"
      />
      <v-dialog v-model="showNewContactDialog" scrollable max-width="720">
        <v-card>
          <v-card-actions class="px-6 py-4">
            <v-card-title class="pa-0">{{
              $t("forms.titles.create_contact")
            }}</v-card-title>
            <v-spacer />
            <v-icon @click="showNewContactDialog = false">mdi-close</v-icon>
          </v-card-actions>
          <v-divider></v-divider>
          <v-card-text style="min-height: 300px;" class="px-6 py-5">
            <contact-form
              :formData.sync="form"
              :handleSubmit="handleAdd"
              :errors="formErrors"
            />
          </v-card-text>
        </v-card>
      </v-dialog>
    </template>
  </section-container-wrapper>
</template>

<script>
import SectionContainerWrapper from "../SectionContainerWrapper";
import CustomerContactList from "./CustomerContactList";
import ContainerMixin from "./ContainerMixin";
import ContactForm from "../forms/ContactForm";

import { reject, cloneDeep } from "lodash";

export default {
  mixins: [ContainerMixin],

  components: {
    SectionContainerWrapper,
    CustomerContactList,
    ContactForm,
  },

  props: {
    contacts: Array,
    permissions: Array,
    id: String,
    contactIdNameMap: Object,
    contactType: String,
  },
  data() {
    return {
      showNewContactDialog: false,
      contactsToDelete: [],
      defaultContactsEdit: {},
      defaultContactsContactsEdit: {},
      form: this.initForm(),
      formErrors: {},
      relationshipChanges: [],
      contacts_: [],
    };
  },
  computed: {
    tempContacts() {
      return [...this.contacts_];
    },
    contactIdsToDelete() {
      return this.contactsToDelete.map(c => c.id);
    },
    saveDisabled() {
      return (
        this.contactIdsToDelete.length === 0 &&
        this.relationshipChanges.length === 0
      );
    },
    contactsAddData() {
      return this.relationshipChanges.map(i => ({
        contact: i.contact,
        relationship_type: i.val,
      }));
    },
  },
  methods: {
    handleCancelEdit() {
      this.isEditing = false;
      this.form = this.initForm();
      this.formErrors = {};
    },
    handleRelationshipChange(contact_id, val) {
      const others = reject(this.relationshipChanges, {
        contact: contact_id,
      });
      this.relationshipChanges = [...others, { contact: contact_id, val }];
    },
    handleDelete(contact) {
      if (contact.added) {
        delete contact.added;
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
          contact_type: this.contactType,
        });
        this.$emit("saved");
        this.saving = false;
        this.contactsToDelete = [];
        this.relationshipChanges = [];
      } catch (error) {
        this.saving = false;
      }
    },
    initForm() {
      return {
        last_name_kanji: "",
        first_name_kanji: "",
        last_name_kana: "",
        first_name_kana: "",
        postal_code: "",
        sector: "",
        prefecture: "",
        municipality: "",
        telephone: "",
        mobilephone: "",
        email: "",
      };
    },
    async handleAdd() {
      const data = {
        name_kanji: {
          last_name: this.form.last_name_kanji,
          first_name: this.form.first_name_kanji,
        },
        name_kana: {
          last_name: this.form.last_name_kana,
          first_name: this.form.first_name_kana,
        },
        address: {
          sector: this.form.sector,
          prefecture: this.form.prefecture,
          municipality: this.form.municipality,
        },
        postal_code: this.form.postal_code,
        telephone: this.form.telephone,
        mobilephone: this.form.mobilephone,
        email: this.form.email,
        contact_type: this.contactType,
      };
      try {
        await this.$rest.post(`/customers/${this.id}/contacts`, data);
        this.form = this.initForm();
        this.showNewContactDialog = false;
        this.$emit("saved");
      } catch (error) {
        if (error.response && error.response.status < 500)
          this.formErrors = error.response.data.errors;
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
        for (let contactToDelete of this.contactsToDelete) {
          this.$set(contactToDelete, "deleted", undefined);
        }
        this.contactsToDelete && (this.contactsToDelete = []);
        this.showNewContactDialog = false;
        this.relationshipChanges = [];
      }
    },
  },
};
</script>
