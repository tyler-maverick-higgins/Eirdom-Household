import axios from "axios";
import { CheckCircle2, Home, LogIn, UserPlus } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
    registerWithInvitation,
    type InvitationRegistrationInput,
} from "../features/auth/api";
import { useAuth } from "../features/auth/useAuth";
import {
    acceptHouseholdInvitation,
    validateHouseholdInvitation,
    type HouseholdInvitationValidation,
} from "../features/households/api";

type RegistrationFormState = Omit<
    InvitationRegistrationInput,
    "token"
>;

function formatRole(role: string) {
    return role
        .split("_")
        .map(
            (part) =>
                part.charAt(0).toUpperCase() + part.slice(1),
        )
        .join(" ");
}

function getApiError(
    error: unknown,
    fallback: string,
) {
    if (!axios.isAxiosError(error)) {
        return fallback;
    }

    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
        return detail;
    }

    const fields = error.response?.data;

    if (fields && typeof fields === "object") {
        for (const value of Object.values(fields)) {
            if (Array.isArray(value) && typeof value[0] === "string") {
                return value[0];
            }
        }
    }

    return fallback;
}

export default function InvitationAcceptPage() {
    const { token } = useParams<{ token: string }>();
    const navigate = useNavigate();
    const {
        user,
        loading: authLoading,
        login,
        logout,
    } = useAuth();

    const [invitation, setInvitation] =
        useState<HouseholdInvitationValidation | null>(null);
    const [loading, setLoading] = useState(true);
    const [pageError, setPageError] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const [loginUsername, setLoginUsername] = useState("");
    const [loginPassword, setLoginPassword] = useState("");

    const [registration, setRegistration] =
        useState<RegistrationFormState>({
            username: "",
            first_name: "",
            last_name: "",
            password: "",
        });

    useEffect(() => {
        const loadInvitation = async () => {
            if (!token) {
                setPageError("This invitation link is invalid.");
                setLoading(false);
                return;
            }

            try {
                const data = await validateHouseholdInvitation(token);
                setInvitation(data);
            } catch (error) {
                if (
                    axios.isAxiosError(error) &&
                    error.response?.status === 410
                ) {
                    setPageError("This invitation has expired.");
                } else {
                    setPageError(
                        "This invitation is invalid or no longer available.",
                    );
                }
            } finally {
                setLoading(false);
            }
        };

        void loadInvitation();
    }, [token]);

    const handleRegister = async (
        event: FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        if (!token) {
            return;
        }

        try {
            setSubmitting(true);
            setFormError("");

            await registerWithInvitation({
                token,
                ...registration,
            });

            window.location.reload();
        } catch (error) {
            setFormError(
                getApiError(
                    error,
                    "Unable to create your Steward account.",
                ),
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleLogin = async (
        event: FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        try {
            setSubmitting(true);
            setFormError("");

            await login({
                username: loginUsername,
                password: loginPassword,
            });
        } catch (error) {
            setFormError(
                getApiError(
                    error,
                    "Unable to sign in with those credentials.",
                ),
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleAccept = async () => {
        if (!token) {
            return;
        }

        try {
            setSubmitting(true);
            setFormError("");

            await acceptHouseholdInvitation(token);

            window.location.assign("/household");
        } catch (error) {
            setFormError(
                getApiError(
                    error,
                    "Unable to accept this household invitation.",
                ),
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleSwitchAccount = async () => {
        try {
            setSubmitting(true);
            setFormError("");
            await logout();
        } catch (error) {
            setFormError(
                getApiError(
                    error,
                    "Unable to sign out. Please try again.",
                ),
            );
        } finally {
            setSubmitting(false);
        }
    };

    const signedInWithInvitedEmail =
        user &&
        invitation &&
        user.email.toLowerCase() === invitation.email.toLowerCase();

    if (loading || authLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-eirdom-surface px-4">
                <p className="text-sm text-eirdom-muted">
                    Loading invitation...
                </p>
            </div>
        );
    }

    if (pageError || !invitation) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-eirdom-surface px-4">
                <div className="w-full max-w-lg rounded-xl border border-eirdom-border/40 bg-white/60 p-8 text-center shadow-sm">
                    <img
                        src="/steward-icon.png"
                        alt="Steward"
                        className="mx-auto h-14 w-14 object-contain"
                    />

                    <h1 className="mt-5 text-2xl font-semibold text-eirdom-moscow-midnight">
                        Invitation unavailable
                    </h1>

                    <p className="mt-3 text-sm text-eirdom-muted">
                        {pageError}
                    </p>

                    <button
                        type="button"
                        onClick={() => navigate("/login")}
                        className="mt-6 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90"
                    >
                        Go to Steward
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-eirdom-surface px-4 py-10 sm:px-6">
            <div className="mx-auto w-full max-w-xl">
                <div className="text-center">
                    <img
                        src="/steward-icon.png"
                        alt="Steward"
                        className="mx-auto h-14 w-14 object-contain"
                    />

                    <p className="mt-4 text-sm font-medium text-eirdom-muted">
                        Steward household invitation
                    </p>

                    <h1 className="mt-2 text-3xl font-semibold text-eirdom-moscow-midnight">
                        Join {invitation.household_name}
                    </h1>

                    <p className="mt-3 text-sm text-eirdom-muted">
                        {invitation.inviter_name} invited{" "}
                        <strong>{invitation.email}</strong> to join as a{" "}
                        {formatRole(invitation.role)}.
                    </p>
                </div>

                <div className="mt-8 rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                    {user && !signedInWithInvitedEmail && (
                        <div>
                            <h2 className="text-xl font-semibold text-eirdom-moscow-midnight">
                                Switch accounts to continue
                            </h2>

                            <p className="mt-2 text-sm text-eirdom-muted">
                                You are signed in as {user.email}, but this
                                invitation belongs to {invitation.email}.
                            </p>

                            {formError && (
                                <p className="mt-4 text-sm text-red-700">
                                    {formError}
                                </p>
                            )}

                            <button
                                type="button"
                                onClick={() => void handleSwitchAccount()}
                                disabled={submitting}
                                className="mt-6 w-full rounded-lg bg-eirdom-moscow-midnight px-4 py-2.5 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {submitting
                                    ? "Signing out..."
                                    : "Sign out and continue"}
                            </button>
                        </div>
                    )}

                    {signedInWithInvitedEmail && (
                        <div>
                            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                <CheckCircle2 size={22} />
                            </div>

                            <h2 className="mt-4 text-xl font-semibold text-eirdom-moscow-midnight">
                                Ready to join
                            </h2>

                            <p className="mt-2 text-sm text-eirdom-muted">
                                You are signed in as {user.email}. Accepting
                                will add you to {invitation.household_name}.
                            </p>

                            {formError && (
                                <p className="mt-4 text-sm text-red-700">
                                    {formError}
                                </p>
                            )}

                            <button
                                type="button"
                                onClick={() => void handleAccept()}
                                disabled={submitting}
                                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2.5 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                <Home size={17} />
                                {submitting
                                    ? "Joining household..."
                                    : `Join ${invitation.household_name}`}
                            </button>
                        </div>
                    )}

                    {!user && invitation.account_exists && (
                        <form onSubmit={handleLogin}>
                            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                <LogIn size={22} />
                            </div>

                            <h2 className="mt-4 text-xl font-semibold text-eirdom-moscow-midnight">
                                Sign in to continue
                            </h2>

                            <p className="mt-2 text-sm text-eirdom-muted">
                                A Steward account already exists for{" "}
                                {invitation.email}.
                            </p>

                            <div className="mt-6 space-y-4">
                                <div>
                                    <label
                                        htmlFor="invitation-login-username"
                                        className="text-sm font-medium text-eirdom-moscow-midnight"
                                    >
                                        Username
                                    </label>
                                    <input
                                        id="invitation-login-username"
                                        value={loginUsername}
                                        onChange={(event) =>
                                            setLoginUsername(event.target.value)
                                        }
                                        required
                                        autoComplete="username"
                                        className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                    />
                                </div>

                                <div>
                                    <label
                                        htmlFor="invitation-login-password"
                                        className="text-sm font-medium text-eirdom-moscow-midnight"
                                    >
                                        Password
                                    </label>
                                    <input
                                        id="invitation-login-password"
                                        type="password"
                                        value={loginPassword}
                                        onChange={(event) =>
                                            setLoginPassword(event.target.value)
                                        }
                                        required
                                        autoComplete="current-password"
                                        className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                    />
                                </div>
                            </div>

                            {formError && (
                                <p className="mt-4 text-sm text-red-700">
                                    {formError}
                                </p>
                            )}

                            <button
                                type="submit"
                                disabled={submitting}
                                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2.5 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                <LogIn size={17} />
                                {submitting ? "Signing in..." : "Sign in"}
                            </button>
                        </form>
                    )}

                    {!user && !invitation.account_exists && (
                        <form onSubmit={handleRegister}>
                            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                <UserPlus size={22} />
                            </div>

                            <h2 className="mt-4 text-xl font-semibold text-eirdom-moscow-midnight">
                                Create your Steward account
                            </h2>

                            <p className="mt-2 text-sm text-eirdom-muted">
                                Registration is available because you were
                                invited to this household. Your account email
                                will be {invitation.email}.
                            </p>

                            <div className="mt-6 grid gap-4 sm:grid-cols-2">
                                <div>
                                    <label
                                        htmlFor="invitation-first-name"
                                        className="text-sm font-medium text-eirdom-moscow-midnight"
                                    >
                                        First name
                                    </label>
                                    <input
                                        id="invitation-first-name"
                                        value={registration.first_name}
                                        onChange={(event) =>
                                            setRegistration((current) => ({
                                                ...current,
                                                first_name: event.target.value,
                                            }))
                                        }
                                        required
                                        autoComplete="given-name"
                                        className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                    />
                                </div>

                                <div>
                                    <label
                                        htmlFor="invitation-last-name"
                                        className="text-sm font-medium text-eirdom-moscow-midnight"
                                    >
                                        Last name
                                    </label>
                                    <input
                                        id="invitation-last-name"
                                        value={registration.last_name}
                                        onChange={(event) =>
                                            setRegistration((current) => ({
                                                ...current,
                                                last_name: event.target.value,
                                            }))
                                        }
                                        required
                                        autoComplete="family-name"
                                        className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                    />
                                </div>
                            </div>

                            <div className="mt-4">
                                <label
                                    htmlFor="invitation-username"
                                    className="text-sm font-medium text-eirdom-moscow-midnight"
                                >
                                    Username
                                </label>
                                <input
                                    id="invitation-username"
                                    value={registration.username}
                                    onChange={(event) =>
                                        setRegistration((current) => ({
                                            ...current,
                                            username: event.target.value,
                                        }))
                                    }
                                    required
                                    autoComplete="username"
                                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                />
                            </div>

                            <div className="mt-4">
                                <label
                                    htmlFor="invitation-password"
                                    className="text-sm font-medium text-eirdom-moscow-midnight"
                                >
                                    Password
                                </label>
                                <input
                                    id="invitation-password"
                                    type="password"
                                    value={registration.password}
                                    onChange={(event) =>
                                        setRegistration((current) => ({
                                            ...current,
                                            password: event.target.value,
                                        }))
                                    }
                                    required
                                    autoComplete="new-password"
                                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                />
                            </div>

                            {formError && (
                                <p className="mt-4 text-sm text-red-700">
                                    {formError}
                                </p>
                            )}

                            <button
                                type="submit"
                                disabled={submitting}
                                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2.5 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                <UserPlus size={17} />
                                {submitting
                                    ? "Creating account..."
                                    : "Create account"}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}
