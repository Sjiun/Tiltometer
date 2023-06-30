// const NodePolyfillPlugin = require('node-polyfill-webpack-plugin')
const path = require('path'),
  HtmlWebpackPlugin = require('html-webpack-plugin'),
  CopyPlugin = require('copy-webpack-plugin'),
  { CleanWebpackPlugin } = require('clean-webpack-plugin'),
  OverwolfPlugin = require('./overwolf.webpack');
const webpack = require('webpack');

module.exports = (env) => ({
  entry: {
    background: './src/background/background.ts',
    desktop: './src/desktop/desktop.ts',
    // desktop_include: './src/desktop/desktop_include.ts',
    in_game: './src/in_game/in_game.ts',
    client: './src/socket/client.ts',
  },
  devtool: 'inline-source-map',
  module: {
    rules: [
      {
        test: /\.ts?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.ts', '.js'],
    fallback:{
      "fs": false,
      "url": false,
      // "fs": require.resolve('fs'),
      // "tls": require.resolve('tls'),
      // "net": require.resolve('net'),
      // "path": require.resolve('path'),
      // "zlib": require.resolve('zlib'),
      "zlib": require.resolve("browserify-zlib"),
      "os": require.resolve("os-browserify/browser"),
      "path": require.resolve("path-browserify"),
      "http": require.resolve('stream-http'),
      "https": require.resolve('https-browserify'),
      "stream": require.resolve('stream-browserify'),
      "crypto": require.resolve('crypto-browserify'),
      "buffer": require.resolve("buffer")
    },
    alias: {
      // ws: './node_modules/xrpl/dist/npm/client/WSWrapper.js'
      // ws: './node_modules/ws/index.js'
    },
  },
  output: {
    // required to fix 'ERR_OSSL_EVP_UNSUPPORTED':
    // https://stackoverflow.com/questions/69394632/webpack-build-failing-with-err-ossl-evp-unsupported
    hashFunction: "xxhash64",
    path: path.resolve(__dirname, 'dist/'),
    filename: 'js/[name].js',
    library: 'tiltometer',
  },

  plugins: [
    // new NodePolyfillPlugin(),
      // Work around for 'Buffer' and 'process' is undefined:
      // https://github.com/webpack/changelog-v5/issues/10
    new webpack.ProvidePlugin({
      Buffer: ['buffer', 'Buffer'],
    }),
    new webpack.ProvidePlugin({
        process: 'process/browser',
    }),
    // new webpack.DefinePlugin({
    //   'process.env.NODE_DEBUG': JSON.stringify(process.env.NODE_DEBUG),
    // }),
    new CleanWebpackPlugin(),
    new CopyPlugin({
      patterns: [{ from: 'public', to: './' }],
    }),
    new HtmlWebpackPlugin({
      template: './src/background/background.html',
      filename: path.resolve(__dirname, './dist/background.html'),
      chunks: ['background'],
    }),
    new HtmlWebpackPlugin({
      template: './src/desktop/desktop.html',
      filename: path.resolve(__dirname, './dist/desktop.html'),
      chunks: ['desktop'],
    }),
    new HtmlWebpackPlugin({
      template: './src/in_game/in_game.html',
      filename: path.resolve(__dirname, './dist/in_game.html'),
      chunks: ['in_game'],
    }),
    new OverwolfPlugin(env),
  ],
});
