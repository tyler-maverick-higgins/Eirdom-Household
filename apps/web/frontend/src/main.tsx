import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./features/auth/AuthProvider";
import { HouseholdProvider } from "./features/households/HouseholdProvider";

import App from "./app/App";
import "./styles/globals.css";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <AuthProvider>
                <HouseholdProvider>
                    <App />
                </HouseholdProvider>
            </AuthProvider>
        </BrowserRouter>
    </StrictMode>,
);
