import { Alert, CircularProgress } from "@mui/material";
import type {
  ColDef,
  GetRowIdParams,
  ValueFormatterParams,
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import { useLiveStatus, usePrices, type Quote } from "./priceStore";

const twoDecimals = (p: ValueFormatterParams<Quote, number>) =>
  p.value == null ? "" : p.value.toFixed(2);

const priceColumn = {
  type: "rightAligned",
  valueFormatter: twoDecimals,
  enableCellChangeFlash: true,
} satisfies ColDef<Quote>;

// Defined outside the component, so the grid gets the same array on every render
const columnDefs: ColDef<Quote>[] = [
  { field: "symbol", headerName: "Symbol" },
  // Sellers receive the bid, buyers pay the ask
  { ...priceColumn, field: "bid", headerName: "Bid (USD)" },
  { ...priceColumn, field: "ask", headerName: "Ask (USD)" },
  { ...priceColumn, field: "mid", headerName: "Mid (USD)" },
];

function getRowId(params: GetRowIdParams<Quote>): string {
  return params.data.symbol;
}

export default function PriceGrid() {
  const prices = usePrices();
  const status = useLiveStatus();

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
      <AgGridReact<Quote>
        rowData={prices}
        columnDefs={columnDefs}
        getRowId={getRowId}
        domLayout="autoHeight"
      />
    </>
  );
}
