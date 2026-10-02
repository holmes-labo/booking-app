import { useTranslation } from "react-i18next"
import { useEffect, useState } from "react"

import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import { API_URL } from "@/lib/api"


export function SectionCards() {
  
  const { t } = useTranslation()

  type DashboardSummary = {
    appointments_today: number
    revenue_today: number
    clients_today: number
    occupancy_rate: number
  }

  const [summary, setSummary] =
    useState<DashboardSummary | null>(null)

  useEffect(() => {
    const today = new Date().toLocaleDateString("en-CA")

    fetch(
      `${API_URL}/businesses/1/dashboard/summary?target_date=${today}`
    )
      .then((response) => response.json())
      .then((data: DashboardSummary) => {
        setSummary(data)
      })
  }, [])

  return (
    <div className="grid grid-cols-1 gap-4 px-4 lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      <Card>
        <CardHeader>
          <CardDescription>
            {t("dashboard.appointmentsToday")}
          </CardDescription>

          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {summary?.appointments_today ?? "—"}
          </CardTitle>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>
            {t("dashboard.revenueToday")}
          </CardDescription>

          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {summary?.revenue_today !== undefined
              ? `${summary.revenue_today.toFixed(2)} €`
              : "—"}
          </CardTitle>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>
            {t("dashboard.clientsToday")}
          </CardDescription>

          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {summary?.clients_today ?? "—"}
          </CardTitle>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>
            {t("dashboard.occupancyRate")}
          </CardDescription>

          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {summary?.occupancy_rate !== undefined
              ? `${summary.occupancy_rate.toFixed(1)} %`
              : "—"}
          </CardTitle>
        </CardHeader>
      </Card>
    </div>
  )
}