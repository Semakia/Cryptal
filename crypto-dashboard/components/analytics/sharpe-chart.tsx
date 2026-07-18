"use client";

import { useState } from "react";
import { useSharpe } from "@/hooks/use-crypto-data";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ChartSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { formatNumber, formatPercent, CRYPTO_NAMES } from "@/lib/utils";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TrendingUp, Award } from "lucide-react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

function getSharpeRating(value: number): {
  label: string;
  color: string;
  emoji: string;
} {
  if (value > 2)
    return { label: "Excellent", color: "text-green-600", emoji: "🌟" };
  if (value > 1) return { label: "Good", color: "text-green-500", emoji: "✅" };
  if (value > 0)
    return { label: "Fair", color: "text-yellow-600", emoji: "⚠️" };
  return { label: "Poor", color: "text-red-600", emoji: "❌" };
}

export function SharpeChart() {
  const [riskFreeRate, setRiskFreeRate] = useState(0.02);
  const { data, isLoading, error, refetch } = useSharpe(riskFreeRate);

  if (isLoading) return <ChartSkeleton />;
  if (error)
    return <ErrorState message={error.message} onRetry={() => refetch()} />;

  const sortedMetrics = [...(data?.metrics || [])].sort(
    (a, b) => b.sharpe_ratio - a.sharpe_ratio,
  );

  const bestCrypto = sortedMetrics[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Label htmlFor="riskFreeRate" className="text-sm whitespace-nowrap">
            Risk-Free Rate
          </Label>
          <Input
            id="riskFreeRate"
            type="number"
            step="0.01"
            min="0"
            max="0.2"
            value={riskFreeRate}
            onChange={(e) => setRiskFreeRate(Number(e.target.value))}
            className="w-24"
          />
          <span className="text-xs text-muted-foreground">
            ({formatPercent(riskFreeRate * 100, 1)})
          </span>
        </div>
      </div>

      {bestCrypto && (
        <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />
              <CardTitle className="text-lg">
                Best Risk-Adjusted Return
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold">
                  {CRYPTO_NAMES[bestCrypto.crypto] || bestCrypto.crypto}
                </p>
                <p className="text-sm text-muted-foreground">
                  Highest Sharpe Ratio
                </p>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-primary">
                  {formatNumber(bestCrypto.sharpe_ratio, 2)}
                </p>
                <p className="text-xs text-muted-foreground">Sharpe Ratio</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Sharpe Ratio Comparison</CardTitle>
          <CardDescription>
            Risk-adjusted returns (higher is better, above 1 is good)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={sortedMetrics.map((m) => ({
                name: CRYPTO_NAMES[m.crypto] || m.crypto,
                sharpe: m.sharpe_ratio,
              }))}
            >
              <XAxis
                dataKey="name"
                tick={{ fill: "#94a3b8" }}
                stroke="#475569"
              />
              <YAxis
                tick={{ fill: "#94a3b8" }}
                stroke="#475569"
                label={{
                  value: "Sharpe Ratio",
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
                  formatNumber(value, 2),
                  "Sharpe Ratio",
                ]}
              />
              <Bar dataKey="sharpe" radius={[8, 8, 0, 0]}>
                {sortedMetrics.map((m, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      m.sharpe_ratio > 1
                        ? "#22c55e"
                        : m.sharpe_ratio > 0
                          ? "#eab308"
                          : "#ef4444"
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Risk-Adjusted Returns (Sharpe Ratio)</CardTitle>
          <CardDescription>
            Measures actual return per unit of risk over the selected period.
            Higher is better.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cryptocurrency</TableHead>
                <TableHead className="text-right">
                  Actual Return (Period)
                </TableHead>
                <TableHead className="text-right">
                  Annualized Volatility
                </TableHead>
                <TableHead className="text-right">Sharpe Ratio</TableHead>
                <TableHead className="text-right">Rating</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedMetrics.map((m, index) => {
                const rating = getSharpeRating(m.sharpe_ratio);
                return (
                  <TableRow key={m.crypto}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        {index === 0 && <span className="text-lg">🥇</span>}
                        {index === 1 && <span className="text-lg">🥈</span>}
                        {index === 2 && <span className="text-lg">🥉</span>}
                        {CRYPTO_NAMES[m.crypto] || m.crypto}
                      </div>
                    </TableCell>
                    <TableCell
                      className={cn(
                        "text-right font-mono",
                        m.total_return >= 0
                          ? "text-success"
                          : "text-destructive",
                      )}
                    >
                      <div className="flex items-center justify-end gap-1">
                        {m.total_return >= 0 ? (
                          <TrendingUp className="w-3 h-3" />
                        ) : null}
                        {formatPercent(m.total_return)}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatNumber(m.annualized_volatility, 1)}%
                    </TableCell>
                    <TableCell
                      className={cn(
                        "text-right font-mono font-bold text-lg",
                        m.sharpe_ratio > 1
                          ? "text-success"
                          : m.sharpe_ratio > 0
                            ? "text-warning"
                            : "text-destructive",
                      )}
                    >
                      {formatNumber(m.sharpe_ratio, 2)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={`font-medium ${rating.color}`}>
                        {rating.emoji} {rating.label}
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="text-sm font-semibold mb-2">
              Understanding Sharpe Ratio
            </h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>
                • <strong>What it shows:</strong> Return earned per unit of risk
                over the selected period
              </li>
              <li>
                • <strong>Formula:</strong> (Actual Return - Risk-Free Rate) /
                Volatility
              </li>
              <li>
                • <strong>&gt; 1.0:</strong> Good - Returns justify the risk
                taken
              </li>
              <li>
                • <strong>0 to 1.0:</strong> Fair - Modest return for risk
              </li>
              <li>
                • <strong>&lt; 0:</strong> Poor - Losing money (common in bear
                markets)
              </li>
              <li>
                • <strong>Note:</strong> We use actual returns, not annualized
                projections
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
