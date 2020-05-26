import Vue from "vue";
import Vuex from "vuex";
import forest from "./modules/forest";
import * as api from "../api";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    pageHeader: "",
    pageIcon: "",
    headerInfo: {},
    headerTagColor: "transparent",
    backBtnContent: "",
    inMaintain: false,
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
    setHeaderTagInfo(state, tags) {
      state.headerInfo.tags = tags;
    },
    setHeaderTagColor(state, info) {
      state.headerTagColor = info;
    },
    setBackBtnContent(state, content) {
      state.backBtnContent = content;
    },
    setInMaintain(state, value) {
      state.inMaintain = value;
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
    setHeaderTagInfo({ commit }, tags) {
      commit("setHeaderTagInfo", tags);
    },
    setHeaderTagColor({ commit }, color) {
      commit("setHeaderTagColor", color);
    },
    setBackBtnContent({ commit }, content) {
      commit("setBackBtnContent", content);
    },
    async getMaintenanceStatus({ commit }) {
      try {
        const status = await api.getMaintenanceStatus();
        commit("setInMaintain", status.in_maintain);
      } catch {}
    },
  },
  modules: {
    forest,
  },
});
