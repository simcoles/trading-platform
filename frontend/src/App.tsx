import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";
type PriceResponse = {
  symbol: string;
  price: number;
  currency: "USD" | "GBP";
};

function App() {
  const [prices, setPrices] = useState<PriceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false; // StrictMode runs effects twice in dev; ignore the stale run

    async function loadPrices() {
      try {
        const response = await fetch(`${API_URL}/prices`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: PriceResponse[] = await response.json();
        if (!ignore) {
          setPrices(data);
        }
      } catch (err) {
        if (!ignore) {
          setError(
            `Failed to load prices: ${err instanceof Error ? err.message : String(err)}`,
          );
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadPrices();
    return () => {
      ignore = true;
    };
  }, []);
  if (loading) {
    return (
      <main>
        <h1>Prices</h1>
        <p>Loading…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main>
        <h1>Prices</h1>
        <p>{error}</p>
      </main>
    );
  }

  return (
    <main>
      <h1>Prices</h1>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>Currency</th>
          </tr>
        </thead>
        <tbody>
          {prices.map((price) => (
            <tr key={price.symbol}>
              <td>{price.symbol}</td>
              <td>{price.price.toFixed(2)}</td>
              <td>{price.currency}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

export default App;
