from ariadne import gql

types = gql(
    """
scalar Date
scalar DateTime
scalar JSON

type User {
    id: ID!
}

interface Timestamp {
    created_at: DateTime
    updated_at: DateTime
}

interface Editor {
    updated_by: User
}

interface HyakumoriResponse {
    ok: Boolean!
    error: JSON
}
"""
)
