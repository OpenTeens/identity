import VueI18nPlugin from "@intlify/unplugin-vue-i18n/vite";
import { VarletImportResolver } from "@varlet/import-resolver";
import vue from "@vitejs/plugin-vue";
import { visualizer } from "rollup-plugin-visualizer";
import autoImport from "unplugin-auto-import/vite";
import UnpluginDetectDuplicatedDeps from "unplugin-detect-duplicated-deps/vite";
import IconsResolver from "unplugin-icons/resolver";
import Icons from "unplugin-icons/vite";
import components from "unplugin-vue-components/vite";
import { defineConfig } from "vite";
import { analyzer } from "vite-bundle-analyzer";
import Inspect from "vite-plugin-inspect";
import vueDevTools from "vite-plugin-vue-devtools";

export default defineConfig({
    plugins: [
        vue(),
        components({
            resolvers: [
                VarletImportResolver(),
                IconsResolver({
                    prefix: "i",
                }),
            ],
        }),
        autoImport({
            include: [
                /\.[tj]sx?$/, // .ts, .tsx, .js, .jsx
                /\.vue$/,
                /\.vue\?vue/, // .vue
                /\.md$/, // .md
            ],
            imports: ["vue", "vue-router"],
            resolvers: [VarletImportResolver({ autoImport: true })],
        }),
        VueI18nPlugin({
            include: "./src/i18n/locales/**.{json}",
            compositionOnly: true,
        }),
        Icons(),
        UnpluginDetectDuplicatedDeps(),
        Inspect(),
        analyzer({
            defaultSizes: "gzip",
        }),
        visualizer(),
        vueDevTools(),
    ],
    server: {
        host: "0.0.0.0",
        port: 9000,
        proxy: {
            "/api": {
                target: "http://127.0.0.1:35271",
            },
            "/.well-known": {
                target: "http://127.0.0.1:35271",
            },
        },
    },
});
