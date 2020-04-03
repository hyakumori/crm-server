import Vue from "vue";
import VueApollo from "vue-apollo";
import ApolloClient from "apollo-boost";

Vue.use(VueApollo);

const apolloClient = new ApolloClient({
  uri: process.env.GRAPHQL_API_URL || "http://localhost:8000/graphql",
});

const apolloProvider = new VueApollo({
  defaultClient: apolloClient,
});

export default apolloProvider;
