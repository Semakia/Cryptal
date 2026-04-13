"use client";

import { Card, CardContent } from "@/components/ui/card";
import { CryptoIcon } from "@/components/shared/crypto-icon";
import {
  cn,
  formatCurrency,
  formatCompactCurrency,
  formatPercent,
  CRYPTO_NAMES,
  CRYPTO_COLORS,
} from "@/lib/utils";
import type { CryptoPrice } from "@/lib/api";
import { TrendingUp, TrendingDown } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { useAppState } from "@/lib/store";

interface PriceCardProps {
  data: CryptoPrice;
}

function getPeriodLabel(period: number): string {
  if (period <= 1) return "24h";
  if (period <= 7) return "7D";
  if (period <= 30) return "30D";
  return `${period}D`;
}

export function PriceCard({ data }: PriceCardProps) {
  const { period } = useAppState();
  const isPositive = data.change_24h_pct >= 0;
  const sparklineData = data.sparkline.map((price, i) => ({
    value: price,
    index: i,
  }));
  const color = CRYPTO_COLORS[data.crypto] || "#888";
  const periodLabel = getPeriodLabel(period);

  return (
    <Card className="group hover:shadow-lg transition-all duration-200 hover:border-primary/20">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">
                {CRYPTO_NAMES[data.crypto] || data.crypto}
              </span>
            </div>
            <div className="text-2xl font-bold tracking-tight">
              {formatCurrency(data.price)}
            </div>
            <div
              className={cn(
                "flex items-center gap-1 text-sm font-medium",
                isPositive ? "text-success" : "text-destructive",
              )}
            >
              {isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {formatPercent(data.change_24h_pct)}
              <span className="text-xs text-muted-foreground ml-1">
                ({periodLabel})
              </span>
            </div>
          </div>
          <CryptoIcon crypto={data.crypto} size="lg" />
        </div>

        <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
          <span>Market Cap</span>
          <span className="font-medium">
            {formatCompactCurrency(data.market_cap)}
          </span>
        </div>

        <div className="h-12 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sparklineData}>
              <defs>
                <linearGradient
                  id={`gradient-${data.crypto}`}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                fill={`url(#gradient-${data.crypto})`}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
