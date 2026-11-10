import type {
  CellStyle,
  CellStyleFunc,
  ColDef,
  GetRowIdParams,
  ValueFormatterParams,
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import type { OrderResponse, Side } from "./api";
import { formatDateTime, formatMoney } from "./format";

// Shared by the Price and Total columns. Formatting only changes what's
// displayed: sorting and filtering still use the raw number.
function money(p: ValueFormatterParams<OrderResponse, number>): string {
  return p.value == null ? "" : formatMoney(p.value);
}

// Colour plus text: BUY/SELL is readable without colour (WCAG 1.4.1)
const sideStyle: CellStyleFunc<OrderResponse, Side> = (p): CellStyle => ({
  color: p.value === "buy" ? "#1b5e20" : "#b71c1c",
  fontWeight: 600,
});

// Module level: the grid gets the same array on every render
const columnDefs: ColDef<OrderResponse>[] = [
  {
    field: "created_at",
    headerName: "Time",
    sort: "desc", // ISO strings sort correctly as text
    valueFormatter: (p: ValueFormatterParams<OrderResponse, string>) =>
      p.value ? formatDateTime(p.value) : "",
    filter: false,
  },
  { field: "symbol", headerName: "Symbol" },
  {
    field: "side",
    headerName: "Side",
    valueFormatter: (p: ValueFormatterParams<OrderResponse, Side>) =>
      p.value ? p.value.toUpperCase() : "",
    cellStyle: sideStyle,
  },
  {
    field: "quantity",
    headerName: "Qty",
    type: "rightAligned",
    filter: "agNumberColumnFilter",
  },
  {
    field: "price",
    headerName: "Price",
    type: "rightAligned",
    valueFormatter: money,
    filter: "agNumberColumnFilter",
  },
  {
    field: "total",
    headerName: "Total",
    type: "rightAligned",
    valueFormatter: money,
    filter: "agNumberColumnFilter",
  },
];

// Applied to every column unless the column overrides it
const defaultColDef: ColDef<OrderResponse> = {
  flex: 1,
  filter: true,
};

// Stable row identity: new orders are added, not the whole grid redrawn
function getRowId(params: GetRowIdParams<OrderResponse>): string {
  return String(params.data.id);
}

type Props = { orders: OrderResponse[] };

export default function OrdersBlotter({ orders }: Props) {
  return (
    <AgGridReact<OrderResponse>
      rowData={orders}
      columnDefs={columnDefs}
      defaultColDef={defaultColDef}
      getRowId={getRowId}
      domLayout="autoHeight"
      overlayNoRowsTemplate="No orders yet"
    />
  );
}
