import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    pageHeader: "",
    pageIcon: "",
  },
  mutations: {
    setPageHeader(state, pageHeader) {
      state.pageHeader = pageHeader;
    },
    setPageIcon(state, pageIcon) {
      state.pageIcon = pageIcon;
    },
  },
  actions: {
    setPageHeader({ commit }, pageHeader) {
      commit("setPageHeader", pageHeader);
    },
    setPageIcon({ commit }, pageIcon) {
      commit("setPageIcon", pageIcon);
    },
  },
});
