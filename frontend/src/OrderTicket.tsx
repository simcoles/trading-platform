import {
  Alert,
  Box,
  Button,
  MenuItem,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { useState, type SubmitEvent } from "react";
import { placeOrder, type OrderResponse, type Side } from "./api";
import { formatMoney } from "./format";

const SYMBOLS = ["AAPL", "GOOGL", "AMZN"];

type Props = { onPlaced: (order: OrderResponse) => void };

export default function OrderTicket({ onPlaced }: Props) {
  const [symbol, setSymbol] = useState(SYMBOLS[0]);
  const [side, setSide] = useState<Side>("buy");
  const [quantity, setQuantity] = useState(""); // inputs give strings
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmation, setConfirmation] = useState<string | null>(null);

  // Client-side check for UX only; the server validates again (gt=0)
  const quantityNumber = Number(quantity);
  const quantityValid = Number.isInteger(quantityNumber) && quantityNumber > 0;

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setConfirmation(null);
    try {
      const order = await placeOrder({
        symbol,
        side,
        quantity: quantityNumber,
      });
      setConfirmation(
        `${order.side === "buy" ? "Bought" : "Sold"} ${order.quantity} ${order.symbol} at ${formatMoney(order.price)}`,
      );
      setQuantity("");
      onPlaced(order);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}
    >
      <TextField
        select
        label="Symbol"
        size="small"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        sx={{ minWidth: 120 }}
      >
        {SYMBOLS.map((s) => (
          <MenuItem key={s} value={s}>
            {s}
          </MenuItem>
        ))}
      </TextField>

      <ToggleButtonGroup
        exclusive
        size="small"
        value={side}
        // exclusive mode gives null when the selected button is clicked again
        onChange={(_e, value: Side | null) => value && setSide(value)}
        aria-label="Side"
      >
        <ToggleButton value="buy">Buy</ToggleButton>
        <ToggleButton value="sell">Sell</ToggleButton>
      </ToggleButtonGroup>

      <TextField
        label="Quantity"
        size="small"
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
        slotProps={{ htmlInput: { min: 1, step: 1 } }}
        sx={{ width: 120 }}
      />

      <Button
        type="submit"
        variant="contained"
        disabled={busy || !quantityValid}
      >
        Place order
      </Button>

      {error && (
        <Alert
          sx={{ width: "100%" }}
          severity="error"
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}
      {confirmation && (
        <Alert
          sx={{ width: "100%" }}
          severity="success"
          onClose={() => setConfirmation(null)}
        >
          {confirmation}
        </Alert>
      )}
    </Box>
  );
}
