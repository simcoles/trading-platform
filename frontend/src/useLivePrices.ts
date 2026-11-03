import { useEffect, useState } from "react";
import { WS_URL, type PriceResponse } from "./api";

// What the server sends: {"AAPL": 150.42, ...}
type PriceTick = Record<string, number>;

export type LiveStatus = "connecting" | "open" | "closed";

function tickToRows(tick: PriceTick): PriceResponse[] {
  return Object.entries(tick).map(([symbol, price]) => ({
    symbol,
    price,
    currency: "USD",
  }));
}

export function useLivePrices(): {
  prices: PriceResponse[];
  status: LiveStatus;
} {
  const [prices, setPrices] = useState<PriceResponse[]>([]);
  const [status, setStatus] = useState<LiveStatus>("connecting");

  useEffect(() => {
    let ignore = false;
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      if (!ignore) {
        setStatus("open");
      }
    };

    ws.onmessage = (event: MessageEvent<string>) => {
      const tick: PriceTick = JSON.parse(event.data);
      if (!ignore) {
        setPrices(tickToRows(tick));
      }
    };

    ws.onclose = () => {
      if (!ignore) {
        setStatus("closed");
      }
    };

    return () => {
      ignore = true;
      ws.close();
    };
  }, []);

  return { prices, status };
}
