'use client'

import type { FeedingResult } from '@/lib/feeding'
import { fmt, useI18n } from '@/lib/i18n'

export function ProjectionChart({ result }: { result: FeedingResult }) {
  const { t } = useI18n()
  const max = Math.max(...result.projection.map((d) => d.feedKg), 0.0001)
  const totalFeed = result.projection.reduce((a, d) => a + d.feedKg, 0)
  const last = result.projection[result.projection.length - 1]

  return (
    <section aria-labelledby="projection-heading" className="flex flex-col gap-4 glass rounded-2xl p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 id="projection-heading" className="font-semibold">
          {t.chart.title}
        </h3>
        <span className="text-xs text-muted-foreground">
          {t.chart.total} <span className="font-mono font-medium text-foreground">{totalFeed.toFixed(2)} kg</span>
        </span>
      </div>
      <div className="flex h-40 items-end gap-2" role="img" aria-label={t.chart.aria}>
        {result.projection.map((d) => (
          <div key={d.day} className="flex h-full flex-1 flex-col items-center justify-end gap-1.5">
            <span className="font-mono text-[10px] tabular-nums text-muted-foreground">{d.feedKg.toFixed(1)}</span>
            <div className="flex w-full flex-1 items-end">
              <div
                className="w-full rounded-t-md bg-primary/80 transition-[height]"
                style={{ height: `${Math.max(2, (d.feedKg / max) * 100)}%` }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{fmt(t.chart.day, { n: d.day })}</span>
          </div>
        ))}
      </div>
      <p className="text-xs leading-relaxed text-muted-foreground">
        {t.chart.note} <span className="font-mono font-medium text-foreground">{last.avgWeight.toFixed(1)} g</span>.{' '}
        {t.chart.note2}
      </p>
    </section>
  )
}
