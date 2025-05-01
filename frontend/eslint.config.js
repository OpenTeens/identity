import pluginJs from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";
import pluginVue from "eslint-plugin-vue";
import globals from "globals";
import tseslint from "typescript-eslint";

/** @type {import('eslint').Linter.Config[]} */
export default [
    { files: ["**/*.{js,mjs,cjs,ts,vue}"] },
    { languageOptions: { globals: globals.browser } },
    pluginJs.configs.recommended,
    ...tseslint.configs.recommended,
    ...pluginVue.configs["flat/essential"],
    {
        files: ["**/*.vue"],
        languageOptions: { parserOptions: { parser: tseslint.parser } },
    },
    { ignores: ["dist/**", "auto-imports.d.ts", "components.d.ts"] },
    {
        rules: {
            "no-undef": "off",
            "@typescript-eslint/no-unused-vars": "warn",
        },
    },
    eslintConfigPrettier,
];
