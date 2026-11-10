import { describe, expect, it } from "vitest";
import { formatDateTime, formatMoney } from "./format";

describe("formatMoney", () => {
  it("formats USD with separators and two decimals", () => {
    expect(formatMoney(1500)).toEqual("$1,500.00");
    expect(formatMoney(118.5)).toEqual("$118.50");
  });

  it("formats negatives", () => {
    expect(formatMoney(-900)).toBe("-$900.00");
  });
});

describe("formatDateTime", () => {
  it("formats an ISO timestamp", () => {
    expect(formatDateTime("2026-07-10T14:01:55Z")).toBe("10/07/2026, 14:01:55");
  });
});
