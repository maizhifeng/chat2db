const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/main.ts',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  resolve: {
    extensions: ['.ts', '.js']
  },
  module: {
    rules: [
      { test: /\.ts$/, use: 'ts-loader', exclude: /node_modules/ },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      { test: /\.html$/, use: 'html-loader' }
    ]
  },
  devServer: {
    static: './dist',
    port: 4200,
    historyApiFallback: true
  },
  plugins: [
    new HtmlWebpackPlugin({ template: './src/index.html' })
  ]
};
