import Vue from "vue";
import Vuex from "vuex";
import forest from "./modules/forest";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    pageHeader: "",
    pageIcon: "",
    headerInfo: {},
    headerTagColor: "transparent",
    backBtnContent: "",
  },
  mutations: {
    setPageHeader(state, pageHeader) {
      state.pageHeader = pageHeader;
    },
    setPageIcon(state, pageIcon) {
      state.pageIcon = pageIcon;
    },
    setHeaderInfo(state, info) {
      state.headerInfo = info;
    },
    setHeaderTagColor(state, info) {
      state.headerTagColor = info;
    },
    setBackBtnContent(state, content) {
      state.backBtnContent = content;
    },
  },
  actions: {
    setPageHeader({ commit }, pageHeader) {
      commit("setPageHeader", pageHeader);
    },
    setPageIcon({ commit }, pageIcon) {
      commit("setPageIcon", pageIcon);
    },
    setHeaderInfo({ commit }, info) {
      commit("setHeaderInfo", info);
    },
    setHeaderTagColor({ commit }, color) {
      commit("setHeaderTagColor", color);
    },
    setBackBtnContent({ commit }, content) {
      commit("setBackBtnContent", content);
    },
  },
  modules: {
    forest,
  },
});
