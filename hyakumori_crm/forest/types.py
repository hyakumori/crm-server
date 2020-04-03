from ariadne import gql

types = gql("""
    type Forest implements Timestamp & Editor {
        id: ID!
        internal_id: String
        geo_data: JSON
        basic_info: ForestBasicInfo
        attributes: JSON
        owner: Client
        customer: Client
        updated_by: User
        updated_at: DateTime
        created_at: DateTime
    }

    extend type Query {
        list_forests: ForestListResponse
    }

    type ForestBasicInfo {
        acreage: String,
        status: String
    }

    type ForestListResponse implements HyakumoriResponse {
        ok: Boolean!
        error: JSON
        forests: [Forest!]
        total: Int
    }
""")