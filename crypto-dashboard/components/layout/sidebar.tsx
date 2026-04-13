<<<<<<< HEAD
"use client"

import { cn } from "@/lib/utils"
import { LayoutDashboard, BarChart3, Grid3X3, Calculator, ChevronLeft, TrendingUp } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { useState } from "react"
=======
"use client";

import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  BarChart3,
  Grid3X3,
  Calculator,
  ChevronLeft,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useState } from "react";
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

const navItems = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    title: "Correlation",
    href: "/correlation",
    icon: Grid3X3,
  },
  {
    title: "Simulator",
    href: "/simulator",
    icon: Calculator,
  },
<<<<<<< HEAD
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
=======
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

  return (
    <aside
      className={cn(
        "hidden lg:flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-64",
      )}
    >
      <div className="flex items-center gap-3 h-16 px-4 border-b border-sidebar-border">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent">
          <TrendingUp className="w-5 h-5 text-white" />
        </div>
<<<<<<< HEAD
        {!collapsed && <span className="font-semibold text-lg text-sidebar-foreground">Crypto Viz</span>}
=======
        {!collapsed && (
          <span className="font-semibold text-lg text-sidebar-foreground">
            CrypTal
          </span>
        )}
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            "ml-auto text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent",
            collapsed && "mx-auto ml-0",
          )}
          onClick={() => setCollapsed(!collapsed)}
        >
<<<<<<< HEAD
          <ChevronLeft className={cn("w-4 h-4 transition-transform", collapsed && "rotate-180")} />
=======
          <ChevronLeft
            className={cn(
              "w-4 h-4 transition-transform",
              collapsed && "rotate-180",
            )}
          />
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        </Button>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
<<<<<<< HEAD
          const isActive = pathname === item.href
=======
          const isActive = pathname === item.href;
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50",
                collapsed && "justify-center px-2",
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.title}</span>}
            </Link>
<<<<<<< HEAD
          )
=======
          );
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        })}
      </nav>

      <div className="p-3 border-t border-sidebar-border">
<<<<<<< HEAD
        {!collapsed && <div className="px-3 py-2 text-xs text-sidebar-foreground/50">v1.0.0</div>}
      </div>
    </aside>
  )
=======
        {!collapsed && (
          <div className="px-3 py-2 text-xs text-sidebar-foreground/50">
            v1.0.0
          </div>
        )}
      </div>
    </aside>
  );
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}
