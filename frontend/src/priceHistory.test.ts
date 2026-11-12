import { describe, expect, it } from "vitest";
import { appendTick, emptyHistory, percentChange } from "./priceHistory";

describe("appendTick", () => {
  it("records the first price as the baseline and appends points", () => {
    const first = appendTick(emptyHistory, { AAPL: 150 }, 1000);
    const second = appendTick(first, { AAPL: 151.5 }, 2000);

    expect(second.start).toEqual({ AAPL: 150 });
    expect(second.points.AAPL).toEqual([
      [1000, 150],
      [2000, 151.5],
    ]);
  });

  it("keeps only the most recent points, but not a moving baseline", () => {
    let history = emptyHistory;
    for (let i = 1; i <= 5; i++) {
      history = appendTick(history, { AAPL: 100 + i }, i * 1000, 3);
    }

    expect(history.points.AAPL).toEqual([
      [3000, 103],
      [4000, 104],
      [5000, 105],
    ]);
    expect(history.start.AAPL).toBe(101);
  });

  it("does not mutate the history it was given", () => {
    const first = appendTick(emptyHistory, { AAPL: 150 }, 1000);
    appendTick(first, { AAPL: 151 }, 2000);

    expect(first.points.AAPL).toEqual([[1000, 150]]);
    expect(emptyHistory).toEqual({ start: {}, points: {} });
  });
});

describe("percentChange", () => {
  it("is relative to the start price", () => {
    expect(percentChange(151.5, 150)).toBeCloseTo(1);
    expect(percentChange(147, 150)).toBeCloseTo(-2);
    expect(percentChange(150, 150)).toBe(0);
  });
});
