<script setup lang="ts">
import { useUrlSearchParams } from "@vueuse/core";
import { useCookies } from "@vueuse/integrations/useCookies";
import { FetchError, ofetch } from "ofetch";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useAuthTokenStore } from "../../shared.ts";
import { AuthForParams, AuthTokenResponse } from "../../types.ts";

const { t } = useI18n();
const router = useRouter();
const params = useUrlSearchParams<AuthForParams>("hash");

let authTokenStore = useAuthTokenStore();
let tokenCookies = useCookies(["token"]);

let username = ref("");
let password = ref("");

let loading = ref(false);

let error_detail = ref("");
let has_error = computed({
    get() {
        return error_detail.value != "";
    },
    set(newValue: boolean) {
        if (!newValue) error_detail.value = "";
    },
});

async function login() {
    loading.value = true;
    try {
        let resp = await ofetch<AuthTokenResponse>("/api/login", {
            method: "POST",
            body: {
                login: username.value,
                password: password.value,
            },
        });
        authTokenStore.addToken(resp.token);
        console.log(authTokenStore.validTokens);
        tokenCookies.set("token", resp.token);
        loading.value = false;
        if (params.for) {
            await router.push(params.for);
        }
    } catch (e) {
        if (!(e instanceof FetchError)) {
            console.log(e);
            return;
        }
        switch (e.statusCode) {
            case 401:
                error_detail.value = t("error.invalid_credential");
                break;
        }
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div class="center-container">
        <var-paper :elevation="2" :radius="8" class="board">
            <var-space direction="column">
                <!-- Logo 图片 -->
                <div class="logo-container">
                    <img src="/src/assets/logo.png" alt="Logo" class="logo" />
                </div>
                <h1 class="font-bold text-xl">{{ t("auth.title.login") }}</h1>
                <var-divider />
                <var-input
                    class="col-group-comp"
                    :placeholder="t('auth.input.username')"
                    v-model="username"
                ></var-input>
                <var-input
                    class="col-group-comp"
                    :placeholder="t('auth.input.password')"
                    v-model="password"
                ></var-input>
                <var-divider />
                <div class="flex justify-end">
                    <var-button
                        class="mx-4 min-w-32"
                        text
                        @click="router.push('/auth/signup')"
                        >{{ t("auth.button.goSignup") }}
                    </var-button>
                    <var-loading description="" :loading="loading">
                        <var-button
                            type="primary"
                            class="min-w-24"
                            color="pink"
                            text-color="black"
                            @click="login"
                        >
                            {{ t("auth.button.login") }}
                        </var-button>
                    </var-loading>
                </div>
            </var-space>
        </var-paper>
    </div>

    <var-popup :default-style="false" v-model:show="has_error">
        <var-result
            class="result"
            type="error"
            :title="error_detail"
            description=""
        >
            <template #footer>
                <var-button
                    color="pink"
                    text-color="black"
                    @click="error_detail = ''"
                >
                    {{ t("auth.button.ok") }}
                </var-button>
            </template>
        </var-result>
    </var-popup>
</template>

<style scoped>
.center-container {
    display: flex;
    align-items: center;
    justify-content: center;
}

.board {
    padding: 22px;
    max-width: 90vw;
    background-color: white;
    border-radius: 8px;
}

/* Logo 样式 */
.logo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.logo {
    max-width: 150px; /* 设置 Logo 大小 */
}

/* 输入框间距 */
.col-group-comp {
    margin-bottom: 12px;
}
</style>
