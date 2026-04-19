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
  devServerConfig.allowedHosts = 'all';
  devServerConfig.host = '0.0.0.0';
  devServerConfig.port = 3001;  // Use port 3001 for OpenCode
  devServerConfig.historyApiFallback = true;
  return devServerConfig;
};

module.exports = webpackConfig;