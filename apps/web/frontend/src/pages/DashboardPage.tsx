import {
    CalendarCheck2,
    UtensilsCrossed,
    WalletCards,
    Wrench,
} from "lucide-react";

import { Link } from "react-router-dom";

export default function DashboardPage() {
    const now = new Date();

    const formattedDate = now.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
    });

    const hour = now.getHours();

    const greeting =
        hour < 12
            ? "Good morning"
            : hour < 18
              ? "Good afternoon"
              : "Good evening";

    return (
        <div className="min-h-screen bg-eirdom-surface">
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <header>
                    <p className="text-sm font-medium text-eirdom-muted">
                        {formattedDate}
                    </p>

                    <h1 className="mt-1 text-3xl font-semibold text-eirdom-moscow-midnight">
                        {greeting}, Tyler
                    </h1>

                    <p className="mt-2 text-sm text-eirdom-muted">
                        Here&apos;s what&apos;s happening around your household.
                    </p>
                </header>

                <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <Link
                        to="tasks"
                        className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                    >
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-eirdom-muted">
                                Open tasks
                            </p>

                            <CalendarCheck2
                                size={20}
                                className="text-eirdom-moscow-midnight/70"
                            />
                        </div>
                        <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">
                            4
                        </p>
                        <p className="mt-1 text-sm text-eirdom-muted">
                            2 due today
                        </p>
                    </Link>

                    <Link
                        to="maintenance"
                        className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                    >
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-eirdom-muted">
                                Maintenance
                            </p>

                            <Wrench
                                size={20}
                                className="text-eirdom-moscow-midnight/70"
                            />
                        </div>
                        <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">
                            2
                        </p>
                        <p className="mt-1 text-sm text-eirdom-muted">
                            Coming up this month
                        </p>
                    </Link>

                    <Link
                        to="meals"
                        className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                    >
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-eirdom-muted">
                                Tonight&apos;s meal
                            </p>

                            <UtensilsCrossed
                                size={20}
                                className="text-eirdom-moscow-midnight/70"
                            />
                        </div>
                        <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">
                            1
                        </p>
                        <p className="mt-3 text-lg font-semibold text-eirdom-moscow-midnight">
                            Chicken Stroganoff
                        </p>
                        <p className="mt-1 text-sm text-eirdom-muted">
                            Planned for 6:30 PM
                        </p>
                    </Link>

                    <Link
                        to="finances"
                        className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                    >
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-eirdom-muted">
                                Monthly spending
                            </p>

                            <WalletCards
                                size={20}
                                className="text-eirdom-moscow-midnight/70"
                            />
                        </div>
                        <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">
                            $3,842
                        </p>
                        <p className="mt-1 text-sm text-eirdom-muted">
                            62% of household budget
                        </p>
                    </Link>
                </div>

                <div className="mt-6 grid gap-6 lg:grid-cols-5">
                    <section className="rounded-xl border border-eirdom-border/40 bg-eirdom-niebla-azul/5 p-6 shadow-sm lg:col-span-3">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-eirdom-muted">
                                    Today
                                </p>

                                <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                    What needs your attention
                                </h2>
                            </div>
                        </div>

                        <div className="mt-6 space-y-3">
                            <div className="flex items-center justify-between rounded-lg px-3 py-3 transition-colors hover:bg-eirdom-niebla-azul/10">
                                <div>
                                    <p className="text-sm font-medium text-eirdom-moscow-midnight">
                                        Take garbage out
                                    </p>
                                    <p className="mt-0.5 text-xs text-eirdom-muted">
                                        Task · Due tonight
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center justify-between rounded-lg px-3 py-3 transition-colors hover:bg-eirdom-niebla-azul/10">
                                <div>
                                    <p className="text-sm font-medium text-eirdom-moscow-midnight">
                                        Replace furnace filter
                                    </p>
                                    <p className="mt-0.5 text-xs text-eirdom-muted">
                                        Maintenance · Due in 5 days
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center justify-between rounded-lg px-3 py-3 transition-colors hover:bg-eirdom-niebla-azul/10">
                                <div>
                                    <p className="text-sm font-medium text-eirdom-moscow-midnight">
                                        Internet bill due
                                    </p>
                                    <p className="mt-0.5 text-xs text-eirdom-muted">
                                        Finance · Due Friday
                                    </p>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-2">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-eirdom-muted">
                                    This week
                                </p>

                                <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                    Meals
                                </h2>
                            </div>

                            <Link
                                to="meals"
                                className="text-sm font-medium text-eirdom-blue hover:text-eirdom-blue/80"
                            >
                                View all meals
                            </Link>
                        </div>

                        <div className="mt-6 space-y-4">
                            <div className="flex items-center justify-between rounded-lg px-3 py-2 transition-colors hover:bg-eirdom-niebla-azul/10">
                                <span className="text-sm text-eirdom-muted">
                                    Mon
                                </span>
                                <span className="text-sm font-medium text-eirdom-moscow-midnight">
                                    Chicken Stroganoff
                                </span>
                            </div>

                            <div className="flex items-center justify-between rounded-lg px-3 py-2 transition-colors hover:bg-eirdom-niebla-azul/10">
                                <span className="text-sm text-eirdom-muted">
                                    Tue
                                </span>
                                <span className="text-sm font-medium text-eirdom-moscow-midnight">
                                    Salmon &amp; asparagus
                                </span>
                            </div>

                            <div className="flex items-center justify-between rounded-lg px-3 py-2 transition-colors hover:bg-eirdom-niebla-azul/10">
                                <span className="text-sm text-eirdom-muted">
                                    Wed
                                </span>
                                <span className="text-sm font-medium text-eirdom-moscow-midnight">
                                    Open
                                </span>
                            </div>
                        </div>
                    </section>

                    <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-5">
                        <div>
                            <p className="text-sm font-medium text-eirdom-muted">
                                Household
                            </p>

                            <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                                At a glance
                            </h2>
                        </div>

                        <div className="mt-6 grid gap-4 md:grid-cols-3">
                            <Link
                                to="inventory"
                                className="rounded-lg bg-eirdom-niebla-azul/10 p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:bg-eirdom-niebla-azul/15 hover:shadow-sm"
                            >
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Inventory
                                </p>

                                <p className="mt-2 text-sm font-medium text-eirdom-moscow-midnight">
                                    127 tracked items
                                </p>

                                <p className="mt-1 text-sm text-eirdom-muted">
                                    3 running low
                                </p>
                            </Link>

                            <Link
                                to="maintenance"
                                className="rounded-lg bg-eirdom-niebla-azul/10 p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:bg-eirdom-niebla-azul/15 hover:shadow-sm"
                            >
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Home
                                </p>

                                <p className="mt-2 text-sm font-medium text-eirdom-moscow-midnight">
                                    8 maintenance items
                                </p>

                                <p className="mt-1 text-sm text-eirdom-muted">
                                    2 coming up this month
                                </p>
                            </Link>

                            <Link
                                to="finances"
                                className="rounded-lg bg-eirdom-niebla-azul/10 p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:bg-eirdom-niebla-azul/15 hover:shadow-sm"
                            >
                                <p className="text-xs font-semibold uppercase tracking-wide text-eirdom-muted">
                                    Finances
                                </p>

                                <p className="mt-2 text-sm font-medium text-eirdom-moscow-midnight">
                                    $3,842 spent
                                </p>

                                <p className="mt-1 text-sm text-eirdom-muted">
                                    62% of monthly budget
                                </p>
                            </Link>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
