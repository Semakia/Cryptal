import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { PnLSimulator } from "@/components/simulator/pnl-simulator"

export default function SimulatorPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">P&L Simulator</h1>
          <p className="text-muted-foreground">Simulate and compare investment returns across cryptocurrencies</p>
        </div>

        <PnLSimulator />
      </div>
    </DashboardLayout>
  )
}
