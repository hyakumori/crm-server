import axios from "axios";
import eventBus from "../BusEvent";

const setupRestClient = options => {
  axios.defaults.baseURL =
    process.env.VUE_APP_REST_HTTP ||
    (window._env && window._env.VUE_APP_REST_HTTP) ||
    "/api/v1";

  axios.defaults = {
    ...axios.defaults,
    ...options,
  };

  axios.interceptors.request.use(
    request => {
      const accessToken = localStorage.getItem("accessToken");

      if (accessToken) {
        request.headers["Authorization"] = "Bearer " + accessToken;
        request.headers["Cache-Control"] = "no-cache";
      }

      return request;
    },
    error => {
      return new Promise((resolve, reject) => {
        reject(error);
      });
    },
  );

  axios.interceptors.response.use(
    response => {
      const method = response && response.config && response.config.method;
      if (method !== "get" && response.config["no_activity"] !== true) {
        eventBus.$emit("action-log:reload");
      }
      return response && response.data;
    },
    error => {
      if (error.response && error.response.status === 401) {
        return new Promise((resolve, reject) => {
          eventBus.$emit("auth:relogin");
          reject(error);
        });
      } else if (error.response && error.response.status === 404) {
        return new Promise((resolve, reject) => {
          eventBus.$emit("rest:404");
          reject(error);
        });
      } else if (error.response && error.response.status === 403) {
        return new Promise((resolve, reject) => {
          // TODO: implement this
          axios.$v.$dialog.notify.error(
            axios.$v.$t("messages.permission_denied"),
            {
              position: "top-right",
              timeout: 5000,
            },
          );
          reject(error);
        });
      } else if (error.response && error.response.status === 400) {
        return new Promise((resolve, reject) => {
          reject(error);
        });
      } else {
        axios.$v.$dialog.notify.error(`${error}`, {
          position: "top-right",
          timeout: 5000,
        });
        return new Promise((resolve, reject) => {
          reject(error);
        });
      }
    },
  );

  return axios;
};

const HttpClientPlugin = {
  install: (Vue, options) => {
    Vue.prototype.$rest = setupRestClient(options);
  },
};

export { HttpClientPlugin };
export default axios;
