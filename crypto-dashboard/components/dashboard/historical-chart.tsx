"use client";

import { useState } from "react";
import { useHistoricalPrices, useCryptos } from "@/hooks/use-crypto-data";
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
  formatCurrency,
  formatDateForPeriod,
  formatDateTimeForPeriod,
  CRYPTO_NAMES,
  CRYPTO_COLORS,
} from "@/lib/utils";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { useAppState } from "@/lib/store";

export function HistoricalChart() {
  const [selectedCrypto, setSelectedCrypto] = useState("bitcoin");
  const { data, isLoading, error, refetch } =
    useHistoricalPrices(selectedCrypto);
  // Liste dynamique des cryptos disponibles en base (endpoint /api/data/cryptos).
  const { data: cryptos } = useCryptos();
  const availableCryptos = (cryptos ?? []).map((c) => c.coin_id);
  const { period } = useAppState();
  const color = CRYPTO_COLORS[selectedCrypto] || "#888";

  if (isLoading) return <ChartSkeleton />;
  if (error)
    return <ErrorState message={error.message} onRetry={() => refetch()} />;

  // Backend now returns aggregated data sorted correctly
  const chartData =
    data?.prices.map((p) => ({
      date: new Date(p.timestamp).getTime(),
      price: p.price,
    })) || [];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div>
          <CardTitle>Historical Prices</CardTitle>
          <CardDescription>
            {CRYPTO_NAMES[selectedCrypto]} price over the last {period} days
          </CardDescription>
        </div>
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
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="currentColor"
                opacity={0.1}
              />
              <XAxis
                dataKey="date"
                tickFormatter={(v) => formatDateForPeriod(v, period)}
                stroke="currentColor"
                opacity={0.5}
                fontSize={12}
              />
              <YAxis
                tickFormatter={(v) => formatCurrency(v, 0)}
                stroke="currentColor"
                opacity={0.5}
                fontSize={12}
                width={80}
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
                      <p className="text-lg font-bold">
                        {formatCurrency(data.price)}
                      </p>
                    </div>
                  );
                }}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke={color}
                strokeWidth={2}
                fill="url(#priceGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
