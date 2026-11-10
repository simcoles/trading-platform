import { Container, Stack, Typography } from "@mui/material";
import { useState } from "react";
import Orders from "./Orders";
import Portfolio from "./Portfolio";
import PriceGrid from "./PriceGrid";
import { useLivePrices } from "./useLivePrices";
import Watchlist from "./Watchlist";

function App() {
  // One WebSocket for the whole app, shared by everything that needs prices
  const { prices, status } = useLivePrices();
  // Bumped after each order so Portfolio knows to refetch
  const [ordersVersion, setOrdersVersion] = useState(0);

  return (
    <Container maxWidth="lg" component="main" sx={{ py: 4 }}>
      <Stack spacing={4}>
        <Typography variant="h4" component="h1">
          Trading Platform
        </Typography>

        <Typography variant="h5" component="h2">
          Prices
        </Typography>
        <PriceGrid prices={prices} status={status} />

        <Typography variant="h5" component="h2">
          Portfolio
        </Typography>
        <Portfolio prices={prices} refreshKey={ordersVersion} />

        <Typography variant="h5" component="h2">
          Orders
        </Typography>
        <Orders onPlaced={() => setOrdersVersion((v) => v + 1)} />

        <Typography variant="h5" component="h2">
          Watchlist
        </Typography>
        <Watchlist />
      </Stack>
    </Container>
  );
}

export default App;
