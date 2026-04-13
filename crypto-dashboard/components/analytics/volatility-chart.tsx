<<<<<<< HEAD
"use client"

import { useVolatility } from "@/hooks/use-crypto-data"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ChartSkeleton } from "@/components/shared/loading-skeleton"
import { ErrorState } from "@/components/shared/error-state"
import { formatNumber, formatCurrency, CRYPTO_NAMES } from "@/lib/utils"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell } from "recharts"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

function getVolatilityColor(value: number, max: number): string {
  const ratio = value / max
  if (ratio < 0.33) return "#22c55e"
  if (ratio < 0.66) return "#eab308"
  return "#ef4444"
}

export function VolatilityChart() {
  const { data, isLoading, error, refetch } = useVolatility()

  if (isLoading) return <ChartSkeleton />
  if (error) return <ErrorState message={error.message} onRetry={() => refetch()} />

  const maxStdDev = Math.max(...(data?.metrics.map((m) => m.std_deviation) || [1]))
  const chartData =
    data?.metrics.map((m) => ({
      name: CRYPTO_NAMES[m.crypto] || m.crypto,
      crypto: m.crypto,
      value: m.std_deviation,
      color: getVolatilityColor(m.std_deviation, maxStdDev),
    })) || []
=======
"use client";

import { useVolatility } from "@/hooks/use-crypto-data";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ChartSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { formatNumber, formatCurrency, CRYPTO_NAMES } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TrendingUp, TrendingDown } from "lucide-react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell,
} from "recharts";

function getVolatilityLevel(volatility: number): {
  label: string;
  color: string;
} {
  if (volatility < 30) return { label: "Low", color: "text-green-600" };
  if (volatility < 60) return { label: "Moderate", color: "text-yellow-600" };
  if (volatility < 90) return { label: "High", color: "text-orange-600" };
  return { label: "Very High", color: "text-red-600" };
}

export function VolatilityChart() {
  const { data, isLoading, error, refetch } = useVolatility();

  if (isLoading) return <ChartSkeleton />;
  if (error)
    return <ErrorState message={error.message} onRetry={() => refetch()} />;

  const chartData =
    data?.metrics.map((m: any) => ({
      name: CRYPTO_NAMES[m.crypto] || m.crypto,
      volatility: m.annualized_volatility,
    })) || [];

  const getBarColor = (volatility: number) => {
    if (volatility < 30) return "#22c55e"; // green
    if (volatility < 60) return "#eab308"; // yellow
    if (volatility < 90) return "#f97316"; // orange
    return "#ef4444"; // red
  };
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Volatility Comparison</CardTitle>
<<<<<<< HEAD
          <CardDescription>Standard deviation of returns over the selected period</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical">
                <XAxis type="number" tickFormatter={(v) => formatNumber(v, 4)} fontSize={12} />
                <YAxis type="category" dataKey="name" width={100} fontSize={12} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null
                    const data = payload[0].payload
                    return (
                      <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
                        <p className="font-medium">{data.name}</p>
                        <p className="text-sm text-muted-foreground">Std Dev: {formatNumber(data.value, 6)}</p>
                      </div>
                    )
                  }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
=======
          <CardDescription>
            Standard deviation of returns over the selected period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis
                dataKey="name"
                tick={{ fill: "#94a3b8" }}
                stroke="#475569"
              />
              <YAxis
                tick={{ fill: "#94a3b8" }}
                stroke="#475569"
                label={{
                  value: "Annualized Volatility (%)",
                  angle: -90,
                  position: "insideLeft",
                  fill: "#94a3b8",
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
                formatter={(value: number) => [
                  `${formatNumber(value, 1)}%`,
                  "Volatility",
                ]}
              />
              <Bar dataKey="volatility" radius={[8, 8, 0, 0]}>
                {chartData.map((entry: any, index: number) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getBarColor(entry.volatility)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
<<<<<<< HEAD
          <CardTitle>Volatility Metrics</CardTitle>
=======
          <CardTitle>Volatility Analysis</CardTitle>
          <CardDescription>
            Annualized volatility measures how much an asset's price fluctuates.
            Higher volatility = higher risk.
          </CardDescription>
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
<<<<<<< HEAD
                <TableHead>Crypto</TableHead>
                <TableHead className="text-right">Std Deviation</TableHead>
                <TableHead className="text-right">Coef. of Variation</TableHead>
                <TableHead className="text-right">VaR 95%</TableHead>
                <TableHead className="text-right">Price Range</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.metrics.map((m) => (
                <TableRow key={m.crypto}>
                  <TableCell className="font-medium">{CRYPTO_NAMES[m.crypto] || m.crypto}</TableCell>
                  <TableCell className="text-right font-mono">{formatNumber(m.std_deviation, 6)}</TableCell>
                  <TableCell className="text-right font-mono">{formatNumber(m.coefficient_of_variation, 4)}</TableCell>
                  <TableCell className="text-right font-mono">{formatCurrency(m.var_95)}</TableCell>
                  <TableCell className="text-right text-sm">
                    {formatCurrency(m.price_range.min)} - {formatCurrency(m.price_range.max)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
=======
                <TableHead>Cryptocurrency</TableHead>
                <TableHead className="text-right">Average Price</TableHead>
                <TableHead className="text-right">Period Volatility</TableHead>
                <TableHead className="text-right">
                  Annualized Volatility
                </TableHead>
                <TableHead className="text-right">Risk Level</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.metrics.map((m: any) => {
                const level = getVolatilityLevel(m.annualized_volatility);
                return (
                  <TableRow key={m.crypto}>
                    <TableCell className="font-medium">
                      {CRYPTO_NAMES[m.crypto] || m.crypto}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatCurrency(m.mean_price)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      <div className="flex items-center justify-end gap-2">
                        {formatNumber(m.period_volatility || 0, 1)}%
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        (actual)
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      <div className="flex items-center justify-end gap-2">
                        {m.annualized_volatility > 50 ? (
                          <TrendingUp className="w-4 h-4 text-destructive" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-success" />
                        )}
                        {formatNumber(m.annualized_volatility, 1)}%
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        (projected)
                      </div>
                    </TableCell>
                    <TableCell
                      className={`text-right font-medium ${level.color}`}
                    >
                      {level.label}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="text-sm font-semibold mb-2">
              Understanding Volatility
            </h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>
                • <strong>Period Volatility</strong>: Actual price fluctuation
                over the selected period
              </li>
              <li>
                • <strong>Annualized Volatility</strong>: Projection if this
                trend continues for a year
              </li>
              <li>
                • ⚠️ <strong>Important</strong>: Annualized volatility assumes
                the trend repeats, which may not happen in crypto markets
              </li>
              <li className="mt-3 pt-2 border-t border-border">
                • <strong>Low (&lt;30%)</strong>: Stable, similar to traditional
                stocks
              </li>
              <li>
                • <strong>Moderate (30-60%)</strong>: Typical for established
                cryptocurrencies
              </li>
              <li>
                • <strong>High (60-90%)</strong>: Significant price swings
                expected
              </li>
              <li>
                • <strong>Very High (&gt;90%)</strong>: Extreme volatility, high
                risk
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}
