import axios from "../plugins/http";

export function fetchBasicInfo(forestId) {
  return axios.get(`forests/${forestId}`);
}

export function fetchForestOwner(forestId) {
  return axios.get(`forests/${forestId}/customers`);
}
