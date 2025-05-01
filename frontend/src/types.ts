export interface AuthorizeParams {
    client_id: string;
    response_type: string;
    scope: string;
    redirect_uri: string;
}

export interface ClientInfo {
    status: number; // 默认为 200
    id: number;
    app_name: string;
    app_desc: string;
    app_icon_url: string;
    client_id: string;
    allowed_scopes: string;
    redirect_uri: string;
}

export interface AuthTokenResponse {
    token: string;
}

export interface AuthTokenPayload {
    user_id: string;
    iat: number;
    exp: number;
}

export interface AuthForParams {
    for?: string;
}
