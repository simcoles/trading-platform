import { Alert, CircularProgress } from "@mui/material";
import type {
  ColDef,
  GetRowIdParams,
  ValueFormatterParams,
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import { useEffect, useState } from "react";
import { getPrices, type PriceResponse } from "./api";

// Defined outside the component, so the grid gets the same array on every render
const columnDefs: ColDef<PriceResponse>[] = [
  { field: "symbol", headerName: "Symbol" },
  {
    field: "price",
    headerName: "Price",
    valueFormatter: (p: ValueFormatterParams<PriceResponse, number>) => {
      if (p.value === null || p.value === undefined) {
        return "";
      }
      return p.value.toFixed(2);
    },
    type: "rightAligned",
    enableCellChangeFlash: true,
  },
  {
    field: "currency",
    headerName: "Currency",
  },
];

function getRowId(params: GetRowIdParams<PriceResponse>): string {
  return params.data.symbol;
}

export default function PriceGrid() {
  const [prices, setPrices] = useState<PriceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    async function loadPrices() {
      try {
        const data = await getPrices();
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
    return <CircularProgress />;
  }
  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <AgGridReact<PriceResponse>
      rowData={prices}
      columnDefs={columnDefs}
      getRowId={getRowId}
      domLayout="autoHeight"
    />
  );
}
