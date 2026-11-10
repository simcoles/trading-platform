import { useEffect, useState } from "react";
import { getOrders, type OrderResponse } from "./api";
import OrdersBlotter from "./OrdersBlotter";

export default function Orders() {
  const [orders, setOrders] = useState<OrderResponse[]>([]);

  useEffect(() => {
    let ignore = false;
    getOrders().then((data) => {
      if (!ignore) setOrders(data);
    });
    return () => {
      ignore = true;
    };
  }, []);

  return <OrdersBlotter orders={orders} />;
}
