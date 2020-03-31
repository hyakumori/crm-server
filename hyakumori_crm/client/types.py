from ariadne import gql

types = gql(
    """
type Client implements Timestamp & Editor {
  id: ID!
  internal_id: String
  attributes: JSON
  profile: JSON
  updated_by: User
  created_at: DateTime
  updated_at: DateTime
}

type ClientConnection {
  items: [Client!]
  nextToken: String
}

type ClientResponse implements HyakumoriResponse {
  ok: Boolean!
  error: JSON
  client: Client
}

type Mutation {
  create_client(data: CreateClientInput!): ClientResponse
  delete_client(pk: ID!): ClientResponse
  update_client(pk: ID!, data: UpdateClientInput!): ClientResponse
}

type Query {
  get_client(id: ID!): ClientResponse
  list_clients(filter: TableClientFilterInput, limit: Int, nextToken: String): ClientConnection
}

input CreateClientInput {
  internal_id: String
  profile: JSON
  attributes: JSON
}

input TableClientFilterInput {
  id: ID
  internal_id: String
}

input UpdateClientInput {
  internal_id: String
  profile: JSON
  attributes: JSON
  updated_at: DateTime!
}
"""
)
