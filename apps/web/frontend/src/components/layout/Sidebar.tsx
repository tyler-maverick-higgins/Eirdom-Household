import { useState } from "react"
import { NavLink } from "react-router-dom"
import {
  Boxes,
  ChevronFirst,
  ChevronLast,
  House,
  LayoutDashboard,
  ListChecks,
  LogOut,
  MoreVertical,
  Settings,
  Settings2,
  User,
  UtensilsCrossed,
  WalletCards,
  Wrench,
} from "lucide-react"

const navigation = [
  { name: "Overview", path: "/", icon: LayoutDashboard },
  { name: "Household", path: "/household", icon: House },
  { name: "Tasks", path: "/tasks", icon: ListChecks },
  { name: "Meals", path: "/meals", icon: UtensilsCrossed },
  { name: "Inventory", path: "/inventory", icon: Boxes },
  { name: "Maintenance", path: "/maintenance", icon: Wrench },
  { name: "Finances", path: "/finances", icon: WalletCards },
  { name: "Settings", path: "/settings", icon: Settings },
]

export default function Sidebar() {
  const [expanded, setExpanded] = useState(true)
  const [accountOpen, setAccountOpen] = useState(false)

  return (
    <aside
        className={`sticky top-0 h-screen shrink-0 bg-eirdom-moscow-midnight text-eirdom-natural-linen transition-all duration-300 ${
            expanded ? "w-64" : "w-20"
        }`}
    >
      <nav className="flex h-full flex-col">
        <div
        className={`flex items-center p-6 ${
            expanded ? "justify-between" : "justify-center"
        }`}
        >
        {expanded && (
            <div>
            <h1 className="text-xl font-semibold">Eirdom</h1>
            <p className="text-sm text-eirdom-stone">Household</p>
            </div>
        )}

        <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            className="rounded-md p-2 text-eirdom-niebla-azul transition-colors hover:bg-eirdom-niebla-azul/50 hover:text-eirdom-natural-linen"
            aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
        >
            {expanded ? <ChevronFirst size={20} /> : <ChevronLast size={20} />}
        </button>
        </div>

        <ul className="mt-4 flex-1 space-y-1 px-3">
          {navigation.map((item) => {
            const Icon = item.icon

            return (
              <li key={item.name}>
                <NavLink
                  to={item.path}
                  end={item.path === "/"}
                  title={!expanded ? item.name : undefined}
                  className={({ isActive }) =>
                    `flex w-full items-center rounded-md px-3 py-2 text-sm transition-colors ${
                        expanded ? "px-3" : "justify-center px-2"
                    } ${
                      isActive
                        ? "bg-eirdom-niebla-azul text-eirdom-moscow-midnight"
                        : "text-eirdom-stone hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-natural-linen"
                    }`
                  }
                >
                  <Icon size={20} className="shrink-0" />

                  {expanded && (
                    <span className="ml-3">{item.name}</span>
                  )}

                </NavLink>
              </li>
            )
          })}
        </ul>

        <div className="relative border-t border-eirdom-niebla-azul/30 p-3">
            {accountOpen && expanded && (
                <div className="absolute bottom-full left-3 right-3 mb-2 rounded-md border border-eirdom-niebla-azul/40 bg-eirdom-moscow-midnight p-2 shadow-lg">
                <button
                    type="button"
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-eirdom-stone transition-colors hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-natural-linen"
                >
                    <User size={18} />
                    <span>Profile</span>
                </button>

                <button
                    type="button"
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-eirdom-stone transition-colors hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-natural-linen"
                >
                    <Settings2 size={18} />
                    <span>Account settings</span>
                </button>

                <div className="my-1 border-t border-eirdom-niebla-azul/40" />

                <button
                    type="button"
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-eirdom-stone transition-colors hover:bg-eirdom-niebla-azul/20 hover:text-eirdom-natural-linen"
                >
                    <LogOut size={18} />
                    <span>Sign out</span>
                </button>
                </div>
            )}

            <button
                type="button"
                onClick={() => setAccountOpen((current) => !current)}
                className={`flex w-full items-center rounded-md transition-colors hover:bg-eirdom-niebla-azul/20 ${
                expanded ? "gap-3 px-2 py-2" : "justify-center p-2"
                }`}
            >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-eirdom-niebla-azul/20 font-semibold text-eirdom-natural-linen">
                TH
                </div>

                {expanded && (
                <>
                    <div className="min-w-0 flex-1 text-left">
                    <p className="truncate text-sm font-semibold text-eirdom-natural-linen">
                        Tyler Higgins
                    </p>
                    <p className="truncate text-xs text-eirdom-stone">
                        Administrator
                    </p>
                    </div>

                    <MoreVertical
                    size={18}
                    className="shrink-0 text-eirdom-niebla-azul"
                    />
                </>
                )}
            </button>
            </div>
      </nav>
    </aside>
  )
}
