import axios from "axios";
import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../features/auth/useAuth";

type LocationState = {
    from?: {
        pathname?: string;
    };
};

export default function LoginPage() {
    const { user, loading, login } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const locationState = location.state as LocationState | null;
    const destination = locationState?.from?.pathname ?? "/";

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-eirdom-surface">
                <p className="text-sm text-eirdom-muted">Loading Steward...</p>
            </div>
        );
    }

    if (user) {
        return <Navigate to="/" replace />;
    }

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (!username.trim() || !password) {
            setError("Enter your username and password.");
            return;
        }

        try {
            setSubmitting(true);
            setError("");

            await login({
                username: username.trim(),
                password,
            });

            navigate(destination, { replace: true });
        } catch (requestError) {
            if (axios.isAxiosError(requestError)) {
                const detail = requestError.response?.data?.detail;

                setError(
                    detail ??
                        "Unable to sign in. Please check your credentials.",
                );
                return;
            }

            setError("Unable to sign in. Please try again.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-eirdom-surface px-4 py-12">
            <div className="w-full max-w-md">
                <div className="mb-8 text-center">
                  <img
                      src="/steward-logo.png"
                      alt="Steward"
                      className="mx-auto h-auto w-full max-w-xs"
                  />

                    <p className="mt-2 text-sm text-eirdom-muted">
                        Household management, organized.
                    </p>
                </div>

                <div className="rounded-xl border border-eirdom-border/40 bg-white/60 p-8 shadow-sm">
                    <div>
                        <p className="text-sm font-medium text-eirdom-muted">
                            Welcome back
                        </p>

                        <h2 className="mt-1 text-2xl font-semibold text-eirdom-moscow-midnight">
                            Sign in
                        </h2>

                        <p className="mt-2 text-sm text-eirdom-muted">
                            Sign in to continue to your household.
                        </p>
                    </div>

                    <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
                        <div>
                            <label
                                htmlFor="username"
                                className="text-sm font-medium text-eirdom-moscow-midnight"
                            >
                                Username
                            </label>

                            <input
                                id="username"
                                type="text"
                                autoComplete="username"
                                value={username}
                                onChange={(event) =>
                                    setUsername(event.target.value)
                                }
                                disabled={submitting}
                                className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2.5 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-60"
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="password"
                                className="text-sm font-medium text-eirdom-moscow-midnight"
                            >
                                Password
                            </label>

                            <input
                                id="password"
                                type="password"
                                autoComplete="current-password"
                                value={password}
                                onChange={(event) =>
                                    setPassword(event.target.value)
                                }
                                disabled={submitting}
                                className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2.5 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-60"
                            />
                        </div>

                        {error && (
                            <div className="rounded-lg border border-red-200 bg-red-50 p-3">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={submitting}
                            className="w-full rounded-lg bg-eirdom-moscow-midnight px-4 py-2.5 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {submitting ? "Signing in..." : "Sign in"}
                        </button>
                    </form>
                </div>

                <p className="mt-6 text-center text-xs text-eirdom-muted">
                    Steward
                </p>
            </div>
        </div>
    );
}
