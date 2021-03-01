from ariadne import gql

types = gql(
    """
    directive @wkt_to_geojson(format: JSON) on FIELD_DEFINITION

    type Forest implements Timestamp & Editor {
        id: ID!
        internal_id: String
        attributes: JSON
        cadastral: JSON
        owner: JSON
        contracts_json: JSON
        tags: JSON
        land_attributes: JSON
        forest_attributes: JSON
        geodata: JSON @wkt_to_geojson
        updated_by: User
        updated_at: DateTime
        created_at: DateTime
    }

    extend type Query {
        list_forests(data: ForestListFilterInput): ForestListResponse
        foresttable_headers: ForestTableHeaderResponse
    }

    type ForestListResponse implements HyakumoriResponse {
        ok: Boolean!
        error: JSON
        forests: [Forest!]
        total: Int
    }

    input ForestListFilterInput {
        page: Int
        itemsPerPage: Int
        preItemsPerPage: Int
        sortBy: [String]
        sortDesc: [Boolean]
        filters: JSON
    }

    type ForestTableHeaderResponse implements HyakumoriResponse {
      ok: Boolean!
      error: JSON
      headers: JSON
    }
"""
)
