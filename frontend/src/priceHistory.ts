// A rolling window of recent prices per symbol, for the live price chart

export type PricePoint = [time: number, price: number];

export type PriceHistory = {
  // First price seen this session, the baseline for % change
  start: Record<string, number>;
  points: Record<string, PricePoint[]>;
};

// One tick a second, so 120 points is the last 2 minutes
export const MAX_POINTS = 120;

export const emptyHistory: PriceHistory = { start: {}, points: {} };

// Returns a new history with this tick appended; never mutates the input
export function appendTick(
  history: PriceHistory,
  tick: Record<string, number>,
  time: number,
  maxPoints = MAX_POINTS,
): PriceHistory {
  const start = { ...history.start };
  const points: Record<string, PricePoint[]> = {};

  for (const [symbol, price] of Object.entries(tick)) {
    start[symbol] ??= price;
    const previous = history.points[symbol] ?? [];
    points[symbol] = [...previous, [time, price] as PricePoint].slice(
      -maxPoints,
    );
  }

  return { start, points };
}

// % change from the session's first price, e.g. 151.5 against 150 → 1
export function percentChange(price: number, start: number): number {
  return (price / start - 1) * 100;
}
