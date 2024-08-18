import { createI18n } from 'vue-i18n';

const translation = {
    en: {
        loading: 'Loading...',
        app_request: 'APP',
        permissions: 'is requiring following permission(s)',
        cancel: 'Cancel',
        approve: 'Approval',
        error: 'Error',
        openid_title: 'OpenID',
        openid_desc: 'The OpenID of your account',
        profile_title: 'Profile',
        profile_desc: 'Your profile information',
        email_title: 'E-mail',
        email_desc: 'Your email address',
        phone_title: 'Phone',
        phone_desc: 'Your phone number',
        address_title: 'Address',
        address_desc: 'Your address',
        unknown_title: 'Unknown',
        unknown_desc: 'Unknown permission',
        normal: 'Normal',
        sensitive: 'Sensitive',
        dangerous: 'Dangerous',
        critical: 'Critical'
    },
    zh: {
        loading: '加载中...',
        app_request: '应用',
        permissions: '正在请求以下权限',
        cancel: '取消',
        approve: '允许',
        error: '错误',
        openid_title: 'OpenID',
        openid_desc: '您的账户的OpenID',
        profile_title: '个人资料',
        profile_desc: '您的个人资料信息',
        email_title: '电子邮件',
        email_desc: '您的电子邮件地址',
        phone_title: '电话',
        phone_desc: '您的电话号码',
        address_title: '地址',
        address_desc: '您的地址',
        unknown_title: '未知',
        unknown_desc: '未知权限',
        normal: '常规',
        sensitive: '敏感',
        dangerous: '危险',
        critical: '极危险'
    }
}

const i18n = createI18n({
    locale: localStorage.getItem('lang') || 'zh',
    messages: translation
})

// 定义changeLanguage函数
function changeLanguage(lang: 'zh' | 'en') {
    localStorage.setItem('lang', lang)
    i18n.global.locale = lang
}

export { changeLanguage };
export default i18n;
