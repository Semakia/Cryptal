"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { api, type PnLSimulationRequest } from "@/lib/api";
import { useAppState } from "@/lib/store";
import { useEffect } from "react";

export function useLatestPrices() {
  const { setLastUpdated, period } = useAppState();

  const query = useQuery({
    queryKey: ["latestPrices", period],
    queryFn: () => api.getLatestPrices(Number(period)),
    refetchInterval: 60000, // Refresh every 60 seconds
    staleTime: 50000,
  });

  useEffect(() => {
    if (query.data?.last_updated) {
      setLastUpdated(new Date(query.data.last_updated));
    }
  }, [query.data?.last_updated, setLastUpdated]);

  return query;
}

export function useHistoricalPrices(crypto: string) {
  const { period } = useAppState();

  return useQuery({
    queryKey: ["historicalPrices", crypto, period],
    queryFn: () => api.getHistoricalPrices(crypto, Number(period)),
    enabled: !!crypto,
    staleTime: 300000, // 5 minutes
  });
}

export function useVolatility() {
  const { period } = useAppState();

  return useQuery({
    queryKey: ["volatility", period],
    queryFn: () => api.getVolatility(Number(period)),
    staleTime: 300000, // 5 minutes
  });
}

export function useSharpe(riskFreeRate = 0.02) {
  const { period } = useAppState();

  return useQuery({
    queryKey: ["sharpe", period, riskFreeRate],
    queryFn: () => api.getSharpe(Number(period), riskFreeRate),
    staleTime: 300000, // 5 minutes
  });
}

export function useDrawdown() {
  const { period } = useAppState();

  return useQuery({
    queryKey: ["drawdown", period],
    queryFn: () => api.getDrawdown(Number(period)),
    staleTime: 300000, // 5 minutes
  });
}

export function useCorrelation() {
  const { period } = useAppState();

  return useQuery({
    queryKey: ["correlation", period],
    queryFn: () => api.getCorrelation(Number(period)),
    staleTime: 300000, // 5 minutes
  });
}

export function useSimulatePnL() {
  return useMutation({
    mutationFn: (data: PnLSimulationRequest) => api.simulatePnL(data),
  });
}

export function useComparePnL() {
  return useMutation({
    mutationFn: ({
      amount,
      purchaseDate,
    }: {
      amount: number;
      purchaseDate: string;
    }) => api.comparePnL(amount, purchaseDate),
  });
}

export function useBestEntry(
  crypto: string,
  amount: number,
  lookbackDays = 30,
) {
  return useQuery({
    queryKey: ["bestEntry", crypto, amount, lookbackDays],
    queryFn: () => api.getBestEntry(crypto, amount, lookbackDays),
    enabled: !!crypto && amount > 0,
    staleTime: 600000, // 10 minutes
  });
}

export function useCryptos() {
  return useQuery({
    queryKey: ["cryptos"],
    queryFn: api.getCryptos,
    staleTime: 3600000, // 1 hour
  });
}

export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.healthCheck,
    refetchInterval: 30000, // 30 seconds
    retry: 1,
  });
}
