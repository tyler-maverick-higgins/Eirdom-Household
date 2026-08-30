import axios from "axios";
import {
    Building2,
    KeyRound,
    Mail,
    RefreshCw,
    Save,
    Settings,
    Shield,
    UserCheck,
    UserMinus,
    UserPlus,
    UserRound,
    Users,
    X,
} from "lucide-react";
import { useCallback, useEffect, useState, type SyntheticEvent } from "react";

import {
    changePassword,
    updateProfile,
    type AuthUser,
} from "../features/auth/api";
import { useAuth } from "../features/auth/useAuth";
import {
    cancelHouseholdInvitation,
    createHouseholdInvitation,
    getHouseholdMembers,
    resendHouseholdInvitation,
    transferHouseholdOwnership,
    updateHousehold,
    updateHouseholdMembership,
    type HouseholdDetail,
    type HouseholdInvitation,
    type HouseholdMember,
    type HouseholdRole,
    type HouseholdType,
} from "../features/households/api";
import { useHousehold } from "../features/households/useHousehold";

type SettingsSection =
    "household" | "members" | "account" | "security" | "application";

type InvitationRole = "administrator" | "member";

type HouseholdSettingsFormProps = {
    household: HouseholdDetail;
    refreshActiveHousehold: () => Promise<void>;
};

type MemberAdministrationProps = {
    household: HouseholdDetail;
    currentUserId: number;
    currentUserRole: HouseholdRole;
    refreshActiveHousehold: () => Promise<void>;
};

type AccountSettingsFormProps = {
    user: AuthUser;
    refreshUser: () => Promise<void>;
};

function getApiError(error: unknown, fallback: string) {
    if (!axios.isAxiosError(error)) {
        return fallback;
    }

    const nameError = error.response?.data?.name?.[0];

    const usernameError = error.response?.data?.username?.[0];

    const firstNameError = error.response?.data?.first_name?.[0];

    const lastNameError = error.response?.data?.last_name?.[0];

    const emailError = error.response?.data?.email?.[0];

    const typeError = error.response?.data?.household_type?.[0];

    const roleError = error.response?.data?.role?.[0];

    const membershipIdError = error.response?.data?.membership_id?.[0];

    const currentPasswordError = error.response?.data?.current_password?.[0];

    const newPasswordError = error.response?.data?.new_password?.[0];

    const confirmPasswordError = error.response?.data?.confirm_password?.[0];

    const nonFieldError = error.response?.data?.non_field_errors?.[0];

    const detailError = error.response?.data?.detail;

    return (
        nameError ??
        usernameError ??
        firstNameError ??
        lastNameError ??
        emailError ??
        typeError ??
        roleError ??
        membershipIdError ??
        currentPasswordError ??
        newPasswordError ??
        confirmPasswordError ??
        nonFieldError ??
        detailError ??
        fallback
    );
}

function getFieldError(error: unknown, field: string): string | undefined {
    if (!axios.isAxiosError(error)) {
        return undefined;
    }

    const fieldErrors = error.response?.data?.[field];

    if (!Array.isArray(fieldErrors)) {
        return undefined;
    }

    const firstError = fieldErrors[0];

    return typeof firstError === "string" ? firstError : undefined;
}

function getDisplayName(member: HouseholdMember) {
    const fullName = [member.user.first_name, member.user.last_name]
        .filter(Boolean)
        .join(" ");

    return fullName || member.user.username;
}

function getInitials(member: HouseholdMember) {
    const initials = [member.user.first_name, member.user.last_name]
        .filter(Boolean)
        .map((name) => name[0]?.toUpperCase())
        .join("");

    return initials || member.user.username.slice(0, 2).toUpperCase();
}

function formatRole(role: HouseholdRole) {
    const labels: Record<HouseholdRole, string> = {
        owner: "Owner",
        administrator: "Administrator",
        member: "Member",
        guest: "Guest",
    };

    return labels[role];
}

function AccountSettingsForm({ user, refreshUser }: AccountSettingsFormProps) {
    const [username, setUsername] = useState(user.username);

    const [firstName, setFirstName] = useState(user.first_name);

    const [lastName, setLastName] = useState(user.last_name);

    const [email, setEmail] = useState(user.email);

    const [saving, setSaving] = useState(false);

    const [message, setMessage] = useState("");

    const [error, setError] = useState("");

    const [usernameError, setUsernameError] = useState("");

    const [firstNameError, setFirstNameError] = useState("");

    const [lastNameError, setLastNameError] = useState("");

    const [emailError, setEmailError] = useState("");

    useEffect(() => {
        if (!message) {
            return;
        }

        const timeoutId = window.setTimeout(() => {
            setMessage("");
        }, 5000);

        return () => {
            window.clearTimeout(timeoutId);
        };
    }, [message]);

    const formChanged =
        username !== user.username ||
        firstName !== user.first_name ||
        lastName !== user.last_name ||
        email !== user.email;

    const clearErrors = () => {
        setError("");
        setUsernameError("");
        setFirstNameError("");
        setLastNameError("");
        setEmailError("");
    };

    const handleSubmit = async (event: SyntheticEvent<HTMLFormElement>) => {
        event.preventDefault();

        clearErrors();
        setMessage("");

        try {
            setSaving(true);

            await updateProfile({
                username: username.trim(),
                first_name: firstName.trim(),
                last_name: lastName.trim(),
                email: email.trim(),
            });

            await refreshUser();

            setMessage("Account settings saved.");
        } catch (error) {
            setUsernameError(getFieldError(error, "username") ?? "");

            setFirstNameError(getFieldError(error, "first_name") ?? "");

            setLastNameError(getFieldError(error, "last_name") ?? "");

            setEmailError(getFieldError(error, "email") ?? "");

            setError(getApiError(error, "Unable to save account settings."));
        } finally {
            setSaving(false);
        }
    };

    return (
        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            <div className="grid gap-5 md:grid-cols-2">
                <div>
                    <label
                        htmlFor="account-first-name"
                        className="text-sm font-medium text-eirdom-moscow-midnight"
                    >
                        First name
                    </label>

                    <input
                        id="account-first-name"
                        type="text"
                        value={firstName}
                        onChange={(event) => setFirstName(event.target.value)}
                        disabled={saving}
                        autoComplete="given-name"
                        className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                    />

                    {firstNameError && (
                        <p className="mt-2 text-xs text-red-700">
                            {firstNameError}
                        </p>
                    )}
                </div>

                <div>
                    <label
                        htmlFor="account-last-name"
                        className="text-sm font-medium text-eirdom-moscow-midnight"
                    >
                        Last name
                    </label>

                    <input
                        id="account-last-name"
                        type="text"
                        value={lastName}
                        onChange={(event) => setLastName(event.target.value)}
                        disabled={saving}
                        autoComplete="family-name"
                        className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                    />

                    {lastNameError && (
                        <p className="mt-2 text-xs text-red-700">
                            {lastNameError}
                        </p>
                    )}
                </div>
            </div>

            <div>
                <label
                    htmlFor="account-username"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Username
                </label>

                <input
                    id="account-username"
                    type="text"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    disabled={saving}
                    autoComplete="username"
                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                />

                <p className="mt-2 text-xs text-eirdom-muted">
                    Used to sign in to Steward.
                </p>

                {usernameError && (
                    <p className="mt-2 text-xs text-red-700">{usernameError}</p>
                )}
            </div>

            <div>
                <label
                    htmlFor="account-email"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Email address
                </label>

                <div className="relative mt-2">
                    <Mail
                        size={16}
                        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-eirdom-muted"
                    />

                    <input
                        id="account-email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        disabled={saving}
                        autoComplete="email"
                        className="w-full rounded-lg border border-eirdom-border/50 bg-white py-2 pl-10 pr-3 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                    />
                </div>

                <p className="mt-2 text-xs text-eirdom-muted">
                    Used for account identity and household invitations.
                </p>

                {emailError && (
                    <p className="mt-2 text-xs text-red-700">{emailError}</p>
                )}
            </div>

            {message && (
                <div className="rounded-lg border border-eirdom-niebla-azul/40 bg-eirdom-niebla-azul/10 p-3">
                    <p className="text-sm text-eirdom-moscow-midnight">
                        {message}
                    </p>
                </div>
            )}

            {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3">
                    <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            <div className="flex justify-end border-t border-eirdom-border/30 pt-5">
                <button
                    type="submit"
                    disabled={saving || !formChanged}
                    className="inline-flex items-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    <Save size={16} />

                    {saving ? "Saving..." : "Save changes"}
                </button>
            </div>
        </form>
    );
}

function PasswordSecurityForm() {
    const [currentPassword, setCurrentPassword] = useState("");

    const [newPassword, setNewPassword] = useState("");

    const [confirmPassword, setConfirmPassword] = useState("");

    const [saving, setSaving] = useState(false);

    const [message, setMessage] = useState("");

    const [error, setError] = useState("");

    const [currentPasswordError, setCurrentPasswordError] = useState("");

    const [newPasswordError, setNewPasswordError] = useState("");

    const [confirmPasswordError, setConfirmPasswordError] = useState("");

    useEffect(() => {
        if (!message) {
            return;
        }

        const timeoutId = window.setTimeout(() => {
            setMessage("");
        }, 5000);

        return () => {
            window.clearTimeout(timeoutId);
        };
    }, [message]);

    const clearErrors = () => {
        setError("");
        setCurrentPasswordError("");
        setNewPasswordError("");
        setConfirmPasswordError("");
    };

    const formComplete =
        currentPassword.length > 0 &&
        newPassword.length > 0 &&
        confirmPassword.length > 0;

    const handleSubmit = async (event: SyntheticEvent<HTMLFormElement>) => {
        event.preventDefault();

        clearErrors();
        setMessage("");

        try {
            setSaving(true);

            const response = await changePassword({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword,
            });

            setCurrentPassword("");
            setNewPassword("");
            setConfirmPassword("");

            setMessage(response.detail);
        } catch (error) {
            setCurrentPasswordError(
                getFieldError(error, "current_password") ?? "",
            );

            setNewPasswordError(getFieldError(error, "new_password") ?? "");

            setConfirmPasswordError(
                getFieldError(error, "confirm_password") ?? "",
            );

            setError(getApiError(error, "Unable to change password."));
        } finally {
            setSaving(false);
        }
    };

    return (
        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            <div>
                <label
                    htmlFor="current-password"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Current password
                </label>

                <input
                    id="current-password"
                    type="password"
                    value={currentPassword}
                    onChange={(event) => setCurrentPassword(event.target.value)}
                    disabled={saving}
                    autoComplete="current-password"
                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                />

                {currentPasswordError && (
                    <p className="mt-2 text-xs text-red-700">
                        {currentPasswordError}
                    </p>
                )}
            </div>

            <div>
                <label
                    htmlFor="new-password"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    New password
                </label>

                <input
                    id="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                    disabled={saving}
                    autoComplete="new-password"
                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                />

                <p className="mt-2 text-xs text-eirdom-muted">
                    Your new password must meet Steward&apos;s password security
                    requirements.
                </p>

                {newPasswordError && (
                    <p className="mt-2 text-xs text-red-700">
                        {newPasswordError}
                    </p>
                )}
            </div>

            <div>
                <label
                    htmlFor="confirm-new-password"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Confirm new password
                </label>

                <input
                    id="confirm-new-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    disabled={saving}
                    autoComplete="new-password"
                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                />

                {confirmPasswordError && (
                    <p className="mt-2 text-xs text-red-700">
                        {confirmPasswordError}
                    </p>
                )}
            </div>

            {message && (
                <div className="rounded-lg border border-eirdom-niebla-azul/40 bg-eirdom-niebla-azul/10 p-3">
                    <p className="text-sm text-eirdom-moscow-midnight">
                        {message}
                    </p>
                </div>
            )}

            {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3">
                    <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            <div className="flex justify-end border-t border-eirdom-border/30 pt-5">
                <button
                    type="submit"
                    disabled={saving || !formComplete}
                    className="inline-flex items-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    <KeyRound size={16} />

                    {saving ? "Changing password..." : "Change password"}
                </button>
            </div>
        </form>
    );
}

function HouseholdSettingsForm({
    household,
    refreshActiveHousehold,
}: HouseholdSettingsFormProps) {
    const [name, setName] = useState(household.name);

    const [email, setEmail] = useState(household.email);

    const [householdType, setHouseholdType] = useState<HouseholdType>(
        household.household_type,
    );

    const [saving, setSaving] = useState(false);

    const [saveError, setSaveError] = useState("");

    const [saveMessage, setSaveMessage] = useState("");

    useEffect(() => {
        if (!saveMessage) {
            return;
        }

        const timeoutId = window.setTimeout(() => {
            setSaveMessage("");
        }, 5000);

        return () => {
            window.clearTimeout(timeoutId);
        };
    }, [saveMessage]);

    const formChanged =
        name !== household.name ||
        email !== household.email ||
        householdType !== household.household_type;

    const handleSubmit = async (event: SyntheticEvent<HTMLFormElement>) => {
        event.preventDefault();

        const trimmedName = name.trim();

        const trimmedEmail = email.trim();

        if (!trimmedName) {
            setSaveError("Household name is required.");
            return;
        }

        try {
            setSaving(true);
            setSaveError("");
            setSaveMessage("");

            await updateHousehold(household.id, {
                name: trimmedName,
                email: trimmedEmail,
                household_type: householdType,
            });

            await refreshActiveHousehold();

            setSaveMessage("Household settings saved.");
        } catch (error) {
            setSaveError(
                getApiError(error, "Unable to save household settings."),
            );
        } finally {
            setSaving(false);
        }
    };

    return (
        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            <div>
                <label
                    htmlFor="household-name"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Household name
                </label>

                <input
                    id="household-name"
                    type="text"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                />

                <p className="mt-2 text-xs text-eirdom-muted">
                    The name shown throughout Steward.
                </p>
            </div>

            <div>
                <label
                    htmlFor="household-type"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Household type
                </label>

                <select
                    id="household-type"
                    value={householdType}
                    onChange={(event) =>
                        setHouseholdType(event.target.value as HouseholdType)
                    }
                    className="mt-2 w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                >
                    <option value="primary">Primary Household</option>

                    <option value="vacation">Vacation Home</option>

                    <option value="rental">Rental Property</option>

                    <option value="other">Other</option>
                </select>

                <p className="mt-2 text-xs text-eirdom-muted">
                    Classifies how this property is used.
                </p>
            </div>

            <div>
                <label
                    htmlFor="household-email"
                    className="text-sm font-medium text-eirdom-moscow-midnight"
                >
                    Household email
                </label>

                <div className="relative mt-2">
                    <Mail
                        size={16}
                        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-eirdom-muted"
                    />

                    <input
                        id="household-email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="household@example.com"
                        className="w-full rounded-lg border border-eirdom-border/50 bg-white py-2 pl-10 pr-3 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight"
                    />
                </div>

                <p className="mt-2 text-xs text-eirdom-muted">
                    Optional shared email address associated with this
                    household.
                </p>
            </div>

            {saveMessage && (
                <div className="rounded-lg border border-eirdom-niebla-azul/40 bg-eirdom-niebla-azul/10 p-3">
                    <p className="text-sm text-eirdom-moscow-midnight">
                        {saveMessage}
                    </p>
                </div>
            )}

            {saveError && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3">
                    <p className="text-sm text-red-700">{saveError}</p>
                </div>
            )}

            <div className="flex justify-end border-t border-eirdom-border/30 pt-5">
                <button
                    type="submit"
                    disabled={saving || !formChanged}
                    className="inline-flex items-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    <Save size={16} />

                    {saving ? "Saving..." : "Save changes"}
                </button>
            </div>
        </form>
    );
}

function MemberAdministration({
    household,
    currentUserId,
    currentUserRole,
    refreshActiveHousehold,
}: MemberAdministrationProps) {
    const [memberships, setMemberships] = useState<HouseholdMember[]>([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const [message, setMessage] = useState("");

    const [inviteEmail, setInviteEmail] = useState("");

    const [inviteRole, setInviteRole] = useState<InvitationRole>("member");

    const [creatingInvitation, setCreatingInvitation] = useState(false);

    const [managingInvitationId, setManagingInvitationId] = useState<
        number | null
    >(null);

    const [transferMembershipId, setTransferMembershipId] = useState<
        number | null
    >(null);

    const [transferringOwnership, setTransferringOwnership] = useState(false);

    const [updatingMembershipId, setUpdatingMembershipId] = useState<
        number | null
    >(null);

    const loadMemberships = useCallback(async () => {
        try {
            setError("");

            const data = await getHouseholdMembers(household.id);

            setMemberships(data);
        } catch (error) {
            setError(getApiError(error, "Unable to load household members."));
        }
    }, [household.id]);

    useEffect(() => {
        let cancelled = false;

        void getHouseholdMembers(household.id)
            .then((data) => {
                if (!cancelled) {
                    setMemberships(data);
                }
            })
            .catch((error: unknown) => {
                if (!cancelled) {
                    setError(
                        getApiError(error, "Unable to load household members."),
                    );
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [household.id]);

    useEffect(() => {
        if (!message) {
            return;
        }

        const timeoutId = window.setTimeout(() => {
            setMessage("");
        }, 5000);

        return () => {
            window.clearTimeout(timeoutId);
        };
    }, [message]);

    const pendingInvitations = household.pending_invitations;

    const effectiveInviteRole: InvitationRole =
        currentUserRole === "owner" ? inviteRole : "member";

    const canManageMember = (membership: HouseholdMember) => {
        if (membership.user.id === currentUserId) {
            return false;
        }

        if (membership.role === "owner") {
            return false;
        }

        if (
            currentUserRole === "administrator" &&
            membership.role === "administrator"
        ) {
            return false;
        }

        return true;
    };

    const getRoleOptions = (membership: HouseholdMember) => {
        if (!canManageMember(membership)) {
            return [];
        }

        if (currentUserRole === "owner") {
            return [
                {
                    value: "administrator",
                    label: "Administrator",
                },
                {
                    value: "member",
                    label: "Member",
                },
                {
                    value: "guest",
                    label: "Guest",
                },
            ] as const;
        }

        return [
            {
                value: "member",
                label: "Member",
            },
            {
                value: "guest",
                label: "Guest",
            },
        ] as const;
    };

    const ownershipCandidates = memberships.filter(
        (membership) => membership.is_active && membership.role !== "owner",
    );

    const handleCreateInvitation = async (
        event: SyntheticEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        const email = inviteEmail.trim().toLowerCase();

        if (!email) {
            setError("Enter an email address for the invitation.");
            return;
        }

        try {
            setCreatingInvitation(true);
            setError("");
            setMessage("");

            await createHouseholdInvitation(household.id, {
                email,
                role: effectiveInviteRole,
            });

            await refreshActiveHousehold();

            setInviteEmail("");

            setInviteRole("member");

            setMessage(`Invitation sent to ${email}.`);
        } catch (error) {
            setError(
                getApiError(error, "Unable to send household invitation."),
            );
        } finally {
            setCreatingInvitation(false);
        }
    };

    const handleResendInvitation = async (invitation: HouseholdInvitation) => {
        try {
            setManagingInvitationId(invitation.id);

            setError("");

            setMessage("");

            await resendHouseholdInvitation(invitation.id);

            await refreshActiveHousehold();

            setMessage(`Invitation resent to ${invitation.email}.`);
        } catch (error) {
            setError(
                getApiError(error, "Unable to resend household invitation."),
            );
        } finally {
            setManagingInvitationId(null);
        }
    };

    const handleCancelInvitation = async (invitation: HouseholdInvitation) => {
        const confirmed = window.confirm(
            `Cancel the invitation for ${invitation.email}?`,
        );

        if (!confirmed) {
            return;
        }

        try {
            setManagingInvitationId(invitation.id);

            setError("");

            setMessage("");

            await cancelHouseholdInvitation(invitation.id);

            await refreshActiveHousehold();

            setMessage(`Invitation for ${invitation.email} was canceled.`);
        } catch (error) {
            setError(
                getApiError(error, "Unable to cancel household invitation."),
            );
        } finally {
            setManagingInvitationId(null);
        }
    };

    const handleRoleChange = async (
        membership: HouseholdMember,
        role: "administrator" | "member" | "guest",
    ) => {
        if (role === membership.role) {
            return;
        }

        try {
            setUpdatingMembershipId(membership.id);

            setError("");

            setMessage("");

            await updateHouseholdMembership(household.id, membership.id, {
                role,
            });

            await loadMemberships();

            await refreshActiveHousehold();

            setMessage(`${getDisplayName(membership)}'s role was updated.`);
        } catch (error) {
            setError(getApiError(error, "Unable to update household member."));
        } finally {
            setUpdatingMembershipId(null);
        }
    };

    const handleActiveStatusChange = async (membership: HouseholdMember) => {
        const nextActiveState = !membership.is_active;

        const action = nextActiveState ? "reactivate" : "deactivate";

        if (!nextActiveState) {
            const confirmed = window.confirm(
                `Deactivate ${getDisplayName(
                    membership,
                )}? They will lose access to this household until reactivated.`,
            );

            if (!confirmed) {
                return;
            }
        }

        try {
            setUpdatingMembershipId(membership.id);

            setError("");

            setMessage("");

            await updateHouseholdMembership(household.id, membership.id, {
                is_active: nextActiveState,
            });

            await loadMemberships();

            await refreshActiveHousehold();

            setMessage(
                `${getDisplayName(membership)} was ${
                    action === "reactivate" ? "reactivated" : "deactivated"
                }.`,
            );
        } catch (error) {
            setError(
                getApiError(error, `Unable to ${action} household member.`),
            );
        } finally {
            setUpdatingMembershipId(null);
        }
    };

    const handleOwnershipTransfer = async () => {
        if (transferMembershipId === null) {
            setError("Select a household member to receive ownership.");

            return;
        }

        const targetMembership = memberships.find(
            (membership) => membership.id === transferMembershipId,
        );

        if (!targetMembership) {
            setError("The selected household member could not be found.");

            return;
        }

        const confirmed = window.confirm(
            `Transfer ownership of ${household.name} to ${getDisplayName(
                targetMembership,
            )}? You will become an Administrator after the transfer.`,
        );

        if (!confirmed) {
            return;
        }

        try {
            setTransferringOwnership(true);

            setError("");

            setMessage("");

            await transferHouseholdOwnership(household.id, {
                membership_id: targetMembership.id,
            });

            await loadMemberships();

            await refreshActiveHousehold();

            setTransferMembershipId(null);

            setInviteRole("member");

            setMessage(
                `Ownership was transferred to ${getDisplayName(
                    targetMembership,
                )}.`,
            );
        } catch (error) {
            setError(
                getApiError(error, "Unable to transfer household ownership."),
            );
        } finally {
            setTransferringOwnership(false);
        }
    };

    if (loading) {
        return (
            <p className="mt-6 text-sm text-eirdom-muted">
                Loading household members...
            </p>
        );
    }

    return (
        <div className="mt-6 space-y-6">
            {message && (
                <div className="rounded-lg border border-eirdom-niebla-azul/40 bg-eirdom-niebla-azul/10 p-3">
                    <p className="text-sm text-eirdom-moscow-midnight">
                        {message}
                    </p>
                </div>
            )}

            {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3">
                    <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            <div className="rounded-lg border border-eirdom-border/30 bg-white/50 p-4">
                <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                        <UserPlus size={18} />
                    </div>

                    <div>
                        <p className="text-sm font-semibold text-eirdom-moscow-midnight">
                            Invite household member
                        </p>

                        <p className="mt-1 text-sm text-eirdom-muted">
                            Send an invitation to join this household.
                            Membership is created after the invitation is
                            accepted.
                        </p>
                    </div>
                </div>

                <form
                    className="mt-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_180px_auto]"
                    onSubmit={handleCreateInvitation}
                >
                    <div>
                        <label
                            htmlFor="member-invitation-email"
                            className="sr-only"
                        >
                            Email address
                        </label>

                        <div className="relative">
                            <Mail
                                size={16}
                                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-eirdom-muted"
                            />

                            <input
                                id="member-invitation-email"
                                type="email"
                                value={inviteEmail}
                                onChange={(event) =>
                                    setInviteEmail(event.target.value)
                                }
                                placeholder="member@example.com"
                                disabled={creatingInvitation}
                                className="w-full rounded-lg border border-eirdom-border/50 bg-white py-2 pl-10 pr-3 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                            />
                        </div>
                    </div>

                    <div>
                        <label
                            htmlFor="member-invitation-role"
                            className="sr-only"
                        >
                            Role
                        </label>

                        <select
                            id="member-invitation-role"
                            value={effectiveInviteRole}
                            disabled={creatingInvitation}
                            onChange={(event) =>
                                setInviteRole(
                                    event.target.value as InvitationRole,
                                )
                            }
                            className="w-full rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {currentUserRole === "owner" && (
                                <option value="administrator">
                                    Administrator
                                </option>
                            )}

                            <option value="member">Member</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={creatingInvitation || !inviteEmail.trim()}
                        className="inline-flex items-center justify-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        <UserPlus size={16} />

                        {creatingInvitation ? "Sending..." : "Send invitation"}
                    </button>
                </form>
            </div>

            <div>
                <div className="flex items-center justify-between gap-4">
                    <div>
                        <h3 className="text-sm font-semibold text-eirdom-moscow-midnight">
                            Pending invitations
                        </h3>

                        <p className="mt-1 text-xs text-eirdom-muted">
                            Invitations that have not yet been accepted,
                            declined, or canceled.
                        </p>
                    </div>

                    <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                        {pendingInvitations.length}
                    </span>
                </div>

                {pendingInvitations.length === 0 ? (
                    <div className="mt-3 rounded-lg border border-dashed border-eirdom-border/50 p-4">
                        <p className="text-sm text-eirdom-muted">
                            There are no pending household invitations.
                        </p>
                    </div>
                ) : (
                    <div className="mt-3 space-y-3">
                        {pendingInvitations.map((invitation) => {
                            const managing =
                                managingInvitationId === invitation.id;

                            return (
                                <div
                                    key={invitation.id}
                                    className="flex flex-col gap-4 rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4 lg:flex-row lg:items-center lg:justify-between"
                                >
                                    <div className="min-w-0">
                                        <p className="truncate text-sm font-semibold text-eirdom-moscow-midnight">
                                            {invitation.email}
                                        </p>

                                        <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-eirdom-muted">
                                            <span>
                                                {formatRole(invitation.role)}
                                            </span>

                                            <span aria-hidden="true">•</span>

                                            <span>Pending</span>
                                        </div>
                                    </div>

                                    <div className="flex flex-col gap-2 sm:flex-row">
                                        <button
                                            type="button"
                                            disabled={managing}
                                            onClick={() =>
                                                void handleResendInvitation(
                                                    invitation,
                                                )
                                            }
                                            className="inline-flex items-center justify-center gap-2 rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm font-medium text-eirdom-moscow-midnight transition-colors hover:bg-eirdom-niebla-azul/20 disabled:cursor-not-allowed disabled:opacity-50"
                                        >
                                            <RefreshCw size={15} />

                                            {managing ? "Working..." : "Resend"}
                                        </button>

                                        <button
                                            type="button"
                                            disabled={managing}
                                            onClick={() =>
                                                void handleCancelInvitation(
                                                    invitation,
                                                )
                                            }
                                            className="inline-flex items-center justify-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                                        >
                                            <X size={15} />
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            <div>
                <div className="flex items-center justify-between gap-4">
                    <div>
                        <h3 className="text-sm font-semibold text-eirdom-moscow-midnight">
                            Household members
                        </h3>

                        <p className="mt-1 text-xs text-eirdom-muted">
                            Manage roles and household access for existing
                            members.
                        </p>
                    </div>

                    <span className="rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight">
                        {memberships.length}
                    </span>
                </div>

                <div className="mt-3 space-y-3">
                    {memberships.map((membership) => {
                        const manageable = canManageMember(membership);

                        const roleOptions = getRoleOptions(membership);

                        const updating = updatingMembershipId === membership.id;

                        return (
                            <div
                                key={membership.id}
                                className="rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4"
                            >
                                <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                                    <div className="flex min-w-0 items-center gap-4">
                                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 font-semibold text-eirdom-moscow-midnight">
                                            {getInitials(membership)}
                                        </div>

                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-semibold text-eirdom-moscow-midnight">
                                                {getDisplayName(membership)}
                                            </p>

                                            <p className="mt-1 truncate text-xs text-eirdom-muted">
                                                {membership.user.email}
                                            </p>

                                            <div className="mt-1 flex items-center gap-2 text-xs text-eirdom-muted">
                                                <Shield size={13} />

                                                <span>
                                                    {formatRole(
                                                        membership.role,
                                                    )}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                                        {manageable &&
                                        roleOptions.length > 0 ? (
                                            <select
                                                value={membership.role}
                                                disabled={
                                                    updating ||
                                                    !membership.is_active
                                                }
                                                onChange={(event) =>
                                                    void handleRoleChange(
                                                        membership,
                                                        event.target.value as
                                                            | "administrator"
                                                            | "member"
                                                            | "guest",
                                                    )
                                                }
                                                className="rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                                            >
                                                {roleOptions.map((option) => (
                                                    <option
                                                        key={option.value}
                                                        value={option.value}
                                                    >
                                                        {option.label}
                                                    </option>
                                                ))}
                                            </select>
                                        ) : (
                                            <span className="rounded-lg border border-eirdom-border/30 px-3 py-2 text-sm text-eirdom-muted">
                                                {formatRole(membership.role)}
                                            </span>
                                        )}

                                        {manageable && (
                                            <button
                                                type="button"
                                                disabled={updating}
                                                onClick={() =>
                                                    void handleActiveStatusChange(
                                                        membership,
                                                    )
                                                }
                                                className={
                                                    membership.is_active
                                                        ? "inline-flex items-center justify-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                                                        : "inline-flex items-center justify-center gap-2 rounded-lg border border-eirdom-border/50 px-3 py-2 text-sm font-medium text-eirdom-moscow-midnight transition-colors hover:bg-eirdom-niebla-azul/20 disabled:cursor-not-allowed disabled:opacity-50"
                                                }
                                            >
                                                {membership.is_active ? (
                                                    <UserMinus size={16} />
                                                ) : (
                                                    <UserCheck size={16} />
                                                )}

                                                {updating
                                                    ? "Updating..."
                                                    : membership.is_active
                                                      ? "Deactivate"
                                                      : "Reactivate"}
                                            </button>
                                        )}

                                        <span
                                            className={
                                                membership.is_active
                                                    ? "rounded-full bg-eirdom-niebla-azul/20 px-3 py-1 text-xs font-medium text-eirdom-moscow-midnight"
                                                    : "rounded-full bg-eirdom-border/30 px-3 py-1 text-xs font-medium text-eirdom-muted"
                                            }
                                        >
                                            {membership.is_active
                                                ? "Active"
                                                : "Inactive"}
                                        </span>
                                    </div>
                                </div>

                                {!manageable && membership.role === "owner" && (
                                    <p className="mt-3 text-xs text-eirdom-muted">
                                        Ownership is managed through the
                                        dedicated ownership transfer process.
                                    </p>
                                )}

                                {!manageable &&
                                    membership.user.id === currentUserId && (
                                        <p className="mt-3 text-xs text-eirdom-muted">
                                            Your own membership cannot be
                                            changed from this section.
                                        </p>
                                    )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {currentUserRole === "owner" && (
                <div className="rounded-lg border border-eirdom-border/30 bg-white/50 p-4">
                    <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                            <Shield size={18} />
                        </div>

                        <div>
                            <p className="text-sm font-semibold text-eirdom-moscow-midnight">
                                Transfer ownership
                            </p>

                            <p className="mt-1 text-sm text-eirdom-muted">
                                Assign another active household member as Owner.
                                Your membership will become Administrator after
                                the transfer.
                            </p>
                        </div>
                    </div>

                    <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                        <select
                            value={transferMembershipId ?? ""}
                            disabled={
                                transferringOwnership ||
                                ownershipCandidates.length === 0
                            }
                            onChange={(event) => {
                                const value = event.target.value;

                                setTransferMembershipId(
                                    value ? Number(value) : null,
                                );
                            }}
                            className="min-w-0 flex-1 rounded-lg border border-eirdom-border/50 bg-white px-3 py-2 text-sm text-eirdom-moscow-midnight outline-none transition focus:border-eirdom-moscow-midnight disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <option value="">Select a new owner</option>

                            {ownershipCandidates.map((membership) => (
                                <option
                                    key={membership.id}
                                    value={membership.id}
                                >
                                    {getDisplayName(membership)} —{" "}
                                    {formatRole(membership.role)}
                                </option>
                            ))}
                        </select>

                        <button
                            type="button"
                            disabled={
                                transferMembershipId === null ||
                                transferringOwnership
                            }
                            onClick={() => void handleOwnershipTransfer()}
                            className="inline-flex items-center justify-center gap-2 rounded-lg bg-eirdom-moscow-midnight px-4 py-2 text-sm font-medium text-eirdom-natural-linen transition-colors hover:bg-eirdom-moscow-midnight/90 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <Shield size={16} />

                            {transferringOwnership
                                ? "Transferring..."
                                : "Transfer ownership"}
                        </button>
                    </div>

                    {ownershipCandidates.length === 0 && (
                        <p className="mt-3 text-xs text-eirdom-muted">
                            There are no other active household members eligible
                            to receive ownership.
                        </p>
                    )}

                    <div className="mt-4 rounded-lg border border-eirdom-brass/40 bg-eirdom-brass/10 p-3">
                        <p className="text-xs text-eirdom-moscow-midnight">
                            Ownership transfer changes the highest level of
                            household access. The new Owner will be able to
                            manage administrators, members, household settings,
                            and future ownership transfers.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function SettingsPage() {
    const { user, refreshUser } = useAuth();

    const {
        activeHousehold: household,
        loading,
        error: householdError,
        refreshActiveHousehold,
    } = useHousehold();

    const [activeSection, setActiveSection] =
        useState<SettingsSection>("household");

    const currentMembership =
        user && household
            ? household.members.find((member) => member.user.id === user.id)
            : undefined;

    const canManageHousehold =
        currentMembership?.role === "owner" ||
        currentMembership?.role === "administrator";

    const navigationButtonClass = (section: SettingsSection) =>
        activeSection === section
            ? "flex w-full items-center gap-3 rounded-lg bg-eirdom-niebla-azul/20 px-3 py-3 text-left text-sm font-medium text-eirdom-moscow-midnight"
            : "flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm text-eirdom-muted transition-colors hover:bg-eirdom-niebla-azul/10 hover:text-eirdom-moscow-midnight";

    return (
        <div className="min-h-screen bg-eirdom-surface">
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <header>
                    <p className="text-sm font-medium text-eirdom-muted">
                        Settings
                    </p>

                    <h1 className="mt-1 text-3xl font-semibold text-eirdom-moscow-midnight">
                        Steward settings
                    </h1>

                    <p className="mt-2 text-sm text-eirdom-muted">
                        Manage household configuration, membership, account
                        security, and Steward preferences.
                    </p>
                </header>

                {householdError && (
                    <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">
                        <p className="text-sm text-red-700">{householdError}</p>
                    </div>
                )}

                <div className="mt-8 grid gap-6 lg:grid-cols-4">
                    <aside className="lg:col-span-1">
                        <nav className="space-y-2 rounded-xl border border-eirdom-border/40 bg-white/60 p-3 shadow-sm">
                            <button
                                type="button"
                                onClick={() => setActiveSection("household")}
                                className={navigationButtonClass("household")}
                            >
                                <Building2 size={18} />
                                Household settings
                            </button>

                            <button
                                type="button"
                                onClick={() => setActiveSection("members")}
                                className={navigationButtonClass("members")}
                            >
                                <Users size={18} />
                                Member administration
                            </button>

                            <div className="my-2 border-t border-eirdom-border/30" />

                            <button
                                type="button"
                                onClick={() => setActiveSection("account")}
                                className={navigationButtonClass("account")}
                            >
                                <UserRound size={18} />
                                Account
                            </button>

                            <button
                                type="button"
                                onClick={() => setActiveSection("security")}
                                className={navigationButtonClass("security")}
                            >
                                <KeyRound size={18} />
                                Password & security
                            </button>

                            <div className="my-2 border-t border-eirdom-border/30" />

                            <button
                                type="button"
                                onClick={() => setActiveSection("application")}
                                className={navigationButtonClass("application")}
                            >
                                <Settings size={18} />
                                Application settings
                            </button>
                        </nav>
                    </aside>

                    <main className="space-y-6 lg:col-span-3">
                        {activeSection === "household" && (
                            <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                        <Building2 size={22} />
                                    </div>

                                    <div>
                                        <p className="text-sm font-medium text-eirdom-muted">
                                            Household
                                        </p>

                                        <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                            Household settings
                                        </h2>

                                        <p className="mt-2 text-sm text-eirdom-muted">
                                            Update the basic information used to
                                            identify this household or property
                                            throughout Steward.
                                        </p>
                                    </div>
                                </div>

                                {loading ? (
                                    <p className="mt-6 text-sm text-eirdom-muted">
                                        Loading household settings...
                                    </p>
                                ) : !household ? (
                                    <p className="mt-6 text-sm text-eirdom-muted">
                                        No household is currently selected.
                                    </p>
                                ) : !canManageHousehold ? (
                                    <div className="mt-6 rounded-lg border border-eirdom-border/40 bg-eirdom-niebla-azul/10 p-4">
                                        <p className="text-sm text-eirdom-muted">
                                            Only household owners and
                                            administrators may change household
                                            settings.
                                        </p>
                                    </div>
                                ) : (
                                    <HouseholdSettingsForm
                                        key={`${household.id}-${household.updated_at}`}
                                        household={household}
                                        refreshActiveHousehold={
                                            refreshActiveHousehold
                                        }
                                    />
                                )}
                            </section>
                        )}

                        {activeSection === "members" && (
                            <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                        <Users size={22} />
                                    </div>

                                    <div>
                                        <p className="text-sm font-medium text-eirdom-muted">
                                            Household
                                        </p>

                                        <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                            Member administration
                                        </h2>

                                        <p className="mt-2 text-sm text-eirdom-muted">
                                            Manage invitations, household roles,
                                            and access.
                                        </p>
                                    </div>
                                </div>

                                {loading ? (
                                    <p className="mt-6 text-sm text-eirdom-muted">
                                        Loading household members...
                                    </p>
                                ) : !household ||
                                  !user ||
                                  !currentMembership ? (
                                    <p className="mt-6 text-sm text-eirdom-muted">
                                        Household membership information is not
                                        available.
                                    </p>
                                ) : !canManageHousehold ? (
                                    <div className="mt-6 rounded-lg border border-eirdom-border/40 bg-eirdom-niebla-azul/10 p-4">
                                        <p className="text-sm text-eirdom-muted">
                                            Only household owners and
                                            administrators may manage household
                                            members.
                                        </p>
                                    </div>
                                ) : (
                                    <MemberAdministration
                                        key={household.id}
                                        household={household}
                                        currentUserId={user.id}
                                        currentUserRole={currentMembership.role}
                                        refreshActiveHousehold={
                                            refreshActiveHousehold
                                        }
                                    />
                                )}
                            </section>
                        )}

                        {activeSection === "account" && (
                            <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                        <UserRound size={22} />
                                    </div>

                                    <div>
                                        <p className="text-sm font-medium text-eirdom-muted">
                                            Account
                                        </p>

                                        <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                            Profile settings
                                        </h2>

                                        <p className="mt-2 text-sm text-eirdom-muted">
                                            Manage your personal information and
                                            Steward sign-in identity.
                                        </p>
                                    </div>
                                </div>

                                {!user ? (
                                    <p className="mt-6 text-sm text-eirdom-muted">
                                        Account information is not available.
                                    </p>
                                ) : (
                                    <AccountSettingsForm
                                        key={`${user.id}-${user.username}-${user.email}-${user.first_name}-${user.last_name}`}
                                        user={user}
                                        refreshUser={refreshUser}
                                    />
                                )}
                            </section>
                        )}

                        {activeSection === "security" && (
                            <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                        <KeyRound size={22} />
                                    </div>

                                    <div>
                                        <p className="text-sm font-medium text-eirdom-muted">
                                            Account
                                        </p>

                                        <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                            Password &amp; security
                                        </h2>

                                        <p className="mt-2 text-sm text-eirdom-muted">
                                            Change the password used to sign in
                                            to Steward.
                                        </p>
                                    </div>
                                </div>

                                <PasswordSecurityForm />
                            </section>
                        )}

                        {activeSection === "application" && (
                            <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-eirdom-niebla-azul/20 text-eirdom-moscow-midnight">
                                        <Settings size={22} />
                                    </div>

                                    <div>
                                        <p className="text-sm font-medium text-eirdom-muted">
                                            Steward
                                        </p>

                                        <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                            Application settings
                                        </h2>

                                        <p className="mt-2 text-sm text-eirdom-muted">
                                            Application-wide preferences will
                                            live here as Steward grows.
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-6 rounded-lg border border-eirdom-border/30 bg-eirdom-niebla-azul/10 p-4">
                                    <p className="text-sm text-eirdom-muted">
                                        No application settings are available
                                        yet.
                                    </p>
                                </div>
                            </section>
                        )}
                    </main>
                </div>
            </div>
        </div>
    );
}
