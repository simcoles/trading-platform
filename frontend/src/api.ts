export const API_URL = "http://127.0.0.1:8000";

// ---- Types: mirror backend/src/backend/models.py ----

export type Currency = "USD" | "GBP";

export type PriceResponse = {
  symbol: string;
  price: number;
  currency: Currency;
};

export type WatchlistItem = {
  symbol: string;
};

// One item of a 422 `detail` list. Only the fields we use.
type ValidationError = {
  loc: (string | number)[];
  msg: string;
};

type ErrorBody = {
  detail: string | ValidationError[];
};

// ---- Errors ----

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

function detailToMessage(detail: ErrorBody["detail"]): string {
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join("; ");
  } else {
    return detail;
  }
}

// ---- The one place that calls fetch ----

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`; // fallback
    try {
      const errorBody: ErrorBody = await response.json();
      message = detailToMessage(errorBody.detail);
    } catch {
      // body wasn't JSON (e.g. a plain-text 500): keep the fallback
    }
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

// ---- Endpoints ----

export function getPrices(): Promise<PriceResponse[]> {
  return request<PriceResponse[]>("/prices");
}

export function getWatchlist(): Promise<string[]> {
  return request<string[]>("/watchlist");
}

export function addToWatchlist(symbol: string): Promise<WatchlistItem> {
  return request<WatchlistItem>("/watchlist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ symbol }),
  });
}

export function removeFromWatchlist(symbol: string): Promise<void> {
  return request<void>(`/watchlist/${encodeURIComponent(symbol)}`, {
    method: "DELETE",
  });
}
