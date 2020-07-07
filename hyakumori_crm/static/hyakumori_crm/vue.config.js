const path = require("path");
const CompressionPlugin = require("compression-webpack-plugin");

module.exports = {
  devServer: {
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        ws: false,
        changeOrigin: true,
      },
      "^/graphql": {
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
  configureWebpack: {
    plugins: [
      new CompressionPlugin({
        filename: "[path].gz[query]",
        algorithm: "gzip",
        test: /\.js$|\.css$|\.html$/,
        exclude: "index.html",
        minRatio: 0.8,
      }),
      new CompressionPlugin({
        filename: "[path].br[query]",
        algorithm: "brotliCompress",
        test: /\.(js|css|html|svg)$/,
        exclude: "index.html",
        compressionOptions: {
          // zlib’s `level` option matches Brotli’s `BROTLI_PARAM_QUALITY` option.
          level: 11,
        },
        threshold: 10240,
        minRatio: 0.8,
        deleteOriginalAssets: false,
      }),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
      extensions: [".vue", ".js"],
    },
  },
  transpileDependencies: ["vuetify"],
};
