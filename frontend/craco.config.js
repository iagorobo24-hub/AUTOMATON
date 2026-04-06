// craco.config.js
const path = require("path");

const isDevServer = process.env.NODE_ENV !== "production";

let webpackConfig = {
  eslint: {
    configure: {
      extends: ["plugin:react-hooks/recommended"],
      rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
      },
    },
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      webpackConfig.watchOptions = {
        ...webpackConfig.watchOptions,
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/build/**',
          '**/dist/**',
          '**/coverage/**',
          '**/public/**',
        ],
      };
      return webpackConfig;
    },
  },
};

webpackConfig.devServer = (devServerConfig) => {
  // Allow connections from any host (needed for Electron)
  devServerConfig.allowedHosts = 'all';
  devServerConfig.host = '0.0.0.0';
  return devServerConfig;
};

module.exports = webpackConfig;
