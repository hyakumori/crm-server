import busEvent from "../BusEvent";

const ActionLogSetup = {
  install: Vue => {
    Vue.prototype.$actionLog = {
      reload() {
        busEvent.$emit("action-log:reload");
      },
    };
  },
};

export default ActionLogSetup;
