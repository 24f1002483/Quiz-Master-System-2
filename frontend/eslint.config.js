module.exports = [
  {
    files: ["**/*.js", "**/*.vue"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "module",
    },
    plugins: {
      vue: require("eslint-plugin-vue"),
    },
    extends: [
      "eslint:recommended",
      "plugin:vue/vue3-recommended"
    ],
    rules: {
      // Add or override rules here
    },
  },
]; 