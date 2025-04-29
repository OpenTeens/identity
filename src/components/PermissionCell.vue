<script setup lang="ts">
import { Icon } from "@iconify/vue/dist/iconify.js";
import { useI18n } from "vue-i18n";
import { Permission } from "../scopes";
import { getSensitivityInfo } from "../sensitivity";
const props = defineProps<{
    permission: Permission;
}>();
const { t } = useI18n(); // 获取国际化的 `t` 函数
const sensitivityInfo = getSensitivityInfo(props.permission.sensitivity);
</script>
<template>
    <var-cell
        border
        :icon="permission.icon"
        :icon-class="`${sensitivityInfo.color}`"
        :title="t(permission.title)"
        :description="t(permission.desc)"
    >
        <template #extra>
            <VarTooltip>
                <Icon
                    :icon="sensitivityInfo.icon"
                    :class="`text-xl ${sensitivityInfo.color}`"
                />
                <template #content>
                    <div class="text-center">
                        <p>
                            <span :class="sensitivityInfo.color">{{
                                t(sensitivityInfo.name)
                            }}</span>
                            {{ t(sensitivityInfo.description) }}
                        </p>
                    </div>
                </template>
            </VarTooltip>
        </template>
    </var-cell>
</template>
<style scoped></style>
