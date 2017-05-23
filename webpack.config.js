const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const ImageminPlugin = require('imagemin-webpack-plugin').default;
const autoprefixer = require('autoprefixer');
const webpack = require('webpack');


module.exports = {
    context: path.resolve(__dirname, './frontend'),
    entry: {
        index: './js/index.js',
        form: './js/form.js'
    },
    output: {
        path: path.resolve(__dirname, './src/personalisation/static/js'),
        filename: '[name].js',
        sourceMapFilename: '[file].map'
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.js?$/,
                exclude: [/node_modules/],
                use: [{
                    loader: 'babel-loader',
                    options: { presets: ['react', 'es2015', 'stage-0'] }
                }]
            },
            {
                test: /\.css$/,
                use: [ 'style-loader', 'css-loader' ]
            },
            {
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: [
                        {
                            loader: "css-loader",
                            options: {
                                sourceMap: true,
                                minimize: true
                            }
                        },
                        {
                            loader: "postcss-loader",
                            options: {
                                sourceMap: true,
                                plugins: [ autoprefixer ]
                            }
                        },
                        {
                            loader: "sass-loader",
                            options: {
                                sourceMap: true
                            }
                        }
                    ]
                })
            },
            {
                test: /\.(png|jpg|jpeg|gif)/,
                loader: 'file-loader',
                options: {
                    name: '[name].[ext]',
                    outputPath: '../img/'
                }
            }
        ]
    },
    resolve: {
        extensions: [ '.js', '.jsx' ],
        modules: [ 'node_modules' ]
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin({
            name: 'commons',
            filename: 'commons.js',
            minChunks: 2
        }),
        new CopyWebpackPlugin([
            {
                from: './img',
                to: '../img'
            }
        ]),
        new ImageminPlugin(),
        new ExtractTextPlugin({
            filename: '../css/[name].css',
            allChunks: true
        })
    ]
};
