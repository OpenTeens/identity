<template>
    <div class="language-switcher">
        <var-button
            round
            type="default"
            @click="toggleDropdown"
            class="icon-button"
        >
            <var-icon name="translate" />
        </var-button>
        <transition name="slide-fade">
            <ul v-if="isOpen" class="dropdown">
                <li
                    v-for="lang in languages"
                    :key="lang.code"
                    @click="selectLanguage(lang.code)"
                    class="dropdown-item"
                    :class="{active: lang.code === active}"
                >
                    {{ lang.name }}
                </li>
            </ul>
        </transition>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { changeLanguage } from "../i18n";
import { red } from "vuetify/util/colors";

// const { locale } = useI18n();
const isOpen = ref(false);
const languages = [
    { code: "en", name: "English" },
    { code: "zh", name: "简体中文" },
];

let active = localStorage.getItem("lang") || "en";

const toggleDropdown = () => {
    isOpen.value = !isOpen.value;
};

const selectLanguage = (code) => {
    console.log("Selected language:", code);
    changeLanguage(code);
    localStorage.setItem("lang", code);
    active = code;
    isOpen.value = false;
    // refresh page
    location.reload();
};
</script>

<style scoped>
    .language-switcher {
        position: absolute;
        top: 10px;
        right: 10px;
        color: #555;
    }

    .icon-button {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s ease;
    }

    .icon-button:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }

    .dropdown {
        margin-top: 10px;
        padding: 0px 0;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        list-style-type: none;
        position: absolute;
        right: 0;
        width: 120px;
        overflow: hidden;
    }

    .dropdown-item {
        padding: 10px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .active {
        color: var(--color-info);
        background-color: #fafafa;
    }

    .dropdown-item:hover {
        background-color: #f0f0f0;
    }

    /* 下拉动画 */
    .slide-fade-enter-active,
    .slide-fade-leave-active {
        transition: all 0.3s ease;
    }

    .slide-fade-enter-from,
    .slide-fade-leave-to {
        transform: translateY(-10px);
        opacity: 0;
    }
</style>
