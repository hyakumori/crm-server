import axios from "../plugins/http";

export function getMaintenanceStatus() {
  return axios.get("/maintenance/status");
}
