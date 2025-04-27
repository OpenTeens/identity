export interface Permission {
    title: string;
    desc: string;
    icon: string;
    danger: number;
}

export type Permissions = Record<string, Permission>;
