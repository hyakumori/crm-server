module.exports = {
  devServer: {
    proxy: {
      "/api*": {
        target: "http://localhost:8000/"
      }
    }
  },
  transpileDependencies: ["vuetify"],
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.(graphql|gql)$/,
          use: [
            {
              loader: "graphql-tag/loader"
            }
          ]
        }
      ]
    }
  }
};
