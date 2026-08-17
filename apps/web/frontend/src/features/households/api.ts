import { api } from "../../lib/api";

export type CreateHouseholdInvitationInput = {
    email: string;
    role: "member" | "administrator";
};

export type HouseholdInvitation = {
    id: number;
    email: string;
    role: string;
    status: string;
    invited_by: number;
    created_at: string;
    updated_at: string;
};

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
