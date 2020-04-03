module.exports = {
  devServer: {
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        ws: false,
        changeOrigin: true,
      },
    },
    historyApiFallback: true,
    overlay: {
      warnings: false,
      errors: true,
    },
  },
  transpileDependencies: ["vuetify"],
};
