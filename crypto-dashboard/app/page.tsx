import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { PriceGrid } from "@/components/dashboard/price-grid"
import { HistoricalChart } from "@/components/dashboard/historical-chart"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Real-time cryptocurrency prices and market data</p>
        </div>

        <div data-tour="price-grid">
          <PriceGrid />
        </div>
        <div data-tour="historical-chart">
          <HistoricalChart />
        </div>
      </div>
    </DashboardLayout>
  )
}
