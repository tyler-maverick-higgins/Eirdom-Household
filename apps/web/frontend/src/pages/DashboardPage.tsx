export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-eirdom-surface">
      <div className="mx-auto max-w-7xl p-8">
        <header>
          <p className="text-sm font-medium text-eirdom-muted">
            Monday, August 10
          </p>

          <h1 className="mt-1 text-3xl font-semibold text-eirdom-moscow-midnight">
            Good afternoon, Tyler
          </h1>

          <p className="mt-2 text-sm text-eirdom-muted">
            Here&apos;s what&apos;s happening around your household.
          </p>
        </header>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm">
            <p className="text-sm font-medium text-eirdom-muted">Tasks due</p>
            <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">4</p>
            <p className="mt-1 text-sm text-eirdom-muted">2 due today</p>
          </div>

          <div className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm">
            <p className="text-sm font-medium text-eirdom-muted">Maintenance</p>
            <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">2</p>
            <p className="mt-1 text-sm text-eirdom-muted">Coming up this month</p>
          </div>

          <div className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm">
            <p className="text-sm font-medium text-eirdom-muted">Tonight&apos;s meal</p>
            <p className="mt-3 text-lg font-semibold text-eirdom-moscow-midnight">
              Chicken Stroganoff
            </p>
            <p className="mt-1 text-sm text-eirdom-muted">Planned for 6:30 PM</p>
          </div>

          <div className="rounded-xl border border-eirdom-border/40 bg-white/60 p-5 shadow-sm">
            <p className="text-sm font-medium text-eirdom-muted">Monthly spending</p>
            <p className="mt-3 text-3xl font-semibold text-eirdom-moscow-midnight">$3,842</p>
            <p className="mt-1 text-sm text-eirdom-muted">62% of household budget</p>
          </div>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-5">
          <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-eirdom-muted">Today</p>
                <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
                  What needs your attention
                </h2>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-3 rounded-lg px-3 py-3 hover:bg-eirdom-niebla-azul/10">
                <input type="checkbox" className="h-4 w-4" />
                <div>
                  <p className="text-sm font-medium text-eirdom-moscow-midnight">
                    Take garbage out
                  </p>
                  <p className="text-xs text-eirdom-muted">Due tonight</p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-lg px-3 py-3 hover:bg-eirdom-niebla-azul/10">
                <input type="checkbox" className="h-4 w-4" />
                <div>
                  <p className="text-sm font-medium text-eirdom-moscow-midnight">
                    Replace furnace filter
                  </p>
                  <p className="text-xs text-eirdom-muted">Maintenance</p>
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-2">
            <p className="text-sm font-medium text-eirdom-muted">This week</p>
            <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">Meals</h2>

            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-eirdom-muted">Mon</span>
                <span className="text-sm font-medium text-eirdom-moscow-midnight">
                  Chicken Stroganoff
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-eirdom-muted">Tue</span>
                <span className="text-sm font-medium text-eirdom-moscow-midnight">
                  Salmon &amp; asparagus
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-eirdom-muted">Wed</span>
                <span className="text-sm font-medium text-eirdom-moscow-midnight">Open</span>
              </div>
            </div>
          </section>

          <section className="rounded-xl border border-eirdom-border/40 bg-white/60 p-6 shadow-sm lg:col-span-5">
            <p className="text-sm font-medium text-eirdom-muted">Household</p>

            <h2 className="mt-1 text-xl font-semibold text-eirdom-moscow-midnight">
              Needs your attention
            </h2>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-lg bg-eirdom-niebla-azul/10 p-4">
                <p className="text-sm font-medium text-eirdom-moscow-midnight">
                  Pantry inventory
                </p>
                <p className="mt-1 text-sm text-eirdom-muted">3 items are running low</p>
              </div>

              <div className="rounded-lg bg-eirdom-niebla-azul/10 p-4">
                <p className="text-sm font-medium text-eirdom-moscow-midnight">
                  Home maintenance
                </p>
                <p className="mt-1 text-sm text-eirdom-muted">
                  Furnace filter due in 5 days
                </p>
              </div>

              <div className="rounded-lg bg-eirdom-niebla-azul/10 p-4">
                <p className="text-sm font-medium text-eirdom-moscow-midnight">
                  Upcoming bill
                </p>
                <p className="mt-1 text-sm text-eirdom-muted">Internet bill due Friday</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
