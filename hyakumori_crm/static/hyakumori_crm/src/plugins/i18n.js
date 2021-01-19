import Vue from "vue";
import VueI18n from "vue-i18n";
import enMessages from "../assets/localization/en.json";
import enValidationMessages from "vee-validate/dist/locale/en.json";
import jpMessages from "../assets/localization/jp.json";
import jpValidationMessages from "vee-validate/dist/locale/ja.json";

Vue.use(VueI18n);

const messages = {
  jp: {
    ...jpMessages,
    validations: {
      ...jpValidationMessages.messages,
      min_value: "{_field_}は{min}以上の数値でなければなりません。",
      daterange: "不正な期間です。",
      telephone: "電話番号は1桁から10桁までの数字を入力してください。",
    },
  },
  en: {
    ...enMessages,
    validations: enValidationMessages.messages,
  },
};

const i18n = new VueI18n({
  fallbackLocale: "jp",
  locale: "jp",
  messages,
  silentTranslationWarn: process.env.NODE_ENV === "production",
});

export default i18n;
