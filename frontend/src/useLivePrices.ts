import { useEffect, useState } from "react";
import { WS_URL, type PriceResponse } from "./api";
import { appendTick, emptyHistory, type PriceHistory } from "./priceHistory";

const BASE_DELAY_MS = 500; // 0.5 seconds
const MAX_DELAY_MS = 10_000; // 10 seconds
const MAX_ATTEMPTS = 8; // Maximum number of reconnection attempts

// What the server sends: {"AAPL": 150.42, ...}
type PriceTick = Record<string, number>;

export type LiveStatus = "connecting" | "reconnecting" | "open" | "closed";

function tickToRows(tick: PriceTick): PriceResponse[] {
  return Object.entries(tick).map(([symbol, price]) => ({
    symbol,
    price,
    currency: "USD",
  }));
}
function backoffDelay(attempt: number): number {
  const exponentialDelay = BASE_DELAY_MS * Math.pow(2, attempt);
  const cappedDelay = Math.min(exponentialDelay, MAX_DELAY_MS);
  const jitteredDelay = cappedDelay * (0.5 + Math.random() * 0.5); // Random factor between 0.5 and 1
  return jitteredDelay;
}

export function useLivePrices(): {
  prices: PriceResponse[];
  history: PriceHistory;
  status: LiveStatus;
} {
  const [prices, setPrices] = useState<PriceResponse[]>([]);
  const [history, setHistory] = useState<PriceHistory>(emptyHistory);
  const [status, setStatus] = useState<LiveStatus>("connecting");

  useEffect(() => {
    let ignore = false;
    let ws: WebSocket | null = null;
    let retryTimer: ReturnType<typeof setTimeout> | undefined;
    let attempt = 0;

    const connect = () => {
      ws = new WebSocket(WS_URL);
      ws.onopen = () => {
        if (!ignore) {
          attempt = 0; // Reset attempt counter on successful connection
          setStatus("open");
        }
      };

      ws.onmessage = (event: MessageEvent<string>) => {
        const tick: PriceTick = JSON.parse(event.data);
        if (!ignore) {
          setPrices(tickToRows(tick));
          // Timestamp on arrival, in the event handler (not during render)
          const now = Date.now();
          setHistory((previous) => appendTick(previous, tick, now));
        }
      };

      ws.onclose = () => {
        if (ignore) return;
        if (attempt >= MAX_ATTEMPTS) {
          setStatus("closed");
          return;
        }
        setStatus("reconnecting");
        const delay = backoffDelay(attempt);
        retryTimer = setTimeout(connect, delay);
        attempt++;
      };
    };

    connect();

    return () => {
      ignore = true;
      clearTimeout(retryTimer);
      ws?.close();
    };
  }, []);

  return { prices, history, status };
}
