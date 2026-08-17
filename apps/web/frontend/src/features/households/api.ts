import { api } from "../../lib/api";

export type Household = {
    id: number;
    name: string;
    created_at: string;
    updated_at: string;
};

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

export async function getHouseholds() {
    const response = await api.get<Household[]>("/households/");

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
