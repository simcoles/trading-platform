import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { AuthProvider } from "react-oidc-context";
import { oidcConfig } from "./auth.ts";

ModuleRegistry.registerModules([AllCommunityModule]);
const theme = createTheme();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthProvider {...oidcConfig}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </AuthProvider>
  </StrictMode>,
);
