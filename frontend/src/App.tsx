import { Alert, Button, Container, Stack, Typography } from "@mui/material";
import { useState } from "react";
import { useAuth } from "react-oidc-context";
import { rolesOf } from "./auth";
import Orders from "./Orders";
import Portfolio from "./Portfolio";
import PriceGrid from "./PriceGrid";
import { useLivePrices } from "./useLivePrices";
import Watchlist from "./Watchlist";

function App() {
  const auth = useAuth();
  // One WebSocket for the whole app, shared by everything that needs prices
  const { prices, status } = useLivePrices();
  // Bumped after each order so Portfolio knows to refetch
  const [ordersVersion, setOrdersVersion] = useState(0);

  const canTrade = rolesOf(auth.user).includes("trader");

  return (
    <Container maxWidth="lg" component="main" sx={{ py: 4 }}>
      <Stack spacing={4}>
        <Stack
          direction="row"
          sx={{ justifyContent: "space-between", alignItems: "center" }}
        >
          <Typography variant="h4" component="h1">
            Trading Platform
          </Typography>
          {auth.isAuthenticated && (
            <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
              <Typography>
                {auth.user?.profile.preferred_username} (
                {canTrade ? "trader" : "view only"})
              </Typography>
              <Button
                variant="outlined"
                onClick={() => void auth.signoutRedirect()}
              >
                Sign out
              </Button>
            </Stack>
          )}
        </Stack>

        <Typography variant="h5" component="h2">
          Prices
        </Typography>
        <PriceGrid prices={prices} status={status} />

        {auth.error && (
          <Alert severity="error">Sign-in failed: {auth.error.message}</Alert>
        )}

        {auth.isLoading ? (
          <Typography>Checking sign-in…</Typography>
        ) : !auth.isAuthenticated ? (
          <Stack spacing={2} sx={{ alignItems: "flex-start" }}>
            <Typography>Sign in to see your portfolio and orders.</Typography>
            <Button
              variant="contained"
              onClick={() => void auth.signinRedirect()}
            >
              Sign in
            </Button>
          </Stack>
        ) : (
          <>
            <Typography variant="h5" component="h2">
              Portfolio
            </Typography>
            <Portfolio prices={prices} refreshKey={ordersVersion} />

            <Typography variant="h5" component="h2">
              Orders
            </Typography>
            <Orders
              canTrade={canTrade}
              onPlaced={() => setOrdersVersion((v) => v + 1)}
            />
          </>
        )}

        <Typography variant="h5" component="h2">
          Watchlist
        </Typography>
        <Watchlist />
      </Stack>
    </Container>
  );
}

export default App;
