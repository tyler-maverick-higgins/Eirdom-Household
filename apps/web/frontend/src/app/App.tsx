import Sidebar from "../components/layout/Sidebar"
import { Route, Routes } from "react-router-dom"
import {
    DashboardPage,
    HouseholdPage,
    TasksPage,
    MealsPage,
    InventoryPage,
    MaintenancePage,
    FinancesPage,
    SettingsPage,
} from "../pages"

export default function App() {
    return (
        <div className="flex min-h-screen items-stretch">
            <Sidebar />

            <main className="flex-1">
                <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/household" element={<HouseholdPage />} />
                    <Route path="/tasks" element={<TasksPage />} />
                    <Route path="/meals" element={<MealsPage />} />
                    <Route path="/inventory" element={<InventoryPage />} />
                    <Route path="/maintenance" element={<MaintenancePage />} />
                    <Route path="/finances" element={<FinancesPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Routes>
            </main>
        </div>
    );
}
