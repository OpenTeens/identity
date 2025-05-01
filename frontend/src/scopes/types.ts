export interface Permission {
    title: string;
    desc: string;
    icon: string;
    sensitivity: number;
}

export type Permissions = Record<string, Permission>;
