import { createContext } from "react";

import type { AuthUser, LoginInput } from "./api";

export type AuthContextValue = {
    user: AuthUser | null;
    loading: boolean;
    login: (input: LoginInput) => Promise<void>;
    logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | undefined>(
    undefined,
);
