import i18n from "../plugins/i18n";

const makeTitle = title_key => {
  return `${i18n.t("site_name")} - ${i18n.t(title_key)}`;
};

export { makeTitle };
