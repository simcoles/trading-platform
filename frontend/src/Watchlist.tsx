import {
  Alert,
  Box,
  Button,
  Chip,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState, type SubmitEvent } from "react";
import { addToWatchlist, getWatchlist, removeFromWatchlist } from "./api";

function errorMessage(err: unknown): string {
  if (err instanceof Error) {
    return err.message;
  }
  return "Something went wrong";
}

export default function Watchlist() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false); // disables the form while a request is in flight

  // Initial load: same ignore pattern as PriceGrid
  useEffect(() => {
    let ignore = false;
    const loadWatchlist = async () => {
      try {
        const data = await getWatchlist();
        if (!ignore) {
          setSymbols(data);
        }
      } catch (err) {
        if (!ignore) {
          setError(errorMessage(err));
        }
      }
    };
    loadWatchlist();

    return () => {
      ignore = true;
    };
  }, []);

  // Used after every successful add/remove: the server is the source of truth
  async function refresh() {
    const data = await getWatchlist();
    setSymbols(data);
  }

  async function handleAdd(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault(); // stop the browser's full-page form submit
    setBusy(true);
    try {
      await addToWatchlist(input);
      setInput("");
      setError(null);
      await refresh();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(symbol: string) {
    setBusy(true);
    try {
      await removeFromWatchlist(symbol);
      await refresh();
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Stack spacing={2}>
      <Box
        component="form"
        onSubmit={handleAdd}
        sx={{ display: "flex", gap: 1 }}
      >
        <TextField
          label="Symbol"
          size="small"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <Button type="submit" variant="contained" disabled={busy}>
          Add
        </Button>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Stack direction="row" spacing={1}>
        {symbols.map((symbol) => (
          <Chip
            key={symbol}
            label={symbol}
            onDelete={() => handleRemove(symbol)}
            disabled={busy}
          />
        ))}
        {symbols.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No symbols yet
          </Typography>
        )}
      </Stack>
    </Stack>
  );
}
