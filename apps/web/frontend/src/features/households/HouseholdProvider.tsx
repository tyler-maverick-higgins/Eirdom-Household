import { useEffect, useState, type ReactNode } from "react";

import { useAuth } from "../auth/useAuth";
import { getHouseholds, type Household } from "./api";
import { HouseholdContext } from "./householdContext";

type HouseholdState = {
    userId: number | null;
    households: Household[];
    error: string;
};

export function HouseholdProvider({ children }: { children: ReactNode }) {
    const { user, loading: authLoading } = useAuth();

    const [householdState, setHouseholdState] = useState<HouseholdState>({
        userId: null,
        households: [],
        error: "",
    });

    const [activeHouseholdId, setActiveHouseholdId] = useState<number | null>(
        null,
    );

    useEffect(() => {
        if (!user) {
            return;
        }

        let cancelled = false;

        getHouseholds()
            .then((householdData) => {
                if (cancelled) {
                    return;
                }

                setHouseholdState({
                    userId: user.id,
                    households: householdData,
                    error: "",
                });

                setActiveHouseholdId((currentId) => {
                    const currentStillExists =
                        currentId !== null &&
                        householdData.some(
                            (household) => household.id === currentId,
                        );

                    if (currentStillExists) {
                        return currentId;
                    }

                    return householdData[0]?.id ?? null;
                });
            })
            .catch(() => {
                if (cancelled) {
                    return;
                }

                setHouseholdState({
                    userId: user.id,
                    households: [],
                    error: "Unable to load household information.",
                });

                setActiveHouseholdId(null);
            });

        return () => {
            cancelled = true;
        };
    }, [user]);

    const households =
        user && householdState.userId === user.id
            ? householdState.households
            : [];

    const error =
        user && householdState.userId === user.id ? householdState.error : "";

    const loading =
        authLoading || Boolean(user && householdState.userId !== user.id);

    const activeHousehold =
        households.find((household) => household.id === activeHouseholdId) ??
        null;

    return (
        <HouseholdContext.Provider
            value={{
                households,
                activeHousehold,
                loading,
                error,
                setActiveHouseholdId,
            }}
        >
            {children}
        </HouseholdContext.Provider>
    );
}
