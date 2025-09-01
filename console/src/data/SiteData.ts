
export const SiteDefaultData = {
    siteName: "Log Simulator",
    version: "2025.09"
}

export const SiteThemeDefaultToken = {
    // "algorithm": "compact",
    "colorPrimary": "rgb(200, 16, 46)",
    "colorSuccess": "rgb(0, 0, 0)",
    "colorWarning": "#fbbc05",
    "colorError": "#d62b1f",
    "colorInfo": "#cba258",
    "fontSize": 12,
    // "borderRadius": 14,
    "wireframe": false,
    "colorIcon": "rgb(200, 16, 46)",
    "colorIconHover": "rgb(200, 16, 46)",
    "colorLink": "rgb(200, 16, 46)",
}

export const SiteThemeComponentsToken = {
    "Statistic": {
        "fontSizeHeading3": 34,
    },
    "Drawer": {
        "padding": 4
    },
    "Table": {
        headerBg: "#faf6ee",
        rowSelectedBg: "#d4e9e2",
        rowHoverBg: "rgb(241, 130, 149)",
    },
    "Button": {
        contentFontSize: 12,
        paddingInline: 12
    }
}

export const defaultPageConfig: PaginationType = {
    current: 1,
    pageSize: 10
}

export const enum RoleEnum {
    admin = "admin", //platform admin
    guest = "guest", //guest
}

export const SeverityColor = {
    critical: "#f50",
    high: "#ff7a45",
    medium: "#ffaa16",
    low: "#87d068",
    info: "#afb1bc"
}


export const DashboardThemeDefaultToken = {
    // "algorithm": "compact",
    "colorPrimary": "#006241",
    "colorSuccess": "#00754A",
    "colorWarning": "#fbbc05",
    "colorError": "#d62b1f",
    "colorInfo": "#cba258",
    "fontSize": 12,
    "borderRadius": 14,
    "wireframe": false,
    "colorIcon": "#006241",
    "colorIconHover": "#006241",
    "colorLink": "#006241",
}


export const DashboardThemeDarkToken = {
    // "algorithm": "compact",
    "colorPrimary": "#26a541",
    "colorSuccess": "#00754A",
    "colorWarning": "#fbbc05",
    "colorError": "#d62b1f",
    "colorInfo": "#cba258",
    "fontSize": 12,
    "borderRadius": 14,
    "wireframe": false,
    "colorBgBase": "#060b12",
    "colorBgContainer": "#121723"
}


export const DashboardThemeComponentsToken = {
    "Statistic": {
        "fontSizeHeading3": 34,
    },
    "Drawer": {
        "padding": 4
    },
    "Table": {
        headerBg: "#faf6ee",
        rowSelectedBg: "#d4e9e2",
        rowHoverBg: "#d4e9e2",
    },
    "Button": {
        contentFontSize: 12,
        paddingInline: 12
    }
}