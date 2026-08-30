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

export type ProfileInput = {
    username: string;
    first_name: string;
    last_name: string;
    email: string;
};

export type PasswordChangeInput = {
    current_password: string;
    new_password: string;
    confirm_password: string;
};

export type PasswordChangeResponse = {
    detail: string;
};

export type InvitationRegistrationInput = {
    token: string;
    username: string;
    first_name: string;
    last_name: string;
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

export async function getProfile() {
    const response = await api.get<AuthUser>("/auth/profile/")
    return response.data
}

export async function updateProfile(input: Partial<ProfileInput>) {
    const csrfToken = await getCsrfToken()

    const response = await api.patch<AuthUser>(
        "/auth/profile/",
        input,
        {
            headers: {
                "X-CSRFToken": csrfToken,
            },
        },
    );

    return response.data
}

export async function changePassword(input: PasswordChangeInput) {
    const csrfToekn = await getCsrfToken();

    const response = await api.post<PasswordChangeResponse>(
        "/auth/password/change/",
        input,
        {
            headers: {
                "X-CSRFToken": csrfToekn,
            },
        },
    );

    return response.data;
}

export async function registerWithInvitation(
    input: InvitationRegistrationInput,
) {
    const csrfToken = await getCsrfToken();

    const response = await api.post<AuthUser>(
        "/auth/register/",
        input,
        {
            headers: {
                "X-CSRFToken": csrfToken,
            },
        },
    );

    return response.data;
}
