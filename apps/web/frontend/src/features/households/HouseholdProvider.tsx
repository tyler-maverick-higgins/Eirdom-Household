import { useCallback, useEffect, useState, type ReactNode } from "react";

import { useAuth } from "../auth/useAuth";
import {
    getHouseholdDetail,
    getHouseholds,
    type Household,
    type HouseholdDetail,
} from "./api";
import { HouseholdContext } from "./householdContext";

type HouseholdState = {
    userId: number | null;
    households: Household[];
    error: string;
};

type HouseholdDetailState = {
    userId: number | null;
    householdId: number | null;
    household: HouseholdDetail | null;
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

    const [householdDetailState, setHouseholdDetailState] =
        useState<HouseholdDetailState>({
            userId: null,
            householdId: null,
            household: null,
            error: "",
        });

    useEffect(() => {
        if (!user) {
            return;
        }

        let cancelled = false;

        const loadHouseholds = async () => {
            try {
                const householdData = await getHouseholds();

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
            } catch {
                if (cancelled) {
                    return;
                }

                setHouseholdState({
                    userId: user.id,
                    households: [],
                    error: "Unable to load household information.",
                });

                setActiveHouseholdId(null);
            }
        };

        void loadHouseholds();

        return () => {
            cancelled = true;
        };
    }, [user]);

    useEffect(() => {
        if (!user || activeHouseholdId === null) {
            return;
        }

        let cancelled = false;

        const loadHouseholdDetail = async () => {
            try {
                const householdDetail =
                    await getHouseholdDetail(activeHouseholdId);

                if (cancelled) {
                    return;
                }

                setHouseholdDetailState({
                    userId: user.id,
                    householdId: activeHouseholdId,
                    household: householdDetail,
                    error: "",
                });
            } catch {
                if (cancelled) {
                    return;
                }

                setHouseholdDetailState({
                    userId: user.id,
                    householdId: activeHouseholdId,
                    household: null,
                    error: "Unable to load household details.",
                });
            }
        };

        void loadHouseholdDetail();

        return () => {
            cancelled = true;
        };
    }, [user, activeHouseholdId]);

    const refreshActiveHousehold = useCallback(async () => {
        if (!user || activeHouseholdId === null) {
            return;
        }

        try {
            const householdDetail = await getHouseholdDetail(activeHouseholdId);

            setHouseholdDetailState({
                userId: user.id,
                householdId: activeHouseholdId,
                household: householdDetail,
                error: "",
            });
        } catch {
            setHouseholdDetailState({
                userId: user.id,
                householdId: activeHouseholdId,
                household: null,
                error: "Unable to load household details.",
            });
        }
    }, [user, activeHouseholdId]);

    const households =
        user && householdState.userId === user.id
            ? householdState.households
            : [];

    const householdListError =
        user && householdState.userId === user.id ? householdState.error : "";

    const householdListLoading =
        Boolean(user) && householdState.userId !== user?.id;

    const detailMatchesActiveHousehold =
        Boolean(user) &&
        activeHouseholdId !== null &&
        householdDetailState.userId === user?.id &&
        householdDetailState.householdId === activeHouseholdId;

    const activeHousehold = detailMatchesActiveHousehold
        ? householdDetailState.household
        : null;

    const householdDetailError = detailMatchesActiveHousehold
        ? householdDetailState.error
        : "";

    const householdDetailLoading =
        Boolean(user) &&
        activeHouseholdId !== null &&
        !detailMatchesActiveHousehold;

    const loading =
        authLoading || householdListLoading || householdDetailLoading;

    const error = householdListError || householdDetailError;

    return (
        <HouseholdContext.Provider
            value={{
                households,
                activeHousehold,
                loading,
                error,
                setActiveHouseholdId,
                refreshActiveHousehold,
            }}
        >
            {children}
        </HouseholdContext.Provider>
    );
}
