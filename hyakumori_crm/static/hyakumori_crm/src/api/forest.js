import axios from "../plugins/http";

export function fetchBasicInfo(forestId) {
  return axios.get(`forests/${forestId}`);
}

export async function fetchForestOwners(forestId) {
  const customers = [];
  try {
    let data = await axios.get(`forests/${forestId}/customers`);
    customers.push(...data.results);
    while (data.next) {
      data = await axios.get(data.next);
      customers.push(...data.results);
    }
  } catch (error) {
    // throw error;
  }
  return customers;
}

export async function fetchCustomersContacts(forestId) {
  const contacts = [];
  try {
    let data = await axios.get(`forests/${forestId}/customers-forest-contacts`);
    contacts.push(...data.results);
    while (data.next) {
      data = await axios.get(data.next);
      contacts.push(...data.results);
    }
  } catch (error) {
    // throw error;
  }
  return contacts;
}

export function updateBasicInfo(forestId, info) {
  try {
    return axios.put(`forests/${forestId}/basic-info`, info);
  } catch (error) {}
}

export function toggleDefaultCustomer(id, customer_id, val) {
  try {
    return axios.put(`forests/${id}/customers/set-default`, {
      customer_id,
      default: val,
    });
  } catch (error) {}
}

export function toggleDefaultCustomerContact(id, customer_id, contact_id, val) {
  try {
    return axios.put(`forests/${id}/customers/set-default-contact`, {
      customer_id,
      contact_id,
      default: val,
    });
  } catch (error) {}
}

export function fetchForestArchives(id) {
  try {
    return axios.get(`forests/${id}/archives`);
  } catch (error) {}
}

export function fetchForestPostalHistories(id) {
  try {
    return axios.get(`forests/${id}/postal-histories`);
  } catch (error) {}
}
