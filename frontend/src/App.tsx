import PriceGrid from "./PriceGrid";
import Watchlist from "./Watchlist";
import { Stack, Typography, Container } from "@mui/material";

function App() {
  return (
    <Container maxWidth="md" component="main" sx={{ py: 4 }}>
      <Stack spacing={4}>
        <Typography variant="h4" component="h1">
          Trading Platform
        </Typography>
        <Typography variant="h5" component="h2">
          Prices
        </Typography>
        <PriceGrid />
        <Typography variant="h5" component="h2">
          Watchlist
        </Typography>
        <Watchlist />
      </Stack>
    </Container>
  );
}

export default App;
