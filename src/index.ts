import { createApp } from 'vue';
import { createRouter, createWebHashHistory } from "vue-router";

import './style.css';
import Varlet from '@varlet/ui'
import App from './App.vue';
import IndexView from "./views/IndexView.vue";
import AuthorizeView from "./views/AuthorizeView.vue";
import '@varlet/ui/es/style'
import i18n from './i18n';

// import { createVuetify } from 'vuetify';
// import * as components from 'vuetify/components'
// import * as directives from 'vuetify/directives'

const app = createApp(App);

const routes = [
    {
        path: '/',
        component: IndexView,
        meta: { title: "Index" }
    },
    {
        path: '/authorize',
        component: AuthorizeView,
        meta: {
            title: "Authorize",
            showNav: false
        }
    },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes
});


app.use(router);
app.use(Varlet);
app.use(i18n)
app.mount('#app');

