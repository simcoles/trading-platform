// Live prices kept outside React. Components subscribe to just the slice
// they need with useSyncExternalStore, so a tick re-renders the price
// consumers only, not App and everything below it.
import { useSyncExternalStore } from "react";
import { WS_URL, type PriceResponse } from "./api";
import { appendTick, emptyHistory, type PriceHistory } from "./priceHistory";

const BASE_DELAY_MS = 500; // 0.5 seconds
const MAX_DELAY_MS = 10_000; // 10 seconds
const MAX_ATTEMPTS = 8; // Maximum number of reconnection attempts

// What the server sends: {"AAPL": 150.42, ...}
type PriceTick = Record<string, number>;

export type LiveStatus = "connecting" | "reconnecting" | "open" | "closed";

export type LiveState = {
  prices: PriceResponse[];
  history: PriceHistory;
  status: LiveStatus;
};

const initialState: LiveState = {
  prices: [],
  history: emptyHistory,
  status: "connecting",
};

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
  return cappedDelay * (0.5 + Math.random() * 0.5); // jitter: 50–100%
}

export function createPriceStore(
  createSocket: (url: string) => WebSocket = (url) => new WebSocket(url),
) {
  let state = initialState;
  const listeners = new Set<() => void>();
  let socket: WebSocket | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | undefined;
  let attempt = 0;

  // Always replace state with a new object; untouched slices keep their
  // identity, so their subscribers see "no change" and skip re-rendering
  function setState(changes: Partial<LiveState>) {
    state = { ...state, ...changes };
    listeners.forEach((listener) => listener());
  }

  function connect() {
    const ws = createSocket(WS_URL);
    socket = ws;

    ws.onopen = () => {
      attempt = 0;
      setState({ status: "open" });
    };

    ws.onmessage = (event: MessageEvent<string>) => {
      const tick: PriceTick = JSON.parse(event.data);
      setState({
        prices: tickToRows(tick),
        history: appendTick(state.history, tick, Date.now()),
      });
    };

    ws.onclose = () => {
      if (attempt >= MAX_ATTEMPTS) {
        setState({ status: "closed" });
        return;
      }
      setState({ status: "reconnecting" });
      retryTimer = setTimeout(connect, backoffDelay(attempt));
      attempt++;
    };
  }

  function disconnect() {
    clearTimeout(retryTimer);
    if (socket) {
      // Detach handlers first, so closing on purpose doesn't trigger a reconnect
      socket.onopen = socket.onmessage = socket.onclose = null;
      socket.close();
      socket = null;
    }
    attempt = 0;
    state = initialState; // no listeners left, so nobody to notify
  }

  return {
    getState: () => state,
    // First subscriber opens the socket; the last one to leave closes it
    subscribe(listener: () => void) {
      listeners.add(listener);
      if (listeners.size === 1) connect();
      return () => {
        listeners.delete(listener);
        if (listeners.size === 0) disconnect();
      };
    },
  };
}

export type PriceStore = ReturnType<typeof createPriceStore>;

// One store, and so one WebSocket, for the whole app
export const priceStore = createPriceStore();

// Each hook re-renders its component only when its own slice changes
export function usePrices(): PriceResponse[] {
  return useSyncExternalStore(
    priceStore.subscribe,
    () => priceStore.getState().prices,
  );
}

export function usePriceHistory(): PriceHistory {
  return useSyncExternalStore(
    priceStore.subscribe,
    () => priceStore.getState().history,
  );
}

export function useLiveStatus(): LiveStatus {
  return useSyncExternalStore(
    priceStore.subscribe,
    () => priceStore.getState().status,
  );
}
