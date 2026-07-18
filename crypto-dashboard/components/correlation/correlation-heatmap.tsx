"use client";

import { useCorrelation } from "@/hooks/use-crypto-data";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ChartSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { formatNumber, CRYPTO_NAMES, CRYPTO_SYMBOLS } from "@/lib/utils";
import { useState, useMemo } from "react";
import { Shield, Link2, Unlink } from "lucide-react";

const CRYPTOS = ["bitcoin", "ethereum", "binancecoin", "solana", "hyperliquid"];

function getCorrelationColor(value: number): string {
  // Adjusted color scale for crypto (most correlations are 0.8-1.0)
  // This provides better visual differentiation in the typical crypto range
  if (value >= 0.95) return "bg-red-600"; // Very high - poor diversification
  if (value >= 0.9) return "bg-red-500"; // High - limited diversification
  if (value >= 0.85) return "bg-orange-500"; // Moderate-high
  if (value >= 0.8) return "bg-yellow-500"; // Moderate
  if (value >= 0.7) return "bg-green-400"; // Good for crypto!
  if (value >= 0.5) return "bg-green-500"; // Very good
  if (value >= 0) return "bg-blue-400"; // Excellent (rare in crypto)
  if (value >= -0.3) return "bg-blue-500"; // Outstanding
  return "bg-blue-600"; // Perfect hedge (very rare)
}

function getCorrelationText(value: number): string {
  // Adjusted interpretation for crypto markets
  if (value >= 0.95) return "Very High (poor diversification)";
  if (value >= 0.9) return "High (limited diversification)";
  if (value >= 0.85) return "Moderate-High";
  if (value >= 0.8) return "Moderate (typical for crypto)";
  if (value >= 0.7) return "Good (better than average)";
  if (value >= 0.5) return "Very Good (rare in crypto)";
  if (value >= 0) return "Excellent (uncommon)";
  return "Outstanding (negative correlation)";
}

function getDiversificationRecommendation(
  score: number,
  lowestPair: any,
): {
  message: string;
  suggestions: string[];
} {
  if (score >= 30) {
    return {
      message: "🌟 Excellent diversification for a crypto portfolio!",
      suggestions: [
        "Your portfolio has good variety",
        "Consider rebalancing periodically",
        "Monitor correlations as markets change",
      ],
    };
  } else if (score >= 15) {
    return {
      message: "✅ Moderate diversification",
      suggestions: [
        `Best pair: ${lowestPair?.crypto_1?.toUpperCase()} / ${lowestPair?.crypto_2?.toUpperCase()}`,
        "Add stablecoins (USDC, USDT) for stability",
        "Consider traditional assets (stocks, bonds)",
      ],
    };
  } else {
    return {
      message: "⚠️ Low diversification - high risk!",
      suggestions: [
        "Cryptos move together (follow Bitcoin)",
        "Add stablecoins (50%+ recommended)",
        "Diversify into traditional assets",
        "Consider DeFi protocols with different risk profiles",
        `Least correlated: ${lowestPair?.crypto_1?.toUpperCase()} / ${lowestPair?.crypto_2?.toUpperCase()}`,
      ],
    };
  }
}

export function CorrelationHeatmap() {
  const { data, isLoading, error, refetch } = useCorrelation();
  const [hoveredCell, setHoveredCell] = useState<{
    row: number;
    col: number;
  } | null>(null);

  const matrix = useMemo(() => {
    if (!data) return [];

    const result: (number | null)[][] = CRYPTOS.map(() =>
      CRYPTOS.map(() => null),
    );

    data.correlations.forEach((c) => {
      const i = CRYPTOS.indexOf(c.crypto_1);
      const j = CRYPTOS.indexOf(c.crypto_2);
      if (i !== -1 && j !== -1) {
        result[i][j] = c.correlation;
        result[j][i] = c.correlation;
      }
    });

    CRYPTOS.forEach((_, i) => {
      result[i][i] = 1;
    });

    return result;
  }, [data]);

  // Calculate diversification metrics from correlation data
  const diversificationMetrics = useMemo(() => {
    if (!data?.correlations || data.correlations.length === 0) {
      return {
        diversificationScore: 0,
        lowestCorrelation: null,
        highestCorrelation: null,
      };
    }

    // Find highest and lowest correlations (excluding self-correlations)
    const nonSelfCorrelations = data.correlations.filter(
      (c) => c.crypto_1 !== c.crypto_2,
    );

    if (nonSelfCorrelations.length === 0) {
      return {
        diversificationScore: 0,
        lowestCorrelation: null,
        highestCorrelation: null,
      };
    }

    const lowest = nonSelfCorrelations.reduce((min, c) =>
      c.correlation < min.correlation ? c : min,
    );

    const highest = nonSelfCorrelations.reduce((max, c) =>
      c.correlation > max.correlation ? c : max,
    );

    // Calculate diversification score: 100 - (average correlation * 100)
    const avgCorrelation =
      nonSelfCorrelations.reduce((sum, c) => sum + Math.abs(c.correlation), 0) /
      nonSelfCorrelations.length;
    const diversificationScore = Math.max(
      0,
      Math.round((1 - avgCorrelation) * 100),
    );

    return {
      diversificationScore,
      lowestCorrelation: lowest,
      highestCorrelation: highest,
    };
  }, [data]);

  if (isLoading) return <ChartSkeleton />;
  if (error)
    return <ErrorState message={error.message} onRetry={() => refetch()} />;

  const recommendation = getDiversificationRecommendation(
    diversificationMetrics.diversificationScore,
    diversificationMetrics.lowestCorrelation,
  );

  return (
    <div className="space-y-6">
      {/* Warning banner for high correlations */}
      {diversificationMetrics.diversificationScore < 15 && (
        <Card className="border-2 border-orange-500/50 bg-orange-500/5">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <div className="text-2xl">⚠️</div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-2">
                  High Correlation Warning
                </h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Your crypto assets are highly correlated (95%+ average). When
                  Bitcoin moves, they all move together. This means limited
                  diversification benefit.
                </p>
                <div className="bg-background/50 rounded-lg p-3 space-y-2">
                  <p className="text-xs font-semibold">
                    💡 To truly diversify your portfolio:
                  </p>
                  {recommendation.suggestions.map((suggestion, idx) => (
                    <p key={idx} className="text-xs text-muted-foreground">
                      • {suggestion}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Shield className="w-4 h-4" />
              <span className="text-sm">Diversification Score</span>
            </div>
            <span className="text-3xl font-bold text-primary">
              {diversificationMetrics.diversificationScore}%
            </span>
            <p className="text-xs text-muted-foreground mt-1">
              Higher = better diversification
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Unlink className="w-4 h-4" />
              <span className="text-sm">Best Pair</span>
            </div>
            {diversificationMetrics.lowestCorrelation && (
              <>
                <span className="text-lg font-bold">
                  {
                    CRYPTO_SYMBOLS[
                      diversificationMetrics.lowestCorrelation.crypto_1
                    ]
                  }{" "}
                  /{" "}
                  {
                    CRYPTO_SYMBOLS[
                      diversificationMetrics.lowestCorrelation.crypto_2
                    ]
                  }
                </span>
                <p className="text-sm text-blue-500 font-mono">
                  {formatNumber(
                    diversificationMetrics.lowestCorrelation.correlation,
                    3,
                  )}
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Link2 className="w-4 h-4" />
              <span className="text-sm">Most Correlated</span>
            </div>
            {diversificationMetrics.highestCorrelation && (
              <>
                <span className="text-lg font-bold">
                  {
                    CRYPTO_SYMBOLS[
                      diversificationMetrics.highestCorrelation.crypto_1
                    ]
                  }{" "}
                  /{" "}
                  {
                    CRYPTO_SYMBOLS[
                      diversificationMetrics.highestCorrelation.crypto_2
                    ]
                  }
                </span>
                <p className="text-sm text-red-500 font-mono">
                  {formatNumber(
                    diversificationMetrics.highestCorrelation.correlation,
                    3,
                  )}
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Correlation Matrix</CardTitle>
          <CardDescription>
            Price correlation between cryptocurrencies (Green/Blue = better
            diversification, Red = moves together)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <div className="inline-block min-w-full">
              <div className="flex">
                <div className="w-20" />
                {CRYPTOS.map((crypto) => (
                  <div
                    key={crypto}
                    className="w-16 text-center text-xs font-medium text-muted-foreground py-2"
                  >
                    {CRYPTO_SYMBOLS[crypto]}
                  </div>
                ))}
              </div>

              {matrix.map((row, i) => (
                <div key={i} className="flex">
                  <div className="w-20 flex items-center text-xs font-medium text-muted-foreground pr-2">
                    {CRYPTO_SYMBOLS[CRYPTOS[i]]}
                  </div>
                  {row.map((value, j) => {
                    const isHovered =
                      hoveredCell?.row === i ||
                      hoveredCell?.col === j ||
                      (hoveredCell?.row === i && hoveredCell?.col === j);

                    return (
                      <div
                        key={j}
                        className="relative group"
                        onMouseEnter={() => setHoveredCell({ row: i, col: j })}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <div
                          className={`w-16 h-12 flex items-center justify-center text-xs font-mono transition-all cursor-pointer border border-background ${getCorrelationColor(
                            value || 0,
                          )} ${isHovered ? "ring-2 ring-primary z-10" : ""} ${i === j ? "opacity-50" : ""}`}
                        >
                          <span
                            className={
                              Math.abs(value || 0) > 0.5
                                ? "text-white"
                                : "text-foreground"
                            }
                          >
                            {value !== null ? formatNumber(value, 2) : "-"}
                          </span>
                        </div>

                        {hoveredCell?.row === i &&
                          hoveredCell?.col === j &&
                          i !== j && (
                            <div className="absolute z-20 bottom-full left-1/2 -translate-x-1/2 mb-2 bg-popover border border-border rounded-lg p-3 shadow-lg whitespace-nowrap">
                              <p className="font-medium text-sm">
                                {CRYPTO_NAMES[CRYPTOS[i]]} -{" "}
                                {CRYPTO_NAMES[CRYPTOS[j]]}
                              </p>
                              <p className="text-lg font-mono font-bold">
                                {formatNumber(value || 0, 3)}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {getCorrelationText(value || 0)}
                              </p>
                            </div>
                          )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 mt-6 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded" />
              <span>&lt; 0.5 (Excellent)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded" />
              <span>0.5-0.8 (Good)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded" />
              <span>0.8-0.85 (Moderate)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-500 rounded" />
              <span>0.85-0.9 (High)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-600 rounded" />
              <span>&gt; 0.95 (Very High)</span>
            </div>
          </div>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="text-sm font-semibold mb-2">
              Understanding Crypto Correlations
            </h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>
                • <strong>Why so high?</strong> Bitcoin dominates the market -
                when it moves, everything follows
              </li>
              <li>
                • <strong>&lt; 0.80</strong>: Good diversification for crypto
                (rare!)
              </li>
              <li>
                • <strong>0.80-0.90</strong>: Typical for major cryptocurrencies
              </li>
              <li>
                • <strong>&gt; 0.95</strong>: Nearly identical movement - poor
                diversification
              </li>
              <li>
                • <strong>Portfolio tip</strong>: Combine crypto with
                stablecoins, traditional stocks, or bonds for real
                diversification
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
