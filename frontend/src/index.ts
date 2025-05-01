import { createApp } from "vue";

import i18n from "./i18n/i18n.ts"; // 引入 i18n 配置

import "./style.css";
import App from "./App.vue";
import { createPinia } from "pinia";
import { router } from "./router.ts";
// import { createVuetify } from 'vuetify';
// import * as components from 'vuetify/components'
// import * as directives from 'vuetify/directives'

const app = createApp(App);

const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(i18n);
app.mount("#app");
