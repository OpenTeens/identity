import permissions from "./details.json";
import { Permission } from "./types";

export function getScopeDetail(scope: string): Permission {
    if (scope in permissions) return permissions[scope];
    return permissions.unknown;
}

export { permissions };
export type { Permission };
