"use client";

import { useState } from "react";
import { useDrawdown } from "@/hooks/use-crypto-data";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChartSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import {
  formatPercent,
  formatCurrency,
  formatDate,
  formatDateForPeriod,
  formatDateTimeForPeriod,
  CRYPTO_NAMES,
} from "@/lib/utils";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
} from "recharts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TrendingDown, AlertTriangle, Clock, Target } from "lucide-react";
import { useAppState } from "@/lib/store";

function getSeverityEmoji(drawdown: number): string {
  const pct = Math.abs(drawdown);
  if (pct < 10) return "😊";
  if (pct < 25) return "😐";
  if (pct < 50) return "😟";
  return "😱";
}

export function DrawdownChart() {
  const [selectedCrypto, setSelectedCrypto] = useState("bitcoin");
  const { data, isLoading, error, refetch } = useDrawdown();
  const { period } = useAppState();

  if (isLoading) return <ChartSkeleton />;
  if (error)
    return <ErrorState message={error.message} onRetry={() => refetch()} />;

  // Liste dynamique : uniquement les cryptos qui ont réellement une métrique
  // de drawdown renvoyée par l'API (plus de liste codée en dur).
  const availableCryptos = data?.metrics.map((m) => m.crypto) ?? [];
  const selectedMetric = data?.metrics.find((m) => m.crypto === selectedCrypto);
  const chartData =
    selectedMetric?.drawdown_periods.map((p) => ({
      date: new Date(p.start).getTime(),
      drawdown: p.drawdown * 100,
    })) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Select value={selectedCrypto} onValueChange={setSelectedCrypto}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {availableCryptos.map((crypto) => (
              <SelectItem key={crypto} value={crypto}>
                {CRYPTO_NAMES[crypto] || crypto}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedMetric && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <TrendingDown className="w-4 h-4" />
                <span className="text-sm">Max Drawdown</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-destructive">
                  {formatPercent(selectedMetric.max_drawdown)}
                </span>
                <span className="text-2xl">
                  {getSeverityEmoji(selectedMetric.max_drawdown)}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm">Current Drawdown</span>
              </div>
              <span className="text-2xl font-bold">
                {formatPercent(selectedMetric.current_drawdown)}
              </span>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Time Underwater</span>
              </div>
              <span className="text-2xl font-bold">
                {formatPercent(selectedMetric.time_underwater_pct)}
              </span>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Target className="w-4 h-4" />
                <span className="text-sm">Peak Price</span>
              </div>
              <span className="text-2xl font-bold">
                {formatCurrency(selectedMetric.peak_price)}
              </span>
              <p className="text-xs text-muted-foreground mt-1">
                {formatDate(selectedMetric.peak_date)}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Drawdown Over Time</CardTitle>
          <CardDescription>
            {CRYPTO_NAMES[selectedCrypto]} drawdown periods (red = decline from
            peak)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient
                    id="drawdownGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.1} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0.4} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tickFormatter={(v) => formatDateForPeriod(v, period)}
                  stroke="currentColor"
                  opacity={0.5}
                  fontSize={12}
                />
                <YAxis
                  tickFormatter={(v) => `${v.toFixed(0)}%`}
                  stroke="currentColor"
                  opacity={0.5}
                  fontSize={12}
                  domain={["dataMin", 0]}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const data = payload[0].payload;
                    return (
                      <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
                        <p className="text-sm text-muted-foreground">
                          {formatDateTimeForPeriod(data.date, period)}
                        </p>
                        <p className="text-lg font-bold text-destructive">
                          {formatPercent(data.drawdown)}
                        </p>
                      </div>
                    );
                  }}
                />
                <ReferenceLine
                  y={0}
                  stroke="currentColor"
                  strokeOpacity={0.3}
                />
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fill="url(#drawdownGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Drawdown Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Crypto</TableHead>
                <TableHead className="text-right">Max Drawdown</TableHead>
                <TableHead className="text-right">Current</TableHead>
                <TableHead className="text-right">Time Underwater</TableHead>
                <TableHead className="text-right">Peak / Trough</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.metrics.map((m) => (
                <TableRow key={m.crypto}>
                  <TableCell className="font-medium">
                    {CRYPTO_NAMES[m.crypto] || m.crypto}
                  </TableCell>
                  <TableCell className="text-right">
                    <span className="font-mono text-destructive">
                      {formatPercent(m.max_drawdown)}
                    </span>
                    <span className="ml-1">
                      {getSeverityEmoji(m.max_drawdown)}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    {formatPercent(m.current_drawdown)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatPercent(m.time_underwater_pct)}
                  </TableCell>
                  <TableCell className="text-right text-sm">
                    {formatCurrency(m.peak_price)} /{" "}
                    {formatCurrency(m.trough_price)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
