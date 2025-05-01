import { createI18n } from "vue-i18n";
import en from "./locales/en.json";
import zhCN from "./locales/zh-CN.json";

// 定义默认语言
const defaultLocale = navigator.language; // 默认语言为浏览器默认语言

// 创建 i18n 实例
const i18n = createI18n({
    locale: defaultLocale,
    legacy: false,
    fallbackLocale: "zh-CN", // 当未找到当前语言时使用备用语言
    messages: {
        "zh-CN": zhCN,
        en: en,
    },
});

export default i18n;

// async function loadLocaleMessages(locale) {
// 	if (!i18n.global.availableLocales.includes(locale)) {
// 		// 动态导入语言文件
// 		const messages = await import(`./locales/${locale}.json`);
// 		// 设置加载的语言文件
// 		i18n.global.setLocaleMessage(locale, messages.default);
// 	}
// 	// 切换到目标语言
// 	i18n.global.locale.value = locale;
// } // TODO: 此处代码保留备用
