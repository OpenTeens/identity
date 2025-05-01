import {
    createRouter,
    createWebHashHistory,
    RouteLocationRaw,
    RouteRecordRaw,
} from "vue-router";
import { checkLogin } from "./utils.ts";

const IndexView = () => import("./views/IndexView.vue");
const AuthorizeView = () => import("./views/authorize/AuthorizeView.vue");
const SignUpView = () => import("./views/auth/SignUpView.vue");
const LoginView = () => import("./views/auth/LoginView.vue");

const routes: RouteRecordRaw[] = [
    {
        path: "/",
        component: IndexView,
        meta: {
            title: "Index",
            showNav: true,
        },
    },
    {
        path: "/authorize",
        component: AuthorizeView,
        meta: {
            title: "Authorize",
            showNav: false,
            requiresAuth: true,
        },
    },
    {
        path: "/auth/signup",
        component: SignUpView,
        meta: {
            title: "Sign Up",
            showNav: false,
        },
    },
    {
        path: "/auth/login",
        component: LoginView,
        meta: {
            title: "Login",
            showNav: false,
        },
    },
];

export const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

// RequiresAuth handler
router.beforeEach((to): boolean | RouteLocationRaw => {
    if (!to.meta.requiresAuth) return true;
    if (checkLogin()) return true;
    return {
        path: "/auth/login",
        query: { for: to.fullPath },
    };
});
