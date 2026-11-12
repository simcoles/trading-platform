import { Chart, type ChartOptions } from "@highcharts/react";
import { Accessibility } from "@highcharts/react/modules/Accessibility";
import { useMemo } from "react";
import { percentChange, type PriceHistory } from "./priceHistory";

type Props = { history: PriceHistory };

export default function LivePriceChart({ history }: Props) {
  // Rebuilt once per tick. Fine for a few symbols x 120 points; at higher
  // rates you'd keep a chart ref and call series.addPoint(point, true, shift)
  const options = useMemo<ChartOptions>(
    () => ({
      chart: { type: "line", height: 300 },
      title: { text: "Price change since session start" },
      xAxis: { type: "datetime" },
      yAxis: {
        title: { text: "Change (%)" },
        labels: { format: "{value}%" },
        plotLines: [{ value: 0, width: 1, color: "#999999" }],
      },
      // Live data updates every second, so skip the intro animation
      plotOptions: {
        series: { animation: false, marker: { enabled: false } },
      },
      tooltip: { shared: true, valueDecimals: 2, valueSuffix: "%" },
      series: Object.entries(history.points).map(([symbol, points]) => ({
        type: "line",
        name: symbol,
        data: points.map(([time, price]) => [
          time,
          percentChange(price, history.start[symbol]),
        ]),
      })),
    }),
    [history],
  );

  return (
    <Chart options={options}>
      <Accessibility />
    </Chart>
  );
}
