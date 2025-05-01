import { useCookies } from "@vueuse/integrations/useCookies";
import { AuthTokenPayload } from "./types.ts";
import { decodeJwt } from "jose";

const tokenCookies = useCookies(["token"]);

export function checkLogin(): boolean {
    const token = tokenCookies.get("token");
    if (!(typeof token == "string")) return false;
    const parsed = parseAuthToken(token);

    return parsed.exp > Date.now() / 1000;
}

export function parseAuthToken(token: string): AuthTokenPayload {
    return decodeJwt<AuthTokenPayload>(token);
}
