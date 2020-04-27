import axios from "../plugins/http";

export function fetchBasicInfo(forestId) {
  return axios.get(`forests/${forestId}`);
}

export function fetchForestOwner(forestId) {
  return axios.get(`forests/${forestId}/customers`);
}

export function updateBasicInfo(forestId, info) {
  return axios.put(`forests/${forestId}/basic-info`, info);
}
