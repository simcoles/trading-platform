// Created once at module level: building Intl formatters is relatively
// expensive, and a grid may format thousands of cells

const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function formatMoney(value: number): string {
  return usd.format(value);
}

const dateTime = new Intl.DateTimeFormat("en-GB", {
  dateStyle: "short",
  timeStyle: "medium",
});

export function formatDateTime(iso: string): string {
  const date = new Date(iso);
  return dateTime.format(date);
}
