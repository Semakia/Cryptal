"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

type Period = "1" | "7" | "30";

interface AppState {
  period: Period;
  setPeriod: (period: Period) => void;
  lastUpdated: Date | null;
  setLastUpdated: (date: Date) => void;
}

const AppStateContext = createContext<AppState | undefined>(undefined);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [period, setPeriod] = useState<Period>("7");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  return (
    <AppStateContext.Provider
      value={{ period, setPeriod, lastUpdated, setLastUpdated }}
    >
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used within AppStateProvider");
  }
  return context;
}
