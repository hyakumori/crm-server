import * as rules from "vee-validate/dist/rules";

import { configure, extend } from "vee-validate";

const telephoneRe = /^(\d{2}-\d{4}-\d{4}|\d{3}-\d{3}-\d{4}|\d{4}-\d{2}-\d{4}|\d{1,10})$/;

extend("telephone", value => {
  if (!telephoneRe.test(value)) {
    return false;
  }
  return true;
});

const setupVeeValidate = ({ i18n }) => {
  Object.keys(rules).forEach(rule => {
    extend(rule, rules[rule]);
  });

  configure({
    defaultMessage: (field, values) => {
      values._field_ = i18n.t(`${field}`);
      return i18n.t(`validations.${values._rule_}`, values);
    },
  });
};

const VeeValidate = {
  install: (Vue, options) => {
    setupVeeValidate({ ...options });
  },
};

export default VeeValidate;
