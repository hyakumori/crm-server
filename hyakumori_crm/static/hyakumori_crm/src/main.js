import AclSetup from "./plugins/acl";
import App from "./App.vue";
import { HttpClientPlugin } from "./plugins/http";
import VeeValidate from "./plugins/vue-veevalidate";
import Vue from "vue";
import { createProvider } from "./plugins/vue-apollo";
import i18n from "./plugins/i18n";
import router from "./router";
import setupRouter from "./plugins/setup-router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import VuetifyDialog from "vuetify-dialog";
import "vuetify-dialog/dist/vuetify-dialog.css";
import axios from "axios";

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
