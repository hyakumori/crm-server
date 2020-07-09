const path = require("path");
const CompressionPlugin = require("compression-webpack-plugin");

module.exports = {
  devServer: {
    contentBase: path.join(__dirname, "public/"),
    staticOptions: { index: "index-dev.html" },
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
    overlay: {
      warnings: false,
      errors: true,
    },
  },
  configureWebpack: config => {
    if (!config.plugins) config.plugins = [];
    if (process.env.NODE_ENV === "production") {
      config.plugins.push(
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
      );
    }
  },
  chainWebpack: config => {
    if (process.env.NODE_ENV === "production") {
      config.plugin("copy").tap(([options]) => {
        options[0].ignore.push("index-dev.html");
        return [options];
      });
    } else {
      config.plugin("html").tap(args => {
        args[0].template = path.join(__dirname, "public", "index-dev.html");
        return args;
      });
    }
  },
  transpileDependencies: ["vuetify"],
};
