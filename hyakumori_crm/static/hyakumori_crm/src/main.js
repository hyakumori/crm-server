import { flattenDeep, intersection, uniq } from "lodash";

import App from "./App.vue";
import Vue from "vue";
import { createProvider } from "./plugins/vue-apollo";
import i18n from "./plugins/i18n";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";

Vue.config.productionTip = false;

const get_scopes = () => {
  let scopes = localStorage.getItem("scopes") || "";
  scopes = scopes.split(",");
  return scopes;
};

const has_scope = scope => {
  return get_scopes().findIndex(scope) !== -1;
};

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.isPublic)) {
    return next();
  }

  if (localStorage.getItem("accessToken") == null) {
    return next({
      path: "/auth/login",
      params: { nextUrl: to.fullPath },
    });
  }

  if (to.matched.some(record => record.meta.isAdmin)) {
    if (has_scope("admin")) {
      return next();
    } else {
      return next({ name: "error-403" });
    }
  }

  if (
    to.matched.some(
      record => record.meta.scopes && record.meta.scopes.length > 0,
    )
  ) {
    const scopes = uniq(
      flattenDeep(to.matched.map(record => record.meta.scopes)),
    );

    if (intersection(scopes, get_scopes()).length > 0) {
      return next();
    } else {
      return next({ name: "error-403" });
    }
  }

  next();
});

new Vue({
  vuetify,
  store,
  i18n,
  router,
  apolloProvider: createProvider(),
  render: h => h(App),
}).$mount("#app");
