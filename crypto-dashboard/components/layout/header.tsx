"use client";

import { useAppState } from "@/lib/store";
import { formatDateTime } from "@/lib/utils";
import { Moon, Sun, TrendingUp, Menu } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, BarChart3, Grid3X3, Calculator } from "lucide-react";

const navItems = [
  { title: "Dashboard", href: "/", icon: LayoutDashboard },
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "Correlation", href: "/correlation", icon: Grid3X3 },
  { title: "Simulator", href: "/simulator", icon: Calculator },
];

export function Header() {
  const { period, setPeriod, lastUpdated } = useAppState();
  const { theme, setTheme } = useTheme();
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 bg-card/80 backdrop-blur-sm border-b border-border">
      <div className="flex items-center justify-between h-16 px-4 lg:px-6">
        <div className="flex items-center gap-3 lg:hidden">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 bg-sidebar p-0">
              <div className="flex items-center gap-3 h-16 px-4 border-b border-sidebar-border">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <span className="font-semibold text-lg text-sidebar-foreground">
                  CrypTal
                </span>
              </div>
              <nav className="p-3 space-y-1">
                {navItems.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        isActive
                          ? "bg-sidebar-accent text-sidebar-accent-foreground"
                          : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50",
                      )}
                    >
                      <item.icon className="w-5 h-5 flex-shrink-0" />
                      <span>{item.title}</span>
                    </Link>
                  );
                })}
              </nav>
            </SheetContent>
          </Sheet>
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg">CrypTal</span>
          </div>
        </div>

        <div className="hidden lg:block" />

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span>Updated {formatDateTime(lastUpdated)}</span>
            </div>
          )}

          <Select
            value={period}
            onValueChange={(v) => setPeriod(v as typeof period)}
          >
            <SelectTrigger className="w-24 h-9">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">24h</SelectItem>
              <SelectItem value="7">7d</SelectItem>
              <SelectItem value="30">30d</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
