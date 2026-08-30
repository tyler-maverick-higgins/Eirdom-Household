import { createContext } from "react";

import type { Household, HouseholdDetail } from "./api";

export type HouseholdContextValue = {
    households: Household[];
    activeHousehold: HouseholdDetail | null;
    loading: boolean;
    error: string;
    setActiveHouseholdId: (householdId: number) => void;
    refreshActiveHousehold: () => Promise<void>;
};

export const HouseholdContext = createContext<
    HouseholdContextValue | undefined
>(undefined);
