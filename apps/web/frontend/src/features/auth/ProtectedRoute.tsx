import { Navigate, Outlet, useLocation } from "react-router";

import { useAuth } from "./useAuth";

export function ProtectedRoute() {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-eirdom-surface">
                <p className="text-sm text-eirdom-muted">
                    Loading Steward...
                </p>
            </div>
        );
    }

    if (!user) {
        return (
            <Navigate
                to="/login/"
                replace
                state={{ from: location}}
            />
        );
    }

    return <Outlet />;
}
