import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CorrelationHeatmap } from "@/components/correlation/correlation-heatmap"

export default function CorrelationPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Correlation Analysis</h1>
          <p className="text-muted-foreground">
            Understand relationships between cryptocurrencies for better portfolio diversification
          </p>
        </div>

        <CorrelationHeatmap />
      </div>
    </DashboardLayout>
  )
}
