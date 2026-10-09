'use client'

import { Scale, Wheat, Leaf, Waves } from 'lucide-react'
import type { FeedingResult } from '@/lib/feeding'
import { fmt, useI18n } from '@/lib/i18n'

const fmtKg = (kg: number) => (kg >= 1 ? `${kg.toFixed(2)} kg` : `${(kg * 1000).toFixed(0)} g`)

export function KpiCards({ result }: { result: FeedingResult }) {
  const { t } = useI18n()
  const pollutionCut =
    result.nitrogenBaseKg > 0 ? ((result.nitrogenBaseKg - result.nitrogenOptKg) / result.nitrogenBaseKg) * 100 : 0

  const items = [
    {
      key: 'feed',
      icon: Wheat,
      label: t.kpi.feed,
      value: result.suspended ? t.kpi.suspend : fmtKg(result.optimizedFeedKg),
      sub: fmt(t.kpi.standard, { v: fmtKg(result.baseFeedKg) }),
      emphasis: true,
    },
    {
      key: 'biomass',
      icon: Scale,
      label: t.kpi.biomass,
      value: `${result.biomassKg.toFixed(1)} kg`,
      sub: `${result.stockingDensity.toFixed(2)} kg/m³`,
    },
    {
      key: 'waste',
      icon: Leaf,
      label: t.kpi.waste,
      value: fmtKg(result.savedKg),
      sub: fmt(t.kpi.wasteSub, { pct: result.savedPct.toFixed(0) }),
    },
    {
      key: 'nitrogen',
      icon: Waves,
      label: t.kpi.nitrogen,
      value: `${(result.nitrogenOptKg * 1000).toFixed(0)} g`,
      sub: fmt(t.kpi.nitrogenSub, { pct: pollutionCut.toFixed(0) }),
    },
  ]

  return (
    <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {items.map(({ key, icon: Icon, label, value, sub, emphasis }) => (
        <li
          key={key}
          className={`flex flex-col gap-2 rounded-xl border p-4 ${
            emphasis ? 'border-transparent bg-gradient-to-br from-primary to-accent text-primary-foreground shadow-lg shadow-primary/25' : 'glass'
          }`}
        >
          <div className="flex items-center gap-2">
            <Icon className={`size-4 ${emphasis ? '' : 'text-primary'}`} aria-hidden="true" />
            <span className={`text-xs font-medium ${emphasis ? 'opacity-90' : 'text-muted-foreground'}`}>{label}</span>
          </div>
          <span className="font-mono text-2xl font-semibold tabular-nums">{value}</span>
          <span className={`text-xs ${emphasis ? 'opacity-85' : 'text-muted-foreground'}`}>{sub}</span>
        </li>
      ))}
    </ul>
  )
}
