"use client";

import { useDrawdown } from "@/hooks/use-crypto-data";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ChartSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { formatPercent, formatCurrency, CRYPTO_NAMES } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TrendingDown, TrendingUp, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

function getDrawdownSeverity(drawdown: number): {
  label: string;
  color: string;
  emoji: string;
} {
  const abs = Math.abs(drawdown);
  if (abs < 20) return { label: "Mild", color: "text-yellow-600", emoji: "😊" };
  if (abs < 40)
    return { label: "Moderate", color: "text-orange-600", emoji: "😐" };
  if (abs < 60) return { label: "Severe", color: "text-red-600", emoji: "😟" };
  return { label: "Extreme", color: "text-red-700", emoji: "😱" };
}

export function MaxDrawdownCard() {
  const { data, isLoading, error, refetch } = useDrawdown();

  if (isLoading) return <ChartSkeleton />;
  if (error)
    return <ErrorState message={error.message} onRetry={() => refetch()} />;

  const sortedMetrics = [...(data?.metrics || [])].sort(
    (a, b) => a.max_drawdown - b.max_drawdown,
  );

  // The worst drawdown is the most negative (first in sorted array)
  const worstDrawdown = sortedMetrics[0];
  // The best drawdown is the least negative (last in sorted array)
  const bestDrawdown = sortedMetrics[sortedMetrics.length - 1];

  return (
    <div className="space-y-6">
      {bestDrawdown && (
        <Card className="border-2 border-green-500/20 bg-gradient-to-br from-green-500/5 to-transparent">
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <CardTitle className="text-lg">
                Lowest Risk (Best Resilience)
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold">
                  {CRYPTO_NAMES[bestDrawdown.crypto] || bestDrawdown.crypto}
                </p>
                <p className="text-sm text-muted-foreground">
                  Best resistance to price drops
                </p>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-green-500">
                  {formatPercent(bestDrawdown.max_drawdown)}
                </p>
                <p className="text-xs text-muted-foreground">
                  From {formatCurrency(bestDrawdown.peak_price)} to{" "}
                  {formatCurrency(bestDrawdown.trough_price)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {worstDrawdown && (
        <Card className="border-2 border-destructive/20 bg-gradient-to-br from-destructive/5 to-transparent">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              <CardTitle className="text-lg">
                Highest Risk (Max Drawdown)
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold">
                  {CRYPTO_NAMES[worstDrawdown.crypto] || worstDrawdown.crypto}
                </p>
                <p className="text-sm text-muted-foreground">
                  Worst historical loss from peak
                </p>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-destructive">
                  {formatPercent(worstDrawdown.max_drawdown)}
                </p>
                <p className="text-xs text-muted-foreground">
                  From {formatCurrency(worstDrawdown.peak_price)} to{" "}
                  {formatCurrency(worstDrawdown.trough_price)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Drawdown Comparison</CardTitle>
          <CardDescription>
            Maximum loss from peak to trough for each cryptocurrency
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={sortedMetrics.map((m) => ({
                name: CRYPTO_NAMES[m.crypto] || m.crypto,
                drawdown: Math.abs(m.max_drawdown),
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
                  value: "Maximum Drawdown (%)",
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
                  `-${value.toFixed(1)}%`,
                  "Max Drawdown",
                ]}
              />
              <Bar dataKey="drawdown" radius={[8, 8, 0, 0]}>
                {sortedMetrics.map((m, index) => {
                  const abs = Math.abs(m.max_drawdown);
                  const color =
                    abs < 20
                      ? "#eab308"
                      : abs < 40
                        ? "#f97316"
                        : abs < 60
                          ? "#ef4444"
                          : "#dc2626";
                  return <Cell key={`cell-${index}`} fill={color} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Maximum Drawdown Analysis</CardTitle>
          <CardDescription>
            Maximum loss from a peak to a trough. Shows the worst-case scenario
            if you bought at the top.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cryptocurrency</TableHead>
                <TableHead className="text-right">Max Drawdown</TableHead>
                <TableHead className="text-right">Peak Price</TableHead>
                <TableHead className="text-right">Trough Price</TableHead>
                <TableHead className="text-right">Severity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedMetrics.map((m) => {
                const severity = getDrawdownSeverity(m.max_drawdown);
                return (
                  <TableRow key={m.crypto}>
                    <TableCell className="font-medium">
                      {CRYPTO_NAMES[m.crypto] || m.crypto}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <TrendingDown className="w-4 h-4 text-destructive" />
                        <span className="font-mono font-bold text-destructive text-lg">
                          {formatPercent(m.max_drawdown)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatCurrency(m.peak_price)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatCurrency(m.trough_price)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={cn("font-medium", severity.color)}>
                        {severity.emoji} {severity.label}
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="text-sm font-semibold mb-2">
              Understanding Maximum Drawdown
            </h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>
                • <strong>What it means:</strong> The biggest percentage drop
                from a peak to a trough
              </li>
              <li>
                • <strong>Why it matters:</strong> Shows the worst-case loss you
                could have experienced
              </li>
              <li>
                • <strong>&lt; -20%:</strong> Mild correction, common in crypto
              </li>
              <li>
                • <strong>-20% to -40%:</strong> Moderate bear market
              </li>
              <li>
                • <strong>-40% to -60%:</strong> Severe crash
              </li>
              <li>
                • <strong>&gt; -60%:</strong> Extreme crash (crypto winter)
              </li>
              <li>
                • <strong>Investment tip:</strong> Only invest what you can
                afford to lose by this percentage
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
