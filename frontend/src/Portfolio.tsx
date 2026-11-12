import { Alert, Stack, Typography } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import AllocationChart from "./AllocationChart";
import { getPortfolio, type PortfolioResponse } from "./api";
import { formatMoney } from "./format";
import PositionsGrid from "./PositionsGrid";
import { usePrices } from "./priceStore";

type Props = { refreshKey: number };

export default function Portfolio({ refreshKey }: Props) {
  const prices = usePrices();
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Refetch whenever refreshKey changes (App bumps it after each order)
  useEffect(() => {
    let ignore = false;
    getPortfolio()
      .then((data) => {
        if (!ignore) {
          setPortfolio(data);
        }
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(
            err instanceof Error ? err.message : "Could not load portfolio",
          );
        }
      });
    return () => {
      ignore = true;
    };
  }, [refreshKey]);

  // Positions marked to the live mid price; recomputed on each tick or
  // portfolio change. (Valuing at the bid would show what selling would raise.)
  const holdings = useMemo(() => {
    if (portfolio === null) return [];
    const priceBySymbol = new Map(prices.map((p) => [p.symbol, p.mid]));
    return portfolio.positions.map((position) => {
      const price = priceBySymbol.get(position.symbol) ?? 0;
      return { ...position, price, marketValue: position.quantity * price };
    });
  }, [portfolio, prices]);

  if (error) return <Alert severity="error">{error}</Alert>;
  if (portfolio === null) return <Typography>Loading portfolio…</Typography>;

  const invested = holdings.reduce((sum, h) => sum + h.marketValue, 0);
  const totalValue = portfolio.cash + invested;

  return (
    <Stack spacing={2}>
      <Typography>
        {`Cash ${formatMoney(portfolio.cash)} . Invested ${formatMoney(invested)} . Total ${formatMoney(totalValue)}`}
      </Typography>
      <PositionsGrid holdings={holdings} invested={invested} />
      <AllocationChart holdings={holdings} />
    </Stack>
  );
}
