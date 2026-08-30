import { Route, Routes } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import {
    DashboardPage,
    FinancesPage,
    HouseholdPage,
    InventoryPage,
    InvitationAcceptPage,
    LoginPage,
    MaintenancePage,
    MealsPage,
    SettingsPage,
    TasksPage,
} from "../pages";

function ProtectedLayout() {
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

export default function App() {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
                path="/invitations/accept/:token"
                element={<InvitationAcceptPage />}
            />

            <Route element={<ProtectedRoute />}>
                <Route path="/*" element={<ProtectedLayout />} />
            </Route>
        </Routes>
    );
}
