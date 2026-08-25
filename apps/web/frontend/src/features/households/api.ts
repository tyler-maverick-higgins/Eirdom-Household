import { api } from "../../lib/api";

export type Household = {
    id: number;
    name: string;
    created_at: string;
    updated_at: string;
};

export type HouseholdMemberUser = {
  id: number,
  username: string;
  first_name: string;
  last_name: string;
  email: string;
};

export type HouseholdMember = {
  id: number;
  user: HouseholdMemberUser;
  role: "owner" | "administrator" | "member" | "guest";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

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

export type HouseholdDetail = Household & {
  members: HouseholdMember[];
  pending_invitations: HouseholdInvitation[];
}

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
