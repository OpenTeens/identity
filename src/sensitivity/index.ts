export interface SensitivityInfo {
    sensitivity: number;
    name: string;
    description: string;
    color: string;
    icon: string;
}

const tmpst: Record<number, SensitivityInfo> = {
    "0": {
        sensitivity: 0,
        name: "安全",
        description: "授予该权限几乎没有风险",
        color: "text-[#005533]",
        icon: "mdi-check-circle",
    },
    "1": {
        sensitivity: 1,
        name: "低",
        description: "授予该权限风险较低",
        color: "text-[#005533]",
        icon: "mdi-check-circle",
    },
    "2": {
        sensitivity: 2,
        name: "中",
        description: "授予该权限风险较低",
        color: "text-[#005533]",
        icon: "mdi-check-circle",
    },
    "3": {
        sensitivity: 3,
        name: "高",
        description: "授予该权限风险较高",
        color: "text-[#aa1111]",
        icon: "mdi-alert-circle",
    },
    "4": {
        sensitivity: 4,
        name: "极高",
        description: "授予该权限可能导致账号被接管",
        color: "text-[#005533]",
        icon: "mdi-check-circle",
    },
    "-1": {
        sensitivity: -1,
        name: "未知",
        description: "未知的权限敏感度",
        color: "text-[#aa6600]",
        icon: "mdi-help-circle",
    },
};

export function getSensitivityInfo(sensitivity: number) {
    const sensitivityInfo: SensitivityInfo = tmpst[sensitivity] || tmpst[-1];
    return sensitivityInfo;
}
