import { api } from "../../lib/api";

export type HouseholdType = "primary" | "vacation" | "rental" | "other";

export type HouseholdRole = "owner" | "administrator" | "member" | "guest";

export type Household = {
    id: number;
    name: string;
    email: string;
    household_type: HouseholdType;
    created_at: string;
    updated_at: string;
};

export type HouseholdMemberUser = {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
};

export type HouseholdMember = {
    id: number;
    user: HouseholdMemberUser;
    role: HouseholdRole;
    is_active: boolean;
    created_at: string;
    updated_at: string;
};

export type UpdateHouseholdMembershipInput = {
    role?: "administrator" | "member" | "guest";
    is_active?: boolean;
};

export type CreateHouseholdInvitationInput = {
    email: string;
    role: "member" | "administrator";
};

export type HouseholdInvitation = {
    id: number;
    email: string;
    role: HouseholdRole;
    status: string;
    invited_by: number;
    expires_at: string | null;
    last_sent_at: string | null;
    created_at: string;
    updated_at: string;
};

export type UpdateHouseholdInput = {
    name: string;
    email: string;
    household_type: HouseholdType;
};

export type HouseholdDetail = Household & {
    members: HouseholdMember[];
    pending_invitations: HouseholdInvitation[];
};

export type TransferHouseholdOwnershipInput = {
    membership_id: number;
};

export async function getHouseholds() {
    const response = await api.get<Household[]>("/households/");

    return response.data;
}

export async function getHouseholdDetail(householdId: number) {
    const response = await api.get<HouseholdDetail>(
        `/households/${householdId}/`,
    );

    return response.data;
}

export async function updateHousehold(
    householdId: number,
    input: UpdateHouseholdInput,
) {
    const response = await api.patch<Household>(
        `/households/${householdId}/settings/`,
        input,
    );

    return response.data;
}

export async function getHouseholdMembers(householdId: number) {
    const response = await api.get<HouseholdMember[]>(
        `/households/${householdId}/members/`,
    );

    return response.data;
}

export async function updateHouseholdMembership(
    householdId: number,
    membershipId: number,
    input: UpdateHouseholdMembershipInput,
) {
    const response = await api.patch<HouseholdMember>(
        `/households/${householdId}/members/${membershipId}`,
        input,
    );

    return response.data;
}

export async function createHouseholdInvitation(
    householdId: number,
    input: CreateHouseholdInvitationInput,
) {
    const response = await api.post<HouseholdInvitation>(
        `/households/${householdId}/invitations/`,
        input,
    );

    return response.data;
}

export type HouseholdInvitationValidation = {
    household_name: string;
    email: string;
    role: "administrator" | "member";
    inviter_name: string;
    expires_at: string;
    account_exists: boolean;
};

export type HouseholdInvitationAcceptance = {
    household_id: number;
    household_name: string;
    membership_id: number;
    role: "administrator" | "member";
    status: "accepted";
};

export async function validateHouseholdInvitation(token: string) {
    const response = await api.get<HouseholdInvitationValidation>(
        `/households/invitations/${encodeURIComponent(token)}/`,
    );

    return response.data;
}

export async function acceptHouseholdInvitation(token: string) {
    const response = await api.post<HouseholdInvitationAcceptance>(
        `/households/invitations/${encodeURIComponent(token)}/accept/`,
        {},
    );

    return response.data;
}

export async function resendHouseholdInvitation(invitationId: number) {
    const response = await api.post<HouseholdInvitation>(
        `/households/invitations/${invitationId}/resend/`,
        {},
    );

    return response.data;
}

export async function cancelHouseholdInvitation(invitationId: number) {
    const response = await api.post<HouseholdInvitation>(
        `/households/invitations/${invitationId}/cancel/`,
        {},
    );

    return response.data;
}

export async function transferHouseholdOwnership(
    householdId: number,
    input: TransferHouseholdOwnershipInput,
) {
    const response = await api.post<HouseholdMember>(
        `/households/${householdId}/ownership/transfer/`,
        input,
    );

    return response.data;
}
