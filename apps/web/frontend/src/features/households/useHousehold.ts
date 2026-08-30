import { useContext } from "react";

import { HouseholdContext } from "./householdContext";

export function useHousehold() {
    const context = useContext(HouseholdContext);

    if (!context) {
        throw new Error(
            "useHousehold must be used within a HouseholdProvider.",
        );
    }

    return context;
}
