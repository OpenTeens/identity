<script setup lang="ts">
import { useUrlSearchParams } from '@vueuse/core'
import { AuthorizeParams, ClientInfo } from "../types.ts";
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import axios from 'axios';
import { StyleProvider, Themes } from '@varlet/ui';
import i18n from '../i18n.ts';

// i18n
const getI18n = (raw: string) => {
    let result = computed(() => i18n.global.t(raw))
    return result.value;
}

const data = useUrlSearchParams<AuthorizeParams>('hash');
const info = ref({
    "status": 0,
    "id": -1,
    "app_name": "",
    "app_desc": "",
    "client_id": "",
    "allowed_scopes": "",
    "redirect_uri": ""
} as ClientInfo);

watch(() => data.client_id, async () => {
    try {
        const resp = await axios.get(`/api/client/${data.client_id}/info`);
        info.value = resp.data;
    } catch (e) {
        info.value = {
            "status": 500,
            "id": -1,
            "app_name": "",
            "app_desc": "",
            "client_id": "",
            "allowed_scopes": "",
            "redirect_uri": ""
        };
    }
}, { immediate: true })

const router = useRouter();

function cancel() {
    router.back();
}

async function approve() {
    const resp = await axios.post("/api/approve_authorize", {
        client_id: data.client_id,
        redirect_uri: data.redirect_uri,
        scope: data.scope,
    })
    const code = resp.data.code as string;
    console.log(code);
    window.location.assign(data.redirect_uri + "?code=" + code);
}

const error = computed(() => {
    if (info.value.status === 404) return 'Invalid client_id';
    if (info.value.status === 500) return 'Internal Server Error';
    if (info.value.status != 200) return `Abnormal Error Code: ${info.value.status}`;
    if (data.redirect_uri != info.value.redirect_uri) return 'Invalid redirect_uri';
    const allowed_scopes = info.value.allowed_scopes.split(" ");
    const requested_scopes = data.scope.split(" ");
    for (let i = 0; i < requested_scopes.length; i++) {
        if (!allowed_scopes.includes(requested_scopes[i])) return 'Invalid scope ' + requested_scopes[i];
    }
    return '';
})

// get scope detail
const scope_describe: { [key: string]: { title: string; desc: string; icon: string; danger: number } } = {
    "openid": {
        "title": getI18n('openid_title'),
        "desc": getI18n('openid_desc'),
        "icon": "card-account-details",
        "danger": 0
    },
    "profile": {
        "title": getI18n('profile_title'),
        "desc": getI18n('profile_desc'),
        "icon": "account-circle",
        "danger": 0
    },
    "email": {
        "title": getI18n('email_title'),
        "desc": getI18n('email_desc'),
        "icon": "email",
        "danger": 0
    },
    "phone": {
        "title": getI18n('phone_title'),
        "desc": getI18n('phone_desc'),
        "icon": "phone",
        "danger": 0
    },
    "address": {
        "title": getI18n('address_title'),
        "desc": getI18n('address_desc'),
        "icon": "map-marker",
        "danger": 1
    },
    "__DEFAULT__": {
        "title": getI18n('unknown_title'),
        "desc": getI18n('unknown_desc'),
        "icon": "help",
        "danger": 2
    }
}

var scope_detail = data.scope.split(" ").map((x) => scope_describe[x.toLowerCase()] || scope_describe["__DEFAULT__"]);

const perm_danger_badge_type: { [key: number]: string } = {
    1: "warning",
    2: "danger",
    3: "danger"
}
const perm_danger_badge_val: { [key: number]: string } = {
    0: "Normal",
    1: "Sensitive",
    2: "Dangerous",
    3: "Critical"
}

// Theme
// StyleProvider(Themes.md3Dark);
</script>

<template>
    <var-space id="mainbox" :size="[10, 10]" justify="space-between">
        <div v-if="info.status === 0">
            {{ $t('loading') }}
        </div>
        <div id="authbox" v-else-if="error === ''">
            <var-paper id="area-avatar" :radius="3">
                <var-space align="center" justify="center">
                    <var-avatar src="https://openteens.org/img/p/leo_huo.jpg" class="var-elevation--2" />
                    <var-loading type="wave" />
                    <var-avatar src="https://openteens.org/img/logo/build/full_white.png" class="var-elevation--2"
                        :round="false" />
                </var-space>
            </var-paper>

            <var-paper id="area-authorize" :elevation="2" :radius="8">
                {{ $t('app_request') }} <span class="app-name">{{ info.app_name }}</span> {{ $t('permissions') }}:

                <var-divider />

                <div v-for="x in scope_detail" :key="x.title">
                    <var-cell border :icon="x.icon" :title="x.title" :description="x.desc"
                        :class="'permfield-dangerlv--' + x.danger">
                        <template #extra>
                            <var-badge v-if="x.danger == 0" :value="perm_danger_badge_val[x.danger]"></var-badge>
                            <var-badge v-else :type="perm_danger_badge_type[x.danger]" :value="perm_danger_badge_val[x.danger]"></var-badge>
                        </template>
                    </var-cell>
                </div>

                <!-- <var-divider /> -->
                 <br>

                <var-row>
                    <var-col :span="11">
                        <var-button block v-on:click="cancel">{{ $t('cancel') }}</var-button>
                    </var-col>
                    <var-col :span="2"></var-col>
                    <var-col :span="11">
                        <var-button block type="primary" v-on:click="approve">{{ $t('approve') }}</var-button>
                    </var-col>
                </var-row>
            </var-paper>
        </div>
        <div v-else>
            {{ $t('error') }}: {{ error }}
        </div>
    </var-space>
</template>


<style scoped>
.app-name {
    font-weight: bold;
    color: var(--color-info);
}

.var-paper {
    margin: 30px;
    padding: 20px;
    width: 500px;
    max-width: 90vw !important;
}

.var-avatar {
    background-color: transparent;
    user-select: none;
}

.var-badge {
    opacity: 0.5;
    user-select: none;

    &:hover {
        opacity: 1;
    }
}

/* Permission Sensitivity Alert */

.permfield-dangerlv--0 {}

.permfield-dangerlv--1 {
    color: var(--color-warning);
}

.permfield-dangerlv--2 {
    color: var(--color-danger);
}

.permfield-dangerlv--3 {
    background-color: var(--color-danger);
    color: white;
}
</style>