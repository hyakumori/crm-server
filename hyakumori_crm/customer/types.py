from ariadne import gql

types = gql(
    """
enum RelativeType {
  SON
  DAUGHTER
  WIFE
  HUSBAND
  GRANDSON
  GRANDDAUGHTER
  SISTER
  BROTHER
}

type Customer implements Timestamp & Editor {
  id: ID!
  internal_id: String
  attributes: JSON
  profile: JSON
  updated_by: User
  created_at: DateTime
  updated_at: DateTime
}

type CustomerItem {
  id: String!
  business_id: String
  fullname_kana: String!
  fullname_kanji: String!
  postal_code: String
  prefecture: String
  municipality: String
  address: String
  telephone: String
  mobilephone: String
  email: String
  representative: String
  tags: JSON
}

type CustomerList implements HyakumoriResponse {
  ok: Boolean!
  error: JSON
  items: [CustomerItem!]
  total: Int
}

type CustomerResponse implements HyakumoriResponse {
  ok: Boolean!
  error: JSON
  customer: Customer
}

type CustomerTableHeaderResponse  implements HyakumoriResponse {
  ok: Boolean!
  error: JSON
  headers: JSON
}

type Query {
  get_customer(id: ID!): CustomerResponse
  list_customers(data: TableCustomerFilterInput!): CustomerList!
  customertable_headers: CustomerTableHeaderResponse
}

input CreateCustomerInput {
  internal_id: String
  basic_contact: JSON!
  banking: JSON
}

input TableCustomerFilterInput {
  page: Int!
  itemsPerPage: Int!
  preItemsPerPage: Int
  sortBy: [String]
  sortDesc: [Boolean]
  filters: JSON
}
"""
)
