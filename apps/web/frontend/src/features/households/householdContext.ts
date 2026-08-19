import { createContext } from "react";

import type { Household } from "./api";

export type HouseholdContextValue = {
  households: Household[];
  activeHousehold: Household | null;
  loading: boolean;
  error: string;
  setActiveHouseholdId: (HouseholdId: number) => void;
};

export const HouseholdContext = createContext<HouseholdContextValue | undefined
>(undefined);
