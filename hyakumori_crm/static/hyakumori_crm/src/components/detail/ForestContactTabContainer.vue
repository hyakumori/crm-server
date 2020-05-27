<template>
  <section-container-wrapper
    :headerContent="headerContent"
    :toggleEditBtnContent="toggleEditBtnContent"
    :addBtnContent="addBtnContent"
    :isLoading="isLoading"
    :permissions="['manage_forest']"
    :isEditing="isEditing"
    @toggleEdit="val => (isEditing = val)"
    :cancelEdit="handleCancelEdit"
    :addBtnClickHandler="
      () => {
        showSelect = true;
      }
    "
    :saveDisabled="saveDisabled"
    :save="handleSave"
    :saving="saving"
    :showAddBtn="$refs.tabs && $refs.tabs.selectedTab === 'owner'"
  >
    <template>
      <contact-tab
        ref="tabs"
        class="mt-5"
        :class="{ 'mb-10': !isEditing }"
        :customers="tempCustomers"
        :customersContacts="customersContacts"
        :isEditing="isEditing"
        @deleteCustomer="handleDelete"
        @undoDeleteCustomer="handleUndoDelete"
        @customerSelected="
          card_id =>
            selectingCustomerId == card_id
              ? (selectingCustomerId = null)
              : (selectingCustomerId = card_id)
        "
        :selectingCustomerId="selectingCustomerId"
        @toggleDefault="handleToggleDefault"
        @toggleContactDefault="handleToggleContactDefault"
        :customerIdNameMap="customerIdNameMap"
      />
      <select-list-modal
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
          <customer-contact-card
            @click="
              (cId, inx) => {
                modalSelectingId = cId;
                modalSelectingIndex = inx;
              }
            "
            v-for="(item, indx) in itemsForAdding.results"
            :key="item.id"
            :contact="item"
            :showAction="false"
            :index="indx"
            :selectedId="modalSelectingId"
            :selectedIndex="modalSelectingIndex"
            flat
            mode="search"
            :showRelationshipSelect="false"
            clickable
          />
        </template>
      </select-list-modal>
    </template>
  </section-container-wrapper>
</template>

<script>
import SectionContainerWrapper from "../SectionContainerWrapper";
import ContactTab from "./ContactTab";
import ContainerMixin from "./ContainerMixin";
import SelectListModalMixin from "./SelectListModalMixin";
import SelectListModal from "../SelectListModal";
import CustomerContactCard from "./CustomerContactCard";
import { reject, isEmpty, find } from "lodash";

export default {
  name: "forest-contact-tab-container",

  mixins: [ContainerMixin, SelectListModalMixin],

  components: {
    SectionContainerWrapper,
    ContactTab,
    SelectListModal,
    CustomerContactCard,
  },

  props: {
    customers: Array,
    customersContacts: Array,
    permissions: Array,
    id: String,
    customerIdNameMap: Object,
  },
  data() {
    return {
      customersToAdd: [],
      customersToDelete: [],
      selectingCustomerId: null,
      defaultCustomersEdit: {},
      defaultCustomersContactsEdit: {},
      itemsForAddingUrl: "/customers",
    };
  },
  computed: {
    tempCustomers() {
      return [...this.customers, ...this.customersToAdd];
    },
    customerIdsMap() {
      return Object.fromEntries(this.tempCustomers.map(c => [c.id, true]));
    },
    customerIdsToAdd() {
      return this.customersToAdd.map(f => f.id);
    },
    customerIdsToDelete() {
      return this.customersToDelete.map(f => f.id);
    },
    saveDisabled() {
      return (
        this.customerIdsToDelete.length === 0 &&
        this.customerIdsToAdd.length === 0 &&
        isEmpty(this.defaultCustomersEdit) &&
        isEmpty(this.defaultCustomersContactsEdit)
      );
    },
  },
  methods: {
    itemsForAddingResultFilter(item) {
      return this.customerIdsMap[item.id];
    },
    handleCancelEdit() {
      this.isEditing = false;
      this.customersToDelete = [];
      this.customersToAdd = [];
      this.customers.forEach(customer => this.$set(customer, "deleted", false));
    },
    handleAdd() {
      const c = this.itemsForAdding.results.splice(
        this.modalSelectingIndex,
        1,
      )[0];
      c.added = true;
      this.customersToAdd.push(c);
      this.modalSelectingIndex = null;
      this.modalSelectingId = null;
      if (this.itemsForAdding.results.length <= 3) {
        this.handleLoadMore();
      }
    },
    handleDelete(customer, index) {
      if (customer.added) {
        delete customer.added;
        this.customersToAdd = reject(this.customersToAdd, { id: customer.id });
        delete this.defaultCustomersEdit[customer.id];
        this.itemsForAdding = { results: [] };
      } else {
        const newCustomers = [...this.customers];
        const c = newCustomers[index];
        this.$set(c, "deleted", true);
        this.$store.commit("forest/setCustomers", newCustomers);
        this.customersToDelete.push(c);
      }
    },
    handleUndoDelete(customer, index) {
      const newCustomers = [...this.customers];
      const c = newCustomers[index];
      this.$set(c, "deleted", undefined);
      this.$store.commit("forest/setCustomers", newCustomers);
      this.customersToDelete = reject(this.customersToDelete, {
        id: customer.id,
      });
    },
    async handleSave() {
      try {
        this.saving = true;
        if (
          this.customerIdsToAdd.length > 0 ||
          this.customerIdsToDelete.length > 0
        ) {
          await this.$rest.put(`/forests/${this.id}/customers/update`, {
            added: this.customerIdsToAdd,
            deleted: this.customerIdsToDelete,
          });
        }
        if (!isEmpty(this.defaultCustomersEdit)) {
          for (let [customer_id, val] of Object.entries(
            this.defaultCustomersEdit,
          )) {
            await this.$store.dispatch("forest/toggleDefaultCustomer", {
              id: this.id,
              customer_id,
              val,
            });
          }
        }
        if (!isEmpty(this.defaultCustomersContactsEdit)) {
          for (let [customercontact_id, val] of Object.entries(
            this.defaultCustomersContactsEdit,
          )) {
            const [customer_id, contact_id] = customercontact_id.split(",");
            await this.$store.dispatch("forest/toggleDefaultCustomerContact", {
              id: this.id,
              customer_id,
              contact_id,
              val,
            });
          }
          this.$emit("savedCustomersContacts");
        }
        this.$emit("saved");
        this.saving = false;
        this.customersToDelete = [];
        this.customersToAdd = [];
        this.defaultCustomersEdit = {};
        this.defaultCustomersContactsEdit = {};
        this.itemsForAdding = { results: [] };
      } catch (error) {
        this.saving = false;
      }
    },
    handleToggleDefault(val, customer_id) {
      if (this.defaultCustomersEdit[customer_id] === undefined) {
        this.$set(this.defaultCustomersEdit, customer_id, val);
      } else {
        delete this.defaultCustomersEdit[customer_id];
        this.defaultCustomersEdit = { ...this.defaultCustomersEdit };
      }
      const c = find(this.tempCustomers, { id: customer_id });
      this.$set(c, "default", val);
    },
    handleToggleContactDefault(val, customer_id, contact_id) {
      if (
        this.defaultCustomersContactsEdit[`${customer_id},${contact_id}`] ===
        undefined
      )
        this.$set(
          this.defaultCustomersContactsEdit,
          `${customer_id},${contact_id}`,
          val,
        );
      else {
        delete this.defaultCustomersContactsEdit[
          `${customer_id},${contact_id}`
        ];
        this.defaultCustomersContactsEdit = {
          ...this.defaultCustomersContactsEdit,
        };
      }
      const c = find(this.customersContacts, {
        id: contact_id,
        customer_id: customer_id,
      });
      this.$set(c, "default", val);
    },
  },
  watch: {
    isEditing(val) {
      if (!val) {
        if (this.customersToAdd.length > 0) {
          this.customersToAdd = [];
          const newCustomers = [...this.customers];
          for (let c of newCustomers) {
            delete c.deleted;
          }
          this.$store.commit("forest/setCustomers", newCustomers);
          this.itemsForAdding = { results: [] };
        }
        if (this.customersToDelete.length > 0) {
          this.itemsForAdding = { results: [] };
          this.customersToDelete = [];
        }

        for (let [cid, val] of Object.entries(this.defaultCustomersEdit)) {
          this.$store.commit("forest/toggleDefaultCustomerLocal", {
            customer_id: cid,
            val: !val,
          });
        }
        this.defaultCustomersEdit = {};
        for (let [ccid, val] of Object.entries(
          this.defaultCustomersContactsEdit,
        )) {
          const [customer_id, contact_id] = ccid.split(",");
          this.$store.commit("forest/toggleDefaultCustomerContactLocal", {
            customer_id: customer_id,
            contact_id: contact_id,
            val: !val,
          });
        }
        this.defaultCustomersContactsEdit = {};
      }
    },
  },
};
</script>
