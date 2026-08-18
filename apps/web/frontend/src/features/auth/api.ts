import { api } from "../../lib/api";

export type AuthUser = {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
};

export type LoginInput = {
    username: string;
    password: string;
};

type CsrfResponse = {
    csrfToken: string;
};

export async function getCsrfToken() {
    const response = await api.get<CsrfResponse>("/auth/csrf/");
    return response.data.csrfToken;
}

export async function login(input: LoginInput) {
    const csrfToken = await getCsrfToken();

    const response = await api.post<AuthUser>("/auth/login/", input, {
        headers: {
            "X-CSRFToken": csrfToken,
        },
    });

    return response.data;
}

export async function logout() {
    const csrfToken = await getCsrfToken();

    await api.post(
        "/auth/logout/",
        {},
        {
            headers: {
                "X-CSRFToken": csrfToken,
            },
        },
    );
}

export async function getCurrentUser() {
    const response = await api.get<AuthUser>("/auth/me/");
    return response.data;
}
