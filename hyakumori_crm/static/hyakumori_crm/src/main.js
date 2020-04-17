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

Vue.config.productionTip = false;

setupRouter(router);

Vue.use(HttpClientPlugin);
Vue.use(VeeValidate, {
  i18n,
});

new Vue({
  vuetify,
  store,
  i18n,
  router,
  apolloProvider: createProvider(),
  render: h => h(App),
}).$mount("#app");
