import { User, WebStorageStateStore } from "oidc-client-ts";
import type { AuthProviderProps } from "react-oidc-context";

const AUTHORITY = "http://localhost:8080/realms/trading";
const CLIENT_ID = "trading-frontend";

export const oidcConfig: AuthProviderProps = {
  authority: AUTHORITY,
  client_id: CLIENT_ID,
  redirect_uri: `${window.location.origin}/`,
  post_logout_redirect_uri: `${window.location.origin}/`,
  scope: "openid profile",
  // sessionStorage (the default, made explicit): cleared when the tab closes
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
  // Remove ?code=...&state=... from the address bar after login
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname);
  },
};

// For code outside React (api.ts): read the signed-in user from storage
export function getAccessToken(): string | undefined {
  const stored = sessionStorage.getItem(`oidc.user:${AUTHORITY}:${CLIENT_ID}`);
  return stored ? User.fromStorageString(stored).access_token : undefined;
}

// UI hint only: the server checks roles on every request
export function rolesOf(user: User | null | undefined): string[] {
  if (!user) return [];
  const payload = user.access_token.split(".")[1];
  const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
  const claims: { realm_access?: { roles?: string[] } } = JSON.parse(json);
  return claims.realm_access?.roles ?? [];
}
