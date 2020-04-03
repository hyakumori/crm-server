import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import i18n from "./plugins/i18n";
import vuetify from "./plugins/vuetify";
import { createProvider } from "./plugins/vue-apollo";
import store from "./store";

Vue.config.productionTip = false;

new Vue({
  vuetify,
  store,
  i18n,
  router,
  apolloProvider: createProvider(),
  render: h => h(App),
}).$mount("#app");
