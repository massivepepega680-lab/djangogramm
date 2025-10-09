const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { VueLoaderPlugin } = require('vue-loader');

module.exports = {
    context: __dirname,

    entry: './frontend/src/js/main.js',

    output: {
        path: path.resolve('./static/webpack_bundles/'),
        filename: '[name]-[fullhash].js',
        publicPath: '/static/webpack_bundles/',
    },

    plugins: [
        new BundleTracker({
            path: __dirname,
            filename: 'webpack-stats.json',
        }),
        new MiniCssExtractPlugin({ filename: '[name]-[fullhash].css' }),
        new VueLoaderPlugin(),
    ],

    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
            },
            {
                test: /\.scss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader',
                ],
            },
        ],
    },

    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        },
        extensions: ['*', '.js', '.vue', '.json']
    }
};