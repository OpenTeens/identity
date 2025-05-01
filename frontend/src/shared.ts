import { defineStore } from "pinia";
import { useLocalStorage } from "@vueuse/core";
import { parseAuthToken } from "./utils.ts";

export const useAuthTokenStore = defineStore("tokens", () => {
    const tokenStorage = useLocalStorage("tokens", new Map<string, string>());

    const validTokens = computed(() => {
        const valid = new Map<string, string>();
        for (const user_id in tokenStorage.value) {
            const token = tokenStorage.value.get(user_id);
            if (token && parseAuthToken(token).exp > Date.now() / 1000) {
                valid.set(user_id, token);
            }
        }
        tokenStorage.value = valid;
        return tokenStorage.value;
    });

    function addToken(token: string) {
        const user_id = parseAuthToken(token).user_id;
        tokenStorage.value.set(user_id, token);
    }

    return {
        validTokens,
        addToken,
    };
});
