"use client";

// Visite guidée interactive du dashboard CrypTal, propulsée par driver.js.
// Elle surligne les vrais éléments de l'UI, démarre automatiquement à la
// première visite et reste relançable via le bouton de la barre supérieure.

import { useCallback, useEffect } from "react";
import { usePathname } from "next/navigation";
import { driver, type DriveStep } from "driver.js";
import "driver.js/dist/driver.css";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const TOUR_SEEN_KEY = "cryptal_tour_seen_v1";

// Toutes les étapes possibles. Celles rattachées à un élément absent ou masqué
// (ex. la sidebar sur mobile) sont filtrées avant le lancement.
const ALL_STEPS: DriveStep[] = [
  {
    popover: {
      title: "Welcome to CrypTal 👋",
      description:
        "Take a 30-second tour of the dashboard. Use the arrows, your keyboard, or press Esc to leave anytime.",
    },
  },
  {
    element: '[data-tour="sidebar"]',
    popover: {
      title: "Navigation",
      description:
        "Switch between the four views: Dashboard, Analytics, Correlation and Simulator.",
    },
  },
  {
    element: '[data-tour="price-grid"]',
    popover: {
      title: "Live prices",
      description:
        "The top cryptocurrencies, with prices refreshed automatically every 60 seconds.",
    },
  },
  {
    element: '[data-tour="historical-chart"]',
    popover: {
      title: "Historical chart",
      description: "Price evolution over the selected time range.",
    },
  },
  {
    element: '[data-tour="period"]',
    popover: {
      title: "Time range",
      description: "Switch between 24h, 7d and 30d — it updates every view.",
    },
  },
  {
    element: '[data-tour="nav-analytics"]',
    popover: {
      title: "Analytics",
      description:
        "Advanced financial metrics: volatility, Sharpe ratio and drawdown.",
    },
  },
  {
    element: '[data-tour="nav-simulator"]',
    popover: {
      title: "Investment simulator",
      description:
        "Project a profit & loss on a hypothetical position over time.",
    },
  },
  {
    popover: {
      title: "You're all set 🚀",
      description:
        "Replay this tour anytime from the ✨ button in the top bar.",
    },
  },
];

function isVisible(selector: string): boolean {
  if (typeof document === "undefined") return false;
  const el = document.querySelector<HTMLElement>(selector);
  return !!el && el.offsetParent !== null;
}

function markSeen(): void {
  try {
    localStorage.setItem(TOUR_SEEN_KEY, "1");
  } catch {
    // localStorage indisponible (navigation privée…) : on ignore.
  }
}

function hasSeen(): boolean {
  try {
    return localStorage.getItem(TOUR_SEEN_KEY) === "1";
  } catch {
    return true; // en cas de doute, ne pas relancer automatiquement.
  }
}

function runTour(): void {
  const steps = ALL_STEPS.filter(
    (step) => !step.element || isVisible(step.element as string),
  );
  if (steps.length === 0) return;

  const tour = driver({
    showProgress: true,
    allowClose: true,
    overlayColor: "hsl(222 47% 6%)",
    nextBtnText: "Next",
    prevBtnText: "Back",
    doneBtnText: "Done",
    steps,
    onDestroyed: markSeen,
  });
  tour.drive();
}

export function TourButton() {
  const pathname = usePathname();

  const start = useCallback(() => runTour(), []);

  // Démarrage automatique une seule fois, sur le dashboard, après un court délai
  // laissant le temps aux données (prix, graphique) de se monter.
  useEffect(() => {
    if (pathname !== "/" || hasSeen()) return;
    const timer = setTimeout(runTour, 1200);
    return () => clearTimeout(timer);
  }, [pathname]);

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={start}
      aria-label="Guided tour"
      title="Guided tour"
    >
      <Sparkles className="h-5 w-5" />
    </Button>
  );
}
