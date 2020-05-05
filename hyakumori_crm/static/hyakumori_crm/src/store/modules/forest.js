import * as forestApi from "../../api/forest";
import { find } from "lodash";

const state = {
  forest: null,
  forestLoading: false,
  customers: [],
  customersLoading: false,
  customersContacts: [],
  customersContactsLoading: false,
  archives: [],
  archivesLoading: false,
};

const getters = {
  headerInfo(state) {
    if (!state.forest) return {};
    return {
      title: state.forest.internal_id,
      subTitle: state.forest.owner.name_kanji,
      tag: [state.forest.tag.danchi],
      backUrl: { name: "forests" },
    };
  },
  customerIdNameMap(state) {
    if (state.customers.legnth === 0) return {};
    return Object.fromEntries(
      state.customers.map(c => [c.id, c.self_contact.name_kanji]),
    );
  },
};

const actions = {
  async getForest({ commit }, id) {
    commit("forestLoadingOn");
    const forest = await forestApi.fetchBasicInfo(id);
    commit("setForest", forest);
    commit("forestLoadingOff");
  },
  async getCustomers({ commit }, id) {
    commit("customersLoadingOn");
    const customers = await forestApi.fetchForestOwners(id);
    commit("setCustomers", customers);
    commit("customersLoadingOff");
  },
  async getCustomersContacts({ commit }, id) {
    commit("customersContactsLoadingOn");
    const contacts = await forestApi.fetchCustomersContacts(id);
    commit("setCustomersContacts", contacts);
    commit("customersContactsLoadingOff");
  },
  toggleDefaultCustomerLocal({ commit }, { customer_id, val }) {
    commit("toggleDefaultCustomerLocal", { customer_id, val });
  },
  toggleDefaultCustomerContactLocal(
    { commit },
    { customer_id, contact_id, val },
  ) {
    commit("toggleDefaultCustomerContactLocal", {
      customer_id,
      contact_id,
      val,
    });
  },
  async toggleDefaultCustomer({ commit, state }, { id, customer_id, val }) {
    await forestApi.toggleDefaultCustomer(id, customer_id, val);
  },
  async toggleDefaultCustomerContact(
    { commit, state },
    { id, customer_id, contact_id, val },
  ) {
    await forestApi.toggleDefaultCustomerContact(
      id,
      customer_id,
      contact_id,
      val,
    );
  },
};

const mutations = {
  setForest(state, forest) {
    state.forest = forest;
  },
  forestLoadingOn() {
    state.forestLoading = true;
  },
  forestLoadingOff() {
    state.forestLoading = false;
  },
  setCustomers(state, customers) {
    state.customers = customers;
  },
  customersLoadingOn() {
    state.customersLoading = true;
  },
  customersLoadingOff() {
    state.customersLoading = false;
  },
  setCustomersContacts(state, contacts) {
    state.customersContacts = contacts;
  },
  customersContactsLoadingOn() {
    state.customersContactsLoading = true;
  },
  customersContactsLoadingOff() {
    state.customersContactsLoading = false;
  },
  toggleDefaultCustomerLocal(state, { customer_id, val }) {
    const newCustomers = [...state.customers];
    const c = find(newCustomers, { id: customer_id });
    c.default = val;
    state.customers = newCustomers;
  },
  toggleDefaultCustomerContactLocal(state, { customer_id, contact_id, val }) {
    const newCustomersContacts = [...state.customersContacts];
    const c = find(newCustomersContacts, {
      id: contact_id,
      customer_id: customer_id,
    });
    c.default = val;
    state.customersContacts = newCustomersContacts;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
