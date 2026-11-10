import { Chart, type ChartOptions } from "@highcharts/react";
import { Accessibility } from "@highcharts/react/modules/Accessibility";
import { useMemo } from "react";

export type Holding = { symbol: string; marketValue: number };

type Props = { holdings: Holding[] };

export default function AllocationChart({ holdings }: Props) {
  // Rebuild the options only when the data changes, not on every render
  const options = useMemo<ChartOptions>(
    () => ({
      chart: { type: "bar", height: 260 },
      title: { text: "Allocation by market value" },
      xAxis: { categories: holdings.map((h) => h.symbol) },
      yAxis: { title: { text: "Market value (USD)" } },
      legend: { enabled: false },
      // Live data updates every second, so skip the "grow from zero" intro animation
      plotOptions: { series: { animation: false } },
      tooltip: { valuePrefix: "$", valueDecimals: 2 },
      series: [
        {
          type: "bar",
          name: "Market value",
          data: holdings.map((h) => h.marketValue),
        },
      ],
    }),
    [holdings],
  );

  return (
    <Chart options={options}>
      <Accessibility />
    </Chart>
  );
}
