<template>
    <div class="absolute top-12 right-12">
        <var-menu-select scrollable placement="bottom-end" v-model="locale">
            <var-button type="primary" round icon-container>
                <i-mdi-translate />
            </var-button>
            <template #options>
                <var-menu-option label="en" />
                <var-menu-option label="zh-CN" />
            </template>
        </var-menu-select>
    </div>
</template>
<script setup lang="ts">
import i18n from "../i18n/i18n.ts";
let locale = i18n.global.locale;
</script>

<style lang="css" scoped></style>
