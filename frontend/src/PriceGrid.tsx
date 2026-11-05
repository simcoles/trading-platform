import { Alert, CircularProgress } from "@mui/material";
import type {
  ColDef,
  GetRowIdParams,
  ValueFormatterParams,
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import type { PriceResponse } from "./api";
import { useLivePrices } from "./useLivePrices";

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
  const { prices, status } = useLivePrices();

  if (status === "connecting") {
    return <Alert severity="info">Connecting to live prices...</Alert>;
  }

  if (prices.length === 0) {
    return status === "closed" ? (
      <Alert severity="error">Could not connect to live prices</Alert>
    ) : (
      <CircularProgress />
    );
  }

  return (
    <>
      {status === "reconnecting" && (
        <Alert severity="warning">Reconnecting to live prices…</Alert>
      )}
      {status === "closed" && (
        <Alert severity="error">Connection to live prices closed</Alert>
      )}
      <AgGridReact<PriceResponse>
        rowData={prices}
        columnDefs={columnDefs}
        getRowId={getRowId}
        domLayout="autoHeight"
      />
    </>
  );
}
