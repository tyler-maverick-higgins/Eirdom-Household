import {
    Home,
    Mail,
    MailPlus,
    Shield,
    UserPlus,
    X,
} from "lucide-react";

import { useEffect, useState } from "react";
import axios from "axios";
import { createHouseholdInvitation } from "../features/households/api";
import { useHousehold } from "../features/households/useHousehold";

function formatRole(role: string) {
    return role
        .split("_")
        .map(
            (part) =>
                part.charAt(0).toUpperCase() + part.slice(1),
        )
        .join(" ");
}

function getDisplayName(
    firstName: string,
    lastName: string,
    username: string,
) {
    const fullName = [firstName, lastName]
        .filter(Boolean)
        .join(" ");

    return fullName || username;
}

function getInitials(
    firstName: string,
    lastName: string,
    username: string,
) {
    const initials = [firstName, lastName]
        .filter(Boolean)
        .map((name) => name[0]?.toUpperCase())
        .join("");

    return initials || username.slice(0, 2).toUpperCase();
}

function formatInvitationDate(value: string) {
    return new Intl.DateTimeFormat("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric",
    }).format(new Date(value));
}

export default function HouseholdPage() {
    const [inviteOpen, setInviteOpen] = useState(false);
    const [inviteEmail, setInviteEmail] = useState("");
    const [inviteRole, setInviteRole] = useState<"member" | "administrator">(
        "member",
    );
    const [inviteError, setInviteError] = useState("");
    const [inviteSubmitting, setInviteSubmitting] = useState(false);

    const {
        activeHousehold: household,
        loading: householdLoading,
        error: householdError,
        refreshActiveHousehold,
    } = useHousehold();

    const members = household?.members ?? [];
    const pendingInvitations = household?.pending_invitations ?? [];

    const memberCount = members.length;
    const invitationCount = pendingInvitations.length;

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

            await refreshActiveHousehold();

            closeInviteModal();
        } catch (error) {
            if (axios.isAxiosError(error)) {
                const emailError = error.response?.data?.email?.[0];
                const roleError = error.response?.data?.role?.[0];
                const detailError = error.response?.data?.detail;

                setInviteError(
                    emailError ??
                        roleError ??
                        detailError ??
                        "Unable to send the invitation. Please try again.",
                );

                return;
            }

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
                                {memberCount} active{" "}
                                {memberCount === 1 ? "member" : "members"},{" "}
                                {invitationCount} pending{" "}
                                {invitationCount === 1
                                    ? "invitation"
                                    : "invitations"}
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
                            {members.length > 0 ? (
                                members.map((member) => {
                                    const displayName = getDisplayName(
                                        member.user.first_name,
                                        member.user.last_name,
                                        member.user.username,
                                    );

                                    const initials = getInitials(
                                        member.user.first_name,
                                        member.user.last_name,
                                        member.user.username,
                                    );

                                    return (
                                        <div
                                            key={member.id}
                                            className="flex items-center justify-between rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4"
                                        >
                                            <div className="flex min-w-0 items-center gap-4">
                                                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 font-semibold text-eirdom-moscow-midnight">
                                                    {initials}
                                                </div>

                                                <div className="min-w-0">
                                                    <p className="truncate text-sm font-semibold text-eirdom-moscow-midnight">
                                                        {displayName}
                                                    </p>

                                                    <div className="mt-1 flex items-center gap-2 text-xs text-eirdom-muted">
                                                        <Shield size={14} />
                                                        <span>
                                                            {formatRole(
                                                                member.role,
                                                            )}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                                Active
                                            </span>
                                        </div>
                                    );
                                })
                            ) : (
                                <div className="rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4">
                                    <p className="text-sm text-eirdom-muted">
                                        No active household members found.
                                    </p>
                                </div>
                            )}
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
                                    {invitationCount} pending
                                </span>
                            </div>

                            <div className="mt-4 space-y-3">
                                {pendingInvitations.length > 0 ? (
                                    pendingInvitations.map((invitation) => (
                                        <div
                                            key={invitation.id}
                                            className="flex items-center justify-between gap-4 rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4"
                                        >
                                            <div className="flex min-w-0 items-center gap-4">
                                                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                                    <MailPlus size={18} />
                                                </div>

                                                <div className="min-w-0">
                                                    <p className="truncate text-sm font-semibold text-eirdom-moscow-midnight">
                                                        {invitation.email}
                                                    </p>

                                                    <p className="mt-1 text-xs text-eirdom-muted">
                                                        Invited{" "}
                                                        {formatInvitationDate(
                                                            invitation.created_at,
                                                        )}{" "}
                                                        ·{" "}
                                                        {formatRole(
                                                            invitation.role,
                                                        )}
                                                    </p>
                                                </div>
                                            </div>

                                            <span className="shrink-0 rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                                Pending
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <div className="rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4">
                                        <p className="text-sm text-eirdom-muted">
                                            No pending invitations.
                                        </p>
                                    </div>
                                )}
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
                                    {household?.name ?? "Household"}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Members
                                </p>

                                <p className="mt-1 text-sm font-medium text-eirdom-moscow-midnight">
                                    {memberCount} active{" "}
                                    {memberCount === 1 ? "member" : "members"}
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
                                The person will receive an invitation to join{" "}
                                {household?.name ?? "this household"}.
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
                                    className="rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-60"
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
