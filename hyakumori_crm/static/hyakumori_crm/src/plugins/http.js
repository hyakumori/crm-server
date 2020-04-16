/* eslint-disable no-console */
import axios from "axios";
import eventBus from "../BusEvent";

axios.defaults.baseURL = process.env.VUE_APP_REST_HTTP || (window._env && window._env.VUE_APP_REST_HTTP) || "/api/v1";

axios.interceptors.request.use(
  request => {
    const access_token = localStorage.getItem("accessToken");

    if (access_token) {
      request.headers["Authorization"] = "Bearer " + access_token;
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
  response => response,
  error => {
    if (error.response.status === 401) {
      return eventBus.$emit("auth:relogin");
    }

    return new Promise((resolve, reject) => {
      reject(error);
    });
  },
);

export default axios;
