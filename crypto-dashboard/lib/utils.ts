import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number, decimals = 2): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatCompactCurrency(value: number): string {
  if (value >= 1e12) {
    return `$${(value / 1e12).toFixed(2)}T`;
  }
  if (value >= 1e9) {
    return `$${(value / 1e9).toFixed(2)}B`;
  }
  if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(2)}M`;
  }
  if (value >= 1e3) {
    return `$${(value / 1e3).toFixed(2)}K`;
  }
  return formatCurrency(value);
}

export function formatPercent(
  value: number | undefined,
  decimals = 2,
): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "—";
  }

  return `${value >= 0 ? "+" : ""}${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number, decimals = 2): string {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatDate(date?: string | Date | null): string {
  if (!date) return "—";

  const d = new Date(date);
  if (isNaN(d.getTime())) return "—";

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(d);
}

export function formatDateForPeriod(
  date: string | Date | number,
  period: number,
): string {
  const d = new Date(date);

  if (period <= 1) {
    // 24h: show time (e.g., "2:00 PM")
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(d);
  } else if (period <= 7) {
    // 7 days: show day and time (e.g., "Mon 2PM" or "Dec 20")
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
    }).format(d);
  } else if (period <= 30) {
    // 30 days: show month and day (e.g., "Dec 20")
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
    }).format(d);
  } else {
    // 90+ days: show month and day (e.g., "Dec 20")
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
    }).format(d);
  }
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function formatDateTimeForPeriod(
  date: string | Date | number,
  period: number,
): string {
  const d = new Date(date);

  if (period <= 1) {
    // 24h: show full date and time
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(d);
  } else {
    // 7+ days: show date and time
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(d);
  }
}

export const CRYPTO_COLORS: Record<string, string> = {
  bitcoin: "#F7931A",
  ethereum: "#627EEA",
  binancecoin: "#F3BA2F",
  solana: "#9945FF",
  hyperliquid: "#00D4AA",
};

export const CRYPTO_NAMES: Record<string, string> = {
  bitcoin: "Bitcoin",
  ethereum: "Ethereum",
  binancecoin: "BNB",
  solana: "Solana",
  hyperliquid: "Hyperliquid",
};

export const CRYPTO_SYMBOLS: Record<string, string> = {
  bitcoin: "BTC",
  ethereum: "ETH",
  binancecoin: "BNB",
  solana: "SOL",
  hyperliquid: "HYPE",
};
