import type {
  ColDef,
  GetRowIdParams,
  ValueFormatterParams,
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import { useMemo } from "react";
import { formatMoney } from "./format";

export type PositionRow = {
  symbol: string;
  quantity: number;
  price: number;
  marketValue: number;
};

type Row = PositionRow & { weight: number };
type Props = { holdings: PositionRow[]; invested: number };

const money = (p: ValueFormatterParams<Row, number>) =>
  p.value == null ? "" : formatMoney(p.value);

const percent = new Intl.NumberFormat("en-GB", {
  style: "percent",
  minimumFractionDigits: 1,
});

const columnDefs: ColDef<Row>[] = [
  {
    field: "symbol",
    headerName: "Symbol",
  },
  {
    field: "quantity",
    headerName: "Quantity",
    type: "rightAligned",
  },
  {
    field: "price",
    headerName: "Mid price",
    type: "rightAligned",
    valueFormatter: money,
    enableCellChangeFlash: true,
  },
  {
    field: "marketValue",
    headerName: "Market value",
    type: "rightAligned",
    valueFormatter: money,
  },
  {
    field: "weight",
    headerName: "Weight",
    type: "rightAligned",
    valueFormatter: (p: ValueFormatterParams<Row, number>) =>
      p.value == null ? "" : percent.format(p.value),
  },
];

function getRowId(params: GetRowIdParams<Row>): string {
  return params.data.symbol;
}

export default function PositionsGrid({ holdings, invested }: Props) {
  const rows = useMemo<Row[]>(
    () =>
      holdings.map((h) => ({
        ...h,
        weight: invested === 0 ? 0 : h.marketValue / invested,
      })),
    [holdings, invested],
  );

  return (
    <AgGridReact<Row>
      rowData={rows}
      columnDefs={columnDefs}
      getRowId={getRowId}
      domLayout="autoHeight"
    />
  );
}
