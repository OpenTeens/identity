<script setup lang="ts">
import { useI18n } from "vue-i18n";

let { t } = useI18n();
</script>
<template>
    <var-divider>
        <var-icon name="heart-outline" style="margin: 0 16px; color: pink" />
    </var-divider>
    <div class="footer flex items-center justify-center">
        <span
            >{{ new Date().getFullYear() }} Identity is made with
            <var-icon name="heart" color="pink"
        /></span>
    </div>
    <div class="footer flex items-center justify-center">
        <span
            ><a href="/user-agreement">{{
                t("footer.user-agreement")
            }}</a></span
        >
        <var-divider vertical />
        <span
            ><a href="/privacy-policy">{{
                t("footer.privacy-policy")
            }}</a></span
        >
        <var-divider vertical />
        <span
            ><a href="/about-us">{{ t("footer.about-us") }}</a></span
        >
    </div>
</template>
<style scoped>
.footer {
    color: #333;
}

.footer a {
    font-size: 14px;
    color: #888;
    text-decoration: none;
}

.footer span {
    font-size: 14px;
    color: #888;
    text-decoration: none;
}
</style>
