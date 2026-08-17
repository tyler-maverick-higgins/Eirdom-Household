import {
    Home,
    Mail,
    MailPlus,
    RotateCw,
    Shield,
    UserPlus,
    UserRound,
    X,
} from "lucide-react";

import { useEffect, useState } from "react";

import {
    createHouseholdInvitation,
    getHouseholds,
    type Household,
} from "../features/households/api";

export default function HouseholdPage() {
    const [inviteOpen, setInviteOpen] = useState(false);
    const [inviteEmail, setInviteEmail] = useState("");
    const [inviteRole, setInviteRole] = useState<"member" | "administrator">(
        "member",
    );
    const [inviteError, setInviteError] = useState("");
    const [inviteSubmitting, setInviteSubmitting] = useState(false);
    const [household, setHousehold] = useState<Household | null>(null);
    const [householdLoading, setHouseholdLoading] = useState(true);
    const [householdError, setHouseholdError] = useState("");

    const closeInviteModal = () => {
        setInviteOpen(false);
        setInviteEmail("");
        setInviteRole("member");
        setInviteError("");
    };

    useEffect(() => {
        if (!inviteOpen) {
            return;
        }

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                setInviteOpen(false);
                setInviteEmail("");
                setInviteRole("member");
                setInviteError("");
            }
        };

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [inviteOpen]);

    useEffect(() => {
        const loadHousehold = async () => {
            try {
                setHouseholdLoading(true);
                setHouseholdError("");

                const households = await getHouseholds();

                if (households.length === 0) {
                    setHousehold(null);
                    return;
                }

                setHousehold(households[0]);
            } catch {
                setHouseholdError("Unable to load household information.");
            } finally {
                setHouseholdLoading(false);
            }
        };

        void loadHousehold();
    }, []);

    const handleInviteSubmit = async (
        event: React.FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        const trimmedEmail = inviteEmail.trim();

        if (!trimmedEmail) {
            setInviteError("Please enter an email address.");
            return;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(trimmedEmail)) {
            setInviteError("Please enter a valid email address.");
            return;
        }

        if (!household) {
            setInviteError("Household information is not available.");
            return;
        }

        try {
            setInviteSubmitting(true);
            setInviteError("");

            await createHouseholdInvitation(household.id, {
                email: trimmedEmail,
                role: inviteRole,
            });

            closeInviteModal();
        } catch {
            setInviteError("Unable to send the invitation. Please try again.");
        } finally {
            setInviteSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-eirdom-surface">
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <header>
                    {householdError && (
                        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">
                            <p className="text-sm text-red-700">
                                {householdError}
                            </p>
                        </div>
                    )}
                    <p className="text-sm font-medium text-eirdom-muted">
                        Household
                    </p>

                    <h1 className="mt-1 text-3xl font-semibold text-eirdom-moscow-midnight">
                        {householdLoading
                            ? "Loading household..."
                            : (household?.name ?? "Household")}
                    </h1>

                    <p className="mt-2 text-sm text-eirdom-muted">
                        Manage your household members, roles, and household
                        information
                    </p>
                </header>

                <section className="mt-8 rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                    <div className="flex items-start gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                            <Home size={24} />
                        </div>

                        <div className="text-sm font-medium text-eirdom-muted">
                            <p>Primary Household</p>

                            <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                {household?.name ?? "Household"}
                            </h2>

                            <p className="mt-2 text-sm text-eirdom-muted">
                                2 active members, 1 pending invitation
                            </p>
                        </div>
                    </div>
                </section>

                <div className="mt-6 grid gap-6 lg:grid-cols-5">
                    <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-3">
                        <div className="flex items-end justify-between gap-4">
                            <div>
                                <p className="text-sm font-medium text-eirdom-muted">
                                    People
                                </p>

                                <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                    Household members
                                </h2>
                            </div>

                            <button
                                type="button"
                                onClick={() => setInviteOpen(true)}
                                className="inline-flex items-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90"
                            >
                                <UserPlus size={16} />
                                Invite member
                            </button>
                        </div>

                        <div className="mt-6 space-y-3">
                            <div className="flex items-center justify-between rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4">
                                <div className="flex items-center gap-4">
                                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 font-semibold text-eirdom-moscow-midnight">
                                        TH
                                    </div>

                                    <div>
                                        <p className="text-sm font-semibold text-eirdom-moscow-midnight">
                                            Tyler Higgins
                                        </p>

                                        <div className="mt-1 flex items-center gap-2 text-xs text-eirdom-muted">
                                            <Shield size={14} />
                                            <span>Administrator</span>
                                        </div>
                                    </div>
                                </div>

                                <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                    Active
                                </span>
                            </div>

                            <div className="flex items-center justify-between rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4">
                                <div className="flex items-center gap-4">
                                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 font-semibold text-eirdom-moscow-midnight">
                                        IH
                                    </div>

                                    <div>
                                        <p className="text-sm font-semibold text-eirdom-moscow-midnight">
                                            Irina Higgins
                                        </p>

                                        <div className="mt-1 flex items-center gap-2 text-xs text-eirdom-muted">
                                            <UserRound size={14} />
                                            <span>Member</span>
                                        </div>
                                    </div>
                                </div>

                                <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                    Active
                                </span>
                            </div>
                        </div>

                        <div className="mt-8 border-t border-eirdom-border/30 pt-6">
                            <div className="flex items-end justify-between gap-4">
                                <div>
                                    <p className="text-sm font-medium text-eirdom-muted">
                                        Invitations
                                    </p>

                                    <h3 className="mt-1 text-lg font-semibold text-eirdom-moscow-midnight">
                                        Pending invitations
                                    </h3>
                                </div>

                                <span className="text-sm text-eirdom-muted">
                                    1 pending
                                </span>
                            </div>

                            <div className="mt-4">
                                <div className="flex items-center justify-between gap-4 rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4">
                                    <div className="flex min-w-0 items-center gap-4">
                                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                            <MailPlus size={18} />
                                        </div>

                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-semibold text-eirdom-moscow-midnight">
                                                invited@example.com
                                            </p>

                                            <p className="mt-1 text-xs text-eirdom-muted">
                                                Invited August 16 · Member
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex shrink-0 items-center gap-2">
                                        <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                            Pending
                                        </span>

                                        <button
                                            type="button"
                                            className="rounded-md p-2 text-eirdom-muted transition-colors hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-moscow-midnight"
                                            aria-label="Resend invitation"
                                            title="Resend invitation"
                                        >
                                            <RotateCw size={16} />
                                        </button>

                                        <button
                                            type="button"
                                            className="rounded-md p-2 text-eirdom-muted transition-colors hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-moscow-midnight"
                                            aria-label="Cancel invitation"
                                            title="Cancel invitation"
                                        >
                                            <X size={16} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-2">
                        <div>
                            <p className="text-sm font-medium text-eirdom-muted">
                                Details
                            </p>

                            <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                Household information
                            </h2>
                        </div>

                        <div className="mt-6 space-y-5">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Household name
                                </p>

                                <p className="mt-1 text-sm font-medium text-eirdom-moscow-midnight">
                                    Eirdom Household
                                </p>
                            </div>

                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Members
                                </p>

                                <p className="mt-1 text-sm font-medium text-eirdom-moscow-midnight">
                                    2 active members
                                </p>
                            </div>

                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Household email
                                </p>

                                <div className="mt-1 flex items-center gap-2 text-sm font-medium text-eirdom-moscow-midnight">
                                    <Mail size={16} />
                                    <span>Not configured</span>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>
            </div>

            {inviteOpen && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-eirdom-charcoal-deep/50 p-4"
                    onClick={closeInviteModal}
                >
                    <div
                        className="w-full max-w-md rounded-xl border border-eirdom-border/40 bg-eirdom-surface p-6 shadow-xl"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <div className="flex items-start justify-between gap-4">
                            <div>
                                <p className="text-sm font-medium text-eirdom-muted">
                                    Household invitation
                                </p>

                                <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                    Invite household member
                                </h2>
                            </div>

                            <button
                                type="button"
                                onClick={closeInviteModal}
                                className="rounded-md p-2 text-eirdom-muted transition-colors hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-moscow-midnight"
                                aria-label="Close invite member modal"
                            >
                                <X size={18} />
                            </button>
                        </div>

                        <form
                            className="mt-6 space-y-5"
                            onSubmit={handleInviteSubmit}
                        >
                            <div>
                                <label
                                    htmlFor="invite-email"
                                    className="text-sm font-medium text-eirdom-moscow-midnight"
                                >
                                    Email address
                                </label>

                                <input
                                    id="invite-email"
                                    type="email"
                                    value={inviteEmail}
                                    onChange={(event) =>
                                        setInviteEmail(event.target.value)
                                    }
                                    placeholder="name@example.com"
                                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                />
                                {inviteError && (
                                    <p className="mt-2 text-sm text-red-700">
                                        {inviteError}
                                    </p>
                                )}
                            </div>

                            <div>
                                <label
                                    htmlFor="invite-role"
                                    className="text-sm font-medium text-eirdom-moscow-midnight"
                                >
                                    Role
                                </label>

                                <select
                                    id="invite-role"
                                    value={inviteRole}
                                    onChange={(event) =>
                                        setInviteRole(
                                            event.target.value as
                                                "member" | "administrator",
                                        )
                                    }
                                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                                >
                                    <option value="member">Member</option>
                                    <option value="administrator">
                                        Administrator
                                    </option>
                                </select>
                            </div>

                            <p className="text-sm text-eirdom-muted">
                                The person will receive an invitation to join
                                Eirdom Household.
                            </p>

                            <div className="flex justify-end gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={closeInviteModal}
                                    className="rounded-lg border border-eirdom-border/50 px-4 py-2 text-sm font-medium text-eirdom-moscow-midnight transition-colors hover:bg-eirdom-niebla-azul/10"
                                >
                                    Cancel
                                </button>

                                <button
                                    type="submit"
                                    disabled={inviteSubmitting}
                                    className="rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90"
                                >
                                    {inviteSubmitting
                                        ? "Sending..."
                                        : "Send invitation"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
