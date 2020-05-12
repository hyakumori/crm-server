<template>
  <section-container-wrapper
    :headerContent="headerContent"
    :toggleEditBtnContent="toggleEditBtnContent"
    :addBtnContent="addBtnContent"
    :isLoading="isLoading"
    :permissions="['manage_forest']"
    :isEditing="isEditing"
    @toggleEdit="val => (isEditing = val)"
    :cancelEdit="
      () => {
        isEditing = false;
      }
    "
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
        :loading="customersForAddingLoading"
        :shown.sync="showSelect"
        :submitBtnText="$t('buttons.add')"
        submitBtnIcon="mdi-plus"
        :handleSubmitClick="handleAdd"
        @needToLoad="handleLoadMore"
        @search="debounceLoadInitCustomersForAdding"
      >
        <template #list>
          <customer-contact-card
            @click="
              (cId, inx) => {
                modalSelectingCustomerId = cId;
                modalSelectingCustomerIndex = inx;
              }
            "
            v-for="(item, indx) in customersForAdding.results"
            :key="item.id"
            :card_id="item.id"
            :contact="item"
            :showAction="false"
            :index="indx"
            :selectedId="modalSelectingCustomerId"
            :selectedIndex="modalSelectingCustomerIndex"
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
import SelectListModal from "../SelectListModal";
import CustomerContactCard from "./CustomerContactCard";

import { debounce, reject, isEmpty, find } from "lodash";

export default {
  name: "forest-contact-tab-container",

  mixins: [ContainerMixin],

  components: {
    SectionContainerWrapper,
    ContactTab,
    SelectListModal,
    CustomerContactCard,
  },

  props: {
    headerContent: String,
    toggleEditBtnContent: String,
    addBtnContent: String,
    customers: Array,
    customersContacts: Array,
    permissions: Array,
    isLoading: Boolean,
    id: String,
    customerIdNameMap: Object,
  },
  data() {
    return {
      isEditing: false,
      customersForAddingLoading: false,
      showSelect: false,
      customersForAdding: { results: [] },
      customersToAdd: [],
      customersToDelete: [],
      modalSelectingCustomerId: null,
      modalSelectingCustomerIndex: null,
      saving: false,
      selectingCustomerId: null,
      defaultCustomersEdit: {},
      defaultCustomersContactsEdit: {},
    };
  },
  created() {
    this.debounceLoadInitCustomersForAdding = debounce(
      this.loadInitCustomersForAdding,
      500,
    );
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
    handleAdd() {
      const c = this.customersForAdding.results.splice(
        this.modalSelectingCustomerIndex,
        1,
      )[0];
      c.added = true;
      this.customersToAdd.push(c);
      this.modalSelectingCustomerIndex = null;
      this.modalSelectingCustomerId = null;
      if (this.customersForAdding.results.length <= 3) {
        this.handleLoadMore();
      }
    },
    handleDelete(customer, index) {
      if (customer.added) {
        delete customer.added;
        this.customersToAdd = reject(this.customersToAdd, { id: customer.id });
        delete this.defaultCustomersEdit[customer_id];
        this.customersForAdding = { results: [] };
      } else {
        const newCustomers = [...this.customers];
        const c = newCustomers[index];
        c.deleted = true;
        this.$store.commit("forest/setCustomers", newCustomers);
        this.customersToDelete.push(c);
      }
    },
    handleUndoDelete(customer, index) {
      const newCustomers = [...this.customers];
      const c = newCustomers[index];
      delete c.deleted;
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
        this.customersForAdding = { results: [] };
      } catch (error) {
        this.saving = false;
      }
    },
    async handleLoadMore() {
      if (!this.customersForAdding.next || this.customersForAddingLoading)
        return;
      this.customersForAddingLoading = true;
      const resp = await this.$rest.get(this.customersForAdding.next);
      this.customersForAdding = {
        next: resp.next,
        previous: resp.previous,
        results: [
          ...this.customersForAdding.results,
          ...reject(resp.results, c => this.customerIdsMap[c.id]),
        ],
      };
      this.customersForAddingLoading = false;
    },
    async loadInitCustomersForAdding(keyword) {
      const reqConfig = keyword
        ? {
            params: {
              search: keyword || "",
            },
          }
        : {};
      this.customersForAddingLoading = true;
      let resp = { next: "/customers" };
      while (resp.next) {
        resp = await this.$rest.get(resp.next, reqConfig);
        this.customersForAdding = {
          next: resp.next,
          previous: resp.previous,
          results: reject(resp.results, c => this.customerIdsMap[c.id]),
        };
        if (this.customersForAdding.results.length > 5) break;
        if (resp.next && resp.next.indexOf("page=") > -1) reqConfig = {};
      }
      this.customersForAddingLoading = false;
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
    showSelect(val) {
      if (val && !this.customersForAdding.next) {
        this.loadInitCustomersForAdding();
      }
    },
    isEditing(val) {
      if (!val) {
        if (this.customersToAdd.length > 0) {
          this.customersToAdd = [];
          const newCustomers = [...this.customers];
          for (let c of newCustomers) {
            delete c.deleted;
          }
          this.$store.commit("forest/setCustomers", newCustomers);
          this.customersForAdding = { results: [] };
        }
        if (this.customersToDelete.length > 0) {
          this.customersForAdding = { results: [] };
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
