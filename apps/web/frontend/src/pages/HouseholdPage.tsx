import { Home, Mail, Shield } from "lucide-react";

import { useAuth } from "../features/auth/useAuth";
import { useHousehold } from "../features/households/useHousehold";

function formatHouseholdType(householdType: string) {
    const labels: Record<string, string> = {
        primary: "Primary Household",
        vacation: "Vacation Home",
        rental: "Rental Property",
        other: "Other",
    };

    return labels[householdType] ?? "Household";
}

function formatRole(role: string) {
    return role
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");
}

function getDisplayName(firstName: string, lastName: string, username: string) {
    const fullName = [firstName, lastName].filter(Boolean).join(" ");

    return fullName || username;
}

function getInitials(firstName: string, lastName: string, username: string) {
    const initials = [firstName, lastName]
        .filter(Boolean)
        .map((name) => name[0]?.toUpperCase())
        .join("");

    return initials || username.slice(0, 2).toUpperCase();
}

export default function HouseholdPage() {
    const { user } = useAuth();

    const {
        activeHousehold: household,
        loading: householdLoading,
        error: householdError,
    } = useHousehold();

    const members = household?.members ?? [];

    const pendingInvitations = household?.pending_invitations ?? [];

    const memberCount = members.length;

    const invitationCount = pendingInvitations.length;

    const currentMembership = user
        ? members.find((member) => member.user.id === user.id)
        : undefined;

    const currentUserRole = currentMembership?.role;

    return (
        <div className="min-h-screen bg-eirdom-surface">
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <header>
                    {householdError && (
                        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
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
                        View household members, invitations, and household
                        information.
                    </p>
                </header>

                <section className="mt-8 rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                    <div className="flex items-start gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                            <Home size={24} />
                        </div>

                        <div className="text-sm font-medium text-eirdom-muted">
                            <p>
                                {household
                                    ? formatHouseholdType(
                                          household.household_type,
                                      )
                                    : "Household"}
                            </p>

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

                            {currentUserRole && (
                                <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                    <Shield size={13} />

                                    <span>
                                        Your role: {formatRole(currentUserRole)}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                <div className="mt-6 grid gap-6 lg:grid-cols-5">
                    <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-3">
                        <div>
                            <p className="text-sm font-medium text-eirdom-muted">
                                People
                            </p>

                            <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                Household members
                            </h2>

                            <p className="mt-2 text-sm text-eirdom-muted">
                                Active members of this household.
                            </p>
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

                                    <p className="mt-2 text-sm text-eirdom-muted">
                                        Invitations awaiting a response.
                                    </p>
                                </div>

                                <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                    {invitationCount} pending
                                </span>
                            </div>

                            <div className="mt-4 space-y-3">
                                {pendingInvitations.length > 0 ? (
                                    pendingInvitations.map((invitation) => (
                                        <div
                                            key={invitation.id}
                                            className="flex flex-col gap-4 rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4 sm:flex-row sm:items-center sm:justify-between"
                                        >
                                            <div className="min-w-0">
                                                <p className="truncate text-sm font-semibold text-eirdom-moscow-midnight">
                                                    {invitation.email}
                                                </p>

                                                <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-eirdom-muted">
                                                    <span>
                                                        {formatRole(
                                                            invitation.role,
                                                        )}
                                                    </span>

                                                    <span aria-hidden="true">
                                                        •
                                                    </span>

                                                    <span>Pending</span>
                                                </div>
                                            </div>

                                            <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                                                Pending
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <div className="rounded-lg border border-dashed border-eirdom-border/50 p-4">
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
                                    Household type
                                </p>

                                <p className="mt-1 text-sm font-medium text-eirdom-moscow-midnight">
                                    {household
                                        ? formatHouseholdType(
                                              household.household_type,
                                          )
                                        : "Household"}
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
                                    Pending invitations
                                </p>

                                <p className="mt-1 text-sm font-medium text-eirdom-moscow-midnight">
                                    {invitationCount} pending{" "}
                                    {invitationCount === 1
                                        ? "invitation"
                                        : "invitations"}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Household email
                                </p>

                                <div className="mt-1 flex items-center gap-2 text-sm font-medium text-eirdom-moscow-midnight">
                                    <Mail size={16} />

                                    <span>
                                        {household?.email || "Not configured"}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
