import "vuetify-dialog/dist/vuetify-dialog.css";

import AclSetup from "./plugins/acl";
import ActionLog from "./plugins/action-log";
import App from "./App.vue";
import { HttpClientPlugin } from "./plugins/http";
import VeeValidate from "./plugins/vue-veevalidate";
import Vue from "vue";
import VuetifyDialog from "vuetify-dialog";
import axios from "./plugins/http";
import { createProvider } from "./plugins/vue-apollo";
import i18n from "./plugins/i18n";
import router from "./router";
import setupRouter from "./plugins/setup-router";
import store from "./store";
import vuetify from "./plugins/vuetify";

Vue.config.productionTip = false;

setupRouter(router);

Vue.use(HttpClientPlugin);
Vue.use(VeeValidate, {
  i18n,
});
Vue.use(AclSetup);
Vue.use(VuetifyDialog, {
  context: {
    vuetify,
  },
});
Vue.use(ActionLog);

const vm = new Vue({
  vuetify,
  store,
  i18n,
  router,
  apolloProvider: createProvider(),
  render: h => h(App),
});

vm.$mount("#app");
axios.$v = vm;

export default vm;
