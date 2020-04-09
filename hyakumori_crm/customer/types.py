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
  internal_id: String
  fullname_kana: String!
  fullname_kanji: String!
  postal_code: String
  address: String
  telephone: String
  mobilephone: String
  representative: String
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

type Mutation {
  create_customer(data: CreateCustomerInput!): CustomerResponse
  delete_customer(pk: ID!): CustomerResponse
  update_customer(pk: ID!, data: UpdateCustomerInput!): CustomerResponse
}

type Query {
  get_customer(id: ID!): CustomerResponse
  list_customers(data: TableCustomerFilterInput!): CustomerList!
}

input CreateCustomerInput {
  internal_id: String
  basic_contact: JSON!
  banking: JSON
}

input TableCustomerFilterInput {
  id: ID
  internal_id: String
  page: Int!
  itemsPerPage: Int!
  preItemsPerPage: Int
  sortBy: [String]
  sortDesc: [Boolean]
}

input UpdateCustomerInput {
  internal_id: String
  profile: JSON
  attributes: JSON
  updated_at: DateTime!
}
"""
)
