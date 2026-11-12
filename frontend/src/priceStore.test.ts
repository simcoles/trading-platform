import { afterEach, describe, expect, it, vi } from "vitest";
import { createPriceStore } from "./priceStore";

// Just enough of a WebSocket for the store: handlers it sets, and close()
class FakeSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  close = vi.fn();

  open() {
    this.onopen?.();
  }
  // Takes mids and sends quotes 1.00 either side, in the server's format
  send(mids: Record<string, number>) {
    const tick = Object.fromEntries(
      Object.entries(mids).map(([symbol, mid]) => [
        symbol,
        { bid: mid - 1, mid, ask: mid + 1 },
      ]),
    );
    this.onmessage?.({ data: JSON.stringify(tick) });
  }
  drop() {
    this.onclose?.();
  }
}

function setup() {
  const sockets: FakeSocket[] = [];
  const store = createPriceStore(() => {
    const socket = new FakeSocket();
    sockets.push(socket);
    return socket as unknown as WebSocket;
  });
  return { store, sockets };
}

afterEach(() => {
  vi.useRealTimers();
});

describe("priceStore", () => {
  it("opens one socket for the first subscriber only", () => {
    const { store, sockets } = setup();
    expect(sockets).toHaveLength(0);

    store.subscribe(() => {});
    store.subscribe(() => {});

    expect(sockets).toHaveLength(1);
  });

  it("turns a tick into quote rows, and the mids into history", () => {
    const { store, sockets } = setup();
    store.subscribe(() => {});

    sockets[0].send({ AAPL: 150, MSFT: 420 });

    expect(store.getState().prices).toEqual([
      { symbol: "AAPL", bid: 149, mid: 150, ask: 151 },
      { symbol: "MSFT", bid: 419, mid: 420, ask: 421 },
    ]);
    expect(store.getState().history.start).toEqual({ AAPL: 150, MSFT: 420 });
  });

  it("keeps untouched slices identical, so their subscribers skip re-rendering", () => {
    const { store, sockets } = setup();
    store.subscribe(() => {});
    sockets[0].open();
    sockets[0].send({ AAPL: 150 });

    const before = store.getState();
    sockets[0].send({ AAPL: 151 });
    const afterTick = store.getState();

    expect(afterTick.prices).not.toBe(before.prices);
    expect(afterTick.status).toBe(before.status);

    sockets[0].drop(); // status changes to "reconnecting"
    expect(store.getState().status).toBe("reconnecting");
    expect(store.getState().prices).toBe(afterTick.prices); // same array
  });

  it("notifies every subscriber on each change", () => {
    const { store, sockets } = setup();
    const listener = vi.fn();
    store.subscribe(listener);

    sockets[0].open();
    sockets[0].send({ AAPL: 150 });

    expect(listener).toHaveBeenCalledTimes(2);
  });

  it("reconnects with a new socket after an unexpected close", () => {
    vi.useFakeTimers();
    const { store, sockets } = setup();
    store.subscribe(() => {});

    sockets[0].drop();
    vi.runOnlyPendingTimers();

    expect(sockets).toHaveLength(2);
  });

  it("closes the socket when the last subscriber leaves, without reconnecting", () => {
    vi.useFakeTimers();
    const { store, sockets } = setup();
    const first = store.subscribe(() => {});
    const second = store.subscribe(() => {});

    first();
    expect(sockets[0].close).not.toHaveBeenCalled();

    second();
    expect(sockets[0].close).toHaveBeenCalledOnce();
    expect(sockets[0].onclose).toBeNull(); // detached, so no reconnect
    vi.runAllTimers();
    expect(sockets).toHaveLength(1);
    expect(store.getState().status).toBe("connecting"); // fresh for next time
  });
});
