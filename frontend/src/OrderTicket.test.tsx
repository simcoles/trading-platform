import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, placeOrder, type OrderResponse } from "./api";
import OrderTicket from "./OrderTicket";

// Replace only placeOrder; keep the real ApiError class and types
vi.mock("./api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./api")>()),
  placeOrder: vi.fn(),
}));

const order: OrderResponse = {
  id: 1,
  symbol: "GOOGL",
  side: "sell",
  quantity: 5,
  price: 2800,
  total: 14000,
  created_at: "2026-11-10T12:00:00Z",
};

describe("OrderTicket", () => {
  beforeEach(() => {
    vi.mocked(placeOrder).mockReset();
  });

  it("disables Place order until the quantity is a positive whole number", async () => {
    const user = userEvent.setup();
    render(<OrderTicket onPlaced={vi.fn()} />);
    const button = screen.getByRole("button", { name: "Place order" });
    const quantity = screen.getByLabelText("Quantity");

    expect(button).toBeDisabled();
    await user.type(quantity, "1.5");
    expect(button).toBeDisabled();
    await user.clear(quantity);
    await user.type(quantity, "5");
    expect(button).toBeEnabled();
  });

  it("places the order and reports it", async () => {
    const user = userEvent.setup();
    vi.mocked(placeOrder).mockResolvedValue(order);
    const onPlaced = vi.fn();
    render(<OrderTicket onPlaced={onPlaced} />);
    await user.click(screen.getByRole("combobox", { name: "Symbol" }));
    await user.click(screen.getByRole("option", { name: "GOOGL" }));
    await user.click(screen.getByRole("button", { name: "Sell" }));
    const quantity = screen.getByLabelText("Quantity");
    await user.type(quantity, "5");
    const placeOrderButton = screen.getByRole("button", {
      name: "Place order",
    });
    expect(placeOrderButton).toBeEnabled();
    await user.click(placeOrderButton);
    expect(placeOrder).toHaveBeenCalledWith({
      symbol: "GOOGL",
      side: "sell",
      quantity: 5,
    });
    expect(onPlaced).toHaveBeenCalledWith(order);
    expect(
      await screen.findByText("Sold 5 GOOGL at $2,800.00"),
    ).toBeInTheDocument();
  });

  it("shows the server's error message", async () => {
    const user = userEvent.setup();
    vi.mocked(placeOrder).mockRejectedValue(
      new ApiError(409, "Insufficient cash"),
    );
    const onPlaced = vi.fn();
    render(<OrderTicket onPlaced={onPlaced} />);
    const quantity = screen.getByLabelText("Quantity");
    await user.type(quantity, "5");
    await user.click(screen.getByRole("button", { name: "Place order" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Insufficient cash",
    );
    expect(onPlaced).not.toHaveBeenCalled();
  });
});
