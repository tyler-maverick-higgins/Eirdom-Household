import { useCallback, useEffect, useState, type ReactNode } from "react";

import {
    getCurrentUser,
    login as loginRequest,
    logout as logoutRequest,
    type AuthUser,
    type LoginInput,
} from "./api";
import { AuthContext } from "./authContext";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshUser = useCallback(async () => {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
    }, []);

    useEffect(() => {
        const loadCurrentUser = async () => {
            try {
                await refreshUser();
            } catch {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        void loadCurrentUser();
    }, [refreshUser]);

    const login = async (input: LoginInput) => {
        const authenticatedUser = await loginRequest(input);
        setUser(authenticatedUser);
    };

    const logout = async () => {
        await logoutRequest();
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                login,
                logout,
                refreshUser,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}
