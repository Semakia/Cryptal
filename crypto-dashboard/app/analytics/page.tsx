import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { VolatilityChart } from "@/components/analytics/volatility-chart";
import { SharpeChart } from "@/components/analytics/sharpe-chart";
import { MaxDrawdownCard } from "@/components/analytics/max-drawdown-card";

export default function AnalyticsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Risk metrics and performance analysis
          </p>
        </div>

        <Tabs defaultValue="volatility" className="space-y-6">
          <TabsList>
            <TabsTrigger value="volatility">Volatility</TabsTrigger>
            <TabsTrigger value="sharpe">Sharpe Ratio</TabsTrigger>
            <TabsTrigger value="drawdown">Drawdown</TabsTrigger>
          </TabsList>

          <TabsContent value="volatility" className="space-y-6">
            <VolatilityChart />
          </TabsContent>

          <TabsContent value="sharpe" className="space-y-6">
            <SharpeChart />
          </TabsContent>

          <TabsContent value="drawdown" className="space-y-6">
            <MaxDrawdownCard />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
