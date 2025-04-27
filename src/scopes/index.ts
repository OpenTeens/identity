import permissions from "./details.json";

export interface Permission {
    title: string;
    desc: string;
    icon: string;
    danger: number;
}

type Permissions = typeof permissions;
type PermissionNames = keyof Permissions;

function isPermissionName(name: string): name is PermissionNames {
    return name in permissions;
}

export function getScopeDetail(scope: PermissionNames | string): Permission {
    if (isPermissionName(scope)) return permissions[scope];
    return permissions.unknown;
}
