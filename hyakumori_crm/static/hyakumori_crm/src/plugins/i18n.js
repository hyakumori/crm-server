import Vue from "vue";
import VueI18n from "vue-i18n";
import jpMessages from "../assets/localization/jp.json";
import enMessages from "../assets/localization/en.json";

Vue.use(VueI18n);

const messages = {
  jp: jpMessages,
  en: enMessages
};

const i18n = new VueI18n({
  locale: "en",
  messages,
  fallbackLocale: "jp"
});

export default i18n;
