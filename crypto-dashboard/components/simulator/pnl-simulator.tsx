"use client"

import { useState } from "react"
import { useSimulatePnL, useComparePnL, useBestEntry } from "@/hooks/use-crypto-data"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { formatCurrency, formatPercent, formatDate, formatNumber, CRYPTO_NAMES, cn } from "@/lib/utils"
import { Calculator, TrendingUp, TrendingDown, Star, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

const CRYPTOS = ["bitcoin", "ethereum", "binancecoin", "solana", "hyperliquid"]
const QUICK_AMOUNTS = [100, 500, 1000, 5000]

export function PnLSimulator() {
  const [crypto, setCrypto] = useState("bitcoin")
  const [amount, setAmount] = useState("1000")
  const [purchaseDate, setPurchaseDate] = useState(() => {
    const d = new Date()
    d.setDate(d.getDate() - 7)
    return d.toISOString().split("T")[0]
  })
  const [showComparison, setShowComparison] = useState(false)
  const [showBestEntry, setShowBestEntry] = useState(false)
  const { toast } = useToast()
  const simulateMutation = useSimulatePnL()
  const compareMutation = useComparePnL()
  const compareItems = compareMutation.data
  const { data: bestEntryData, isLoading: bestEntryLoading } = useBestEntry(
    showBestEntry ? crypto : "",
    showBestEntry ? Number(amount) : 0,
    30,
  )

  const handleSimulate = () => {
    if (!amount || Number(amount) <= 0) {
      toast({ title: "Invalid amount", description: "Please enter a valid investment amount", variant: "destructive" })
      return
    }

    simulateMutation.mutate({
      crypto,
      amount: Number(amount),
      purchase_date: new Date(purchaseDate).toISOString(),
    })
    setShowComparison(false)
    setShowBestEntry(false)
  }

  const handleCompare = () => {
    if (!amount || Number(amount) <= 0) {
      toast({ title: "Invalid amount", description: "Please enter a valid investment amount", variant: "destructive" })
      return
    }

    compareMutation.mutate({
      amount: Number(amount),
      purchaseDate: new Date(purchaseDate).toISOString(),
    })
    setShowComparison(true)
    setShowBestEntry(false)
  }

  const result = simulateMutation.data
  const currentPrice = result?.sell_price ?? 0

  const compareResult = compareMutation.data

  const maxDate = new Date().toISOString().split("T")[0]

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="w-5 h-5" />
              Investment Simulator
            </CardTitle>
            <CardDescription>Simulate returns on historical cryptocurrency investments</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="crypto">Cryptocurrency</Label>
              <Select value={crypto} onValueChange={setCrypto}>
                <SelectTrigger id="crypto">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CRYPTOS.map((c) => (
                    <SelectItem key={c} value={c}>
                      {CRYPTO_NAMES[c]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="amount">Investment Amount (USD)</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="amount"
                  type="number"
                  min="1"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="pl-7"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                {QUICK_AMOUNTS.map((qa) => (
                  <Button
                    key={qa}
                    variant="outline"
                    size="sm"
                    onClick={() => setAmount(String(qa))}
                    className={cn("text-xs", amount === String(qa) && "bg-primary text-primary-foreground")}
                  >
                    ${qa.toLocaleString()}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date">Purchase Date</Label>
              <Input
                id="date"
                type="date"
                max={maxDate}
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
              />
            </div>

            <div className="flex flex-col gap-2 pt-2">
              <Button onClick={handleSimulate} disabled={simulateMutation.isPending}>
                {simulateMutation.isPending ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Calculator className="w-4 h-4 mr-2" />
                )}
                Simulate Investment
              </Button>

              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" onClick={handleCompare} disabled={compareMutation.isPending}>
                  {compareMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Compare All
                </Button>
                <Button variant="outline" onClick={() => setShowBestEntry(!showBestEntry)}>
                  <Star className="w-4 h-4 mr-2" />
                  Best Entry
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {showBestEntry && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5 text-warning" />
                Best Entry Point
              </CardTitle>
              <CardDescription>Optimal historical entry for {CRYPTO_NAMES[crypto]}</CardDescription>
            </CardHeader>
            <CardContent>
              {bestEntryLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
              ) : bestEntryData ? (
                <div className="space-y-4">
                  <div className="p-4 bg-success/10 border border-success/20 rounded-lg">
                    <p className="text-sm text-muted-foreground">Best Entry Date</p>
                    <p className="text-xl font-bold text-success">{formatDate(bestEntryData.best_entry_date)}</p>
                    <p className="text-sm">Price: {formatCurrency(bestEntryData.best_entry_price)}</p>
                    <p className="text-lg font-bold text-success mt-2">
                      ROI: {formatPercent(bestEntryData.pnl_percentage)}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Run simulation first to see best entry analysis
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      <div className="space-y-6">
        {result && (
          <Card>
            <CardHeader>
              <CardTitle>Simulation Results</CardTitle>
              <CardDescription>
                {CRYPTO_NAMES[result.coin_id]} - {formatDate(result.purchase_date)}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Purchase Price</p>
                  <p className="text-lg font-bold">{formatCurrency(result.purchase_price)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Current Price</p>
                  <p className="text-lg font-bold">{formatCurrency(currentPrice)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Quantity Bought</p>
                  <p className="text-lg font-mono">{formatNumber(result.quantity, 8)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Investment</p>
                  <p className="text-lg font-bold">{formatCurrency(result.investment_amount)}</p>
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Current Value</p>
                    <p className="text-2xl font-bold">{formatCurrency(result.current_value)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">P&L</p>
                    <p
                      className={cn(
                        "text-2xl font-bold flex items-center gap-2",
                        result.pnl >= 0 ? "text-success" : "text-destructive",
                      )}
                    >
                      {result.pnl >= 0 ? <TrendingUp className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />}
                      {formatCurrency(result.pnl)}
                    </p>
                  </div>
                </div>
              </div>

              <div
                className={cn(
                  "p-4 rounded-lg text-center",
                  result.roi >= 0
                    ? "bg-success/10 border border-success/20"
                    : "bg-destructive/10 border border-destructive/20",
                )}
              >
                <p className="text-sm text-muted-foreground mb-1">Return on Investment</p>
                <p className={cn("text-4xl font-bold", result.roi >= 0 ? "text-success" : "text-destructive")}>
                  {formatPercent(result.roi)}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {showComparison && compareResult && (
          <Card>
            <CardHeader>
              <CardTitle>Comparison Results</CardTitle>
              <CardDescription>
                ROI comparison for {formatCurrency(Number(amount))} invested on{" "}
                {formatDate(purchaseDate)}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rank</TableHead>
                    <TableHead>Crypto</TableHead>
                    <TableHead className="text-right">Current Value</TableHead>
                    <TableHead className="text-right">P&L</TableHead>
                    <TableHead className="text-right">ROI</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[...compareItems]
                    .sort((a, b) => b.roi - a.roi)
                    .map((c, i) => (
                      <TableRow key={c.coin_id}>
                        <TableCell>{i < 3 ? ["🥇", "🥈", "🥉"][i] : i + 1}</TableCell>
                        <TableCell className="font-medium">{CRYPTO_NAMES[c.coin_id]}</TableCell>
                        <TableCell className="text-right font-mono">{formatCurrency(c.current_value)}</TableCell>
                        <TableCell
                          className={cn("text-right font-mono", c.pnl >= 0 ? "text-success" : "text-destructive")}
                        >
                          {formatCurrency(c.pnl)}
                        </TableCell>
                        <TableCell
                          className={cn(
                            "text-right font-mono font-bold",
                            c.roi >= 0 ? "text-success" : "text-destructive",
                          )}
                        >
                          {formatPercent(c.roi)}
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {!result && !showComparison && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <Calculator className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No simulation yet</h3>
              <p className="text-sm text-muted-foreground">
                Configure your investment parameters and click Simulate to see results
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
