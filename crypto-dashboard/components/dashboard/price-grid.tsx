"use client"

import { useLatestPrices } from "@/hooks/use-crypto-data"
import { PriceCard } from "./price-card"
import { PriceCardSkeleton } from "@/components/shared/loading-skeleton"
import { ErrorState } from "@/components/shared/error-state"
import { EmptyState } from "@/components/shared/empty-state"

export function PriceGrid() {
  const { data, isLoading, error, refetch } = useLatestPrices()

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <PriceCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (error) {
    return <ErrorState message={error.message} onRetry={() => refetch()} />
  }

  if (!data?.prices?.length) {
    return <EmptyState title="No prices available" description="Price data is currently unavailable." />
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
      {data.prices.map((price) => (
        <PriceCard key={price.crypto} data={price} />
      ))}
    </div>
  )
}
