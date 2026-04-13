const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============================================================================
// API Response Types (matching real backend)
// ============================================================================

// Data endpoints
export interface PriceData {
  id: number;
  coin_id: string;
  price_usd: number;
  price_eur: number;
  price_gbp: number;
  change_24h: number | null;
  market_cap: number | null;
  timestamp: string;
}

export interface LatestPricesResponse {
  data: PriceData[];
  count: number;
  last_update: string | null;
}

export interface HistoricalPricesResponse {
  data: PriceData[];
}

export interface CryptoInfo {
  coin_id: string;
  data_points: number;
  earliest_date: string | null;
  latest_date: string | null;
}

// Metrics endpoints
export interface VolatilityMetrics {
  coin_id: string;
  period_days: number;
  data_points: number;
  mean_price: number;
<<<<<<< HEAD
  std_dev: number;
  variance: number;
  coefficient_of_variation: number;
  var_95: number;
=======
  annualized_volatility: number;
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
  min_price: number;
  max_price: number;
  price_range: number;
}

export interface SharpeMetrics {
  coin_id: string;
  period_days: number;
  data_points: number;
<<<<<<< HEAD
  total_return: number;
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
=======
  total_return: number; // Actual return over the period (e.g., -9% over 30 days)
  annualized_return: number; // Hypothetical if trend continues (use total_return instead!)
  annualized_volatility: number; // Standard: volatility scaled to annual basis
  sharpe_ratio: number; // Based on actual returns, not annualized
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
  start_price: number;
  end_price: number;
}

export interface DrawdownMetrics {
  coin_id: string;
  period_days: number;
  data_points: number;
  max_drawdown_pct: number;
  max_drawdown_value: number;
<<<<<<< HEAD
  current_drawdown_pct: number;
  underwater_pct: number;
  peak_price: number;
  trough_price: number;
  current_price: number;
  peak_date: string | null;
  trough_date: string | null;
  drawdown_periods: Array<{
    start: string;
    drawdown: number;
  }>;
=======
  peak_price: number;
  trough_price: number;
  peak_date: string | null;
  trough_date: string | null;
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}

export interface CorrelationPair {
  crypto_1: string;
  crypto_2: string;
  correlation: number;
}

export interface CorrelationMatrix {
  period_days: number;
  correlations: CorrelationPair[];
<<<<<<< HEAD
  diversification_score: number;
  highest_correlation: CorrelationPair;
  lowest_correlation: CorrelationPair;
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}

// Simulation endpoints
export interface PnLSimulationRequest {
  crypto: string;
  amount: number;
  purchase_date: string;
}

export interface PnLSimulationResult {
  coin_id: string;
  investment_amount: number;
  purchase_date: string;
  purchase_price: number;
  quantity: number;
  sell_date: string;
  sell_price: number;
  current_value: number;
  pnl: number;
  roi: number;
}

export interface BestEntryPointResult {
  coin_id: string;
  investment_amount: number;
  lookback_days: number;
  best_entry_date: string;
  best_entry_price: number;
  quantity: number;
  current_price: number;
  current_value: number;
  pnl: number;
  pnl_percentage: number;
}

// ============================================================================
// Transformed Types (for frontend components)
// ============================================================================

export interface CryptoPrice {
  crypto: string;
  price: number;
  price_24h_ago: number;
  change_24h: number;
  change_24h_pct: number;
  market_cap: number;
  volume_24h: number;
  last_updated: string;
  sparkline: number[];
}

export interface TransformedLatestPrices {
  prices: CryptoPrice[];
  last_updated: string | null;
}

export interface HistoricalPrice {
  timestamp: string;
  price: number;
}

export interface TransformedHistoricalPrices {
  crypto: string;
  period_days: number;
  prices: HistoricalPrice[];
}

export interface VolatilityMetric {
  crypto: string;
<<<<<<< HEAD
  std_deviation: number;
  coefficient_of_variation: number;
  var_95: number;
=======
  annualized_volatility: number;
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
  price_range: {
    min: number;
    max: number;
  };
  mean_price: number;
}

export interface VolatilityResponse {
  period_days: number;
  metrics: VolatilityMetric[];
}

export interface SharpeMetric {
  crypto: string;
<<<<<<< HEAD
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  total_return: number;
=======
  annualized_return: number; // Hypothetical projection (misleading for short periods)
  annualized_volatility: number; // Standard annualized volatility
  sharpe_ratio: number; // Calculated using total_return (actual), not annualized
  total_return: number; // ACTUAL return over the period - use this for display!
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}

export interface SharpeResponse {
  period_days: number;
  risk_free_rate: number;
  metrics: SharpeMetric[];
}

export interface DrawdownMetric {
  crypto: string;
  max_drawdown: number;
<<<<<<< HEAD
  current_drawdown: number;
  time_underwater_pct: number;
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
  peak_date: string | null;
  peak_price: number;
  trough_date: string | null;
  trough_price: number;
<<<<<<< HEAD
  current_price: number;
  drawdown_periods: Array<{
    start: string;
    drawdown: number;
  }>;
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}

export interface DrawdownResponse {
  period_days: number;
  metrics: DrawdownMetric[];
}

// ============================================================================
// Helper Functions
// ============================================================================

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `API Error: ${response.status} ${response.statusText} - ${errorText}`,
    );
  }

  return response.json();
}

// Generate simple sparkline data from recent prices
function generateSparkline(prices: PriceData[], limit = 24): number[] {
  const recentPrices = prices.slice(-limit);
  return recentPrices.map((p) => p.price_usd);
}

// Calculate 24h change from historical data
function calculate24hChange(prices: PriceData[]): {
  change: number;
  changePct: number;
  price24hAgo: number;
} {
  if (prices.length < 2) {
    return { change: 0, changePct: 0, price24hAgo: prices[0]?.price_usd || 0 };
  }

  const latestPrice = prices[prices.length - 1].price_usd;
  const price24hAgo = prices[0].price_usd;
  const change = latestPrice - price24hAgo;
  const changePct = (change / price24hAgo) * 100;

  return { change, changePct, price24hAgo };
}

// ============================================================================
// API Client with Data Transformation
// ============================================================================

export const api = {
  // Get latest prices with sparkline data and period-specific change
  async getLatestPrices(period: number = 1): Promise<TransformedLatestPrices> {
    const response = await fetchApi<LatestPricesResponse>(
      "/api/data/prices/latest",
    );

    // Fetch recent historical data for each crypto to generate sparklines and calculate change
    const pricesWithSparklines = await Promise.all(
      response.data.map(async (priceData) => {
        try {
          // Get historical data for the selected period
          const historicalResponse = await fetchApi<PriceData[]>(
            `/api/data/prices/${priceData.coin_id}?days=${period}&limit=1000`,
          );

          if (historicalResponse.length === 0) {
            throw new Error("No historical data");
          }

          // Generate sparkline from recent data
          const sparkline = generateSparkline(
            historicalResponse,
            Math.min(24, historicalResponse.length),
          );

          // Calculate change for the selected period
          const oldestPrice = historicalResponse[0].price_usd;
          const latestPrice = priceData.price_usd;
          const change = latestPrice - oldestPrice;
          const changePct = (change / oldestPrice) * 100;

          return {
            crypto: priceData.coin_id,
            price: latestPrice,
            price_24h_ago: oldestPrice,
            change_24h: change,
            change_24h_pct: changePct,
            market_cap: priceData.market_cap || 0,
            volume_24h: 0, // Not available in API
            last_updated: priceData.timestamp,
            sparkline,
          };
        } catch (error) {
          console.warn(
            `Failed to fetch sparkline for ${priceData.coin_id}:`,
            error,
          );
          return {
            crypto: priceData.coin_id,
            price: priceData.price_usd,
            price_24h_ago: priceData.price_usd,
            change_24h: priceData.change_24h || 0,
            change_24h_pct: priceData.change_24h || 0,
            market_cap: priceData.market_cap || 0,
            volume_24h: 0,
            last_updated: priceData.timestamp,
            sparkline: [priceData.price_usd],
          };
        }
      }),
    );

    return {
      prices: pricesWithSparklines,
      last_updated: response.last_update,
    };
  },

  // Get historical prices
  async getHistoricalPrices(
    crypto: string,
    days: number,
  ): Promise<TransformedHistoricalPrices> {
    const response = await fetchApi<PriceData[]>(
      `/api/data/prices/${crypto}?days=${days}&limit=1000`,
    );

    return {
      crypto,
      period_days: days,
      prices: response.map((p) => ({
        timestamp: p.timestamp,
        price: p.price_usd,
      })),
    };
  },

  // Get volatility metrics
  async getVolatility(period: number): Promise<VolatilityResponse> {
    const response = await fetchApi<VolatilityMetrics[]>(
      `/api/metrics/volatility?period=${period}`,
    );

    return {
      period_days: period,
      metrics: response.map((m) => ({
        crypto: m.coin_id,
<<<<<<< HEAD
        std_deviation: m.std_dev,
        coefficient_of_variation: m.coefficient_of_variation,
        var_95: m.var_95,
=======
        annualized_volatility: m.annualized_volatility,
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        price_range: {
          min: m.min_price,
          max: m.max_price,
        },
        mean_price: m.mean_price,
      })),
    };
  },

  // Get Sharpe ratios
  async getSharpe(
    period: number,
    riskFreeRate = 0.02,
  ): Promise<SharpeResponse> {
    const response = await fetchApi<SharpeMetrics[]>(
      `/api/metrics/sharpe?period=${period}&risk_free_rate=${riskFreeRate}`,
    );

    return {
      period_days: period,
      risk_free_rate: riskFreeRate,
      metrics: response.map((m) => ({
        crypto: m.coin_id,
        annualized_return: m.annualized_return,
        annualized_volatility: m.annualized_volatility,
        sharpe_ratio: m.sharpe_ratio,
<<<<<<< HEAD
        sortino_ratio: m.sortino_ratio,
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        total_return: m.total_return,
      })),
    };
  },

  // Get drawdown metrics
  async getDrawdown(period: number): Promise<DrawdownResponse> {
    const response = await fetchApi<DrawdownMetrics[]>(
      `/api/metrics/drawdown?period=${period}`,
    );

    return {
      period_days: period,
      metrics: response.map((m) => ({
        crypto: m.coin_id,
        max_drawdown: m.max_drawdown_pct,
<<<<<<< HEAD
        current_drawdown: m.current_drawdown_pct,
        time_underwater_pct: m.underwater_pct,
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        peak_date: m.peak_date,
        peak_price: m.peak_price,
        trough_date: m.trough_date,
        trough_price: m.trough_price,
<<<<<<< HEAD
        current_price: m.current_price,
        drawdown_periods: m.drawdown_periods,
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
      })),
    };
  },

  // Get correlation matrix
  async getCorrelation(period: number): Promise<CorrelationMatrix> {
    return fetchApi<CorrelationMatrix>(
      `/api/metrics/correlation?period=${period}`,
    );
  },

  // Simulate P&L
  async simulatePnL(data: PnLSimulationRequest): Promise<PnLSimulationResult> {
    return fetchApi<PnLSimulationResult>("/api/simulate/pnl", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Compare P&L across all cryptos
  async comparePnL(
    amount: number,
    purchaseDate: string,
  ): Promise<PnLSimulationResult[]> {
    return fetchApi<PnLSimulationResult[]>(
      `/api/simulate/pnl/compare?amount=${amount}&purchase_date=${purchaseDate}`,
<<<<<<< HEAD
=======
      {
        method: "POST"
      }
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
    );
  },

  // Get best entry point
  async getBestEntry(
    crypto: string,
    amount: number,
    lookbackDays = 30,
  ): Promise<BestEntryPointResult> {
    return fetchApi<BestEntryPointResult>(
      `/api/simulate/best-entry/${crypto}?amount=${amount}&lookback_days=${lookbackDays}`,
    );
  },

  // Get list of tracked cryptocurrencies
  async getCryptos(): Promise<CryptoInfo[]> {
    return fetchApi<CryptoInfo[]>("/api/data/cryptos");
  },

  // Health check
  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    database: string;
  }> {
    return fetchApi("/health");
  },
};
