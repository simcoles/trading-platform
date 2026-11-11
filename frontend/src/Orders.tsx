import { useEffect, useState } from "react";
import { getOrders, type OrderResponse } from "./api";
import OrdersBlotter from "./OrdersBlotter";
import { Alert, Stack } from "@mui/material";
import OrderTicket from "./OrderTicket";

type Props = { onPlaced: () => void; canTrade: boolean };

export default function Orders({ onPlaced, canTrade }: Props) {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    getOrders()
      .then((data) => {
        if (!ignore) setOrders(data);
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(
            err instanceof Error ? err.message : "Could not load orders",
          );
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  function handlePlaced(order: OrderResponse) {
    setOrders((current) => [order, ...current]);
    onPlaced();
  }

  return (
    <Stack spacing={2}>
      {canTrade ? (
        <OrderTicket onPlaced={handlePlaced} />
      ) : (
        <Alert severity="info">
          View only: your account cannot place orders
        </Alert>
      )}
      {error && <Alert severity="error">{error}</Alert>}
      <OrdersBlotter orders={orders} />
    </Stack>
  );
}
