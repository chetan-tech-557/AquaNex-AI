'use client'

import type { FeedingResult } from '@/lib/feeding'
import { useI18n } from '@/lib/i18n'

function tone(v: number) {
  if (v >= 0.85) return 'bg-success'
  if (v >= 0.5) return 'bg-warning'
  return 'bg-destructive'
}

export function FactorBars({ result }: { result: FeedingResult }) {
  const { t } = useI18n()
  const factors = [
    { key: 'temp', label: t.factors.temp, value: result.tempFactor },
    { key: 'oxygen', label: t.factors.oxygen, value: result.oxygenFactor },
    { key: 'ammonia', label: t.factors.ammonia, value: result.ammoniaFactor },
  ]

  return (
    <section aria-labelledby="factors-heading" className="flex flex-col gap-4 glass rounded-2xl p-5">
      <div className="flex items-baseline justify-between">
        <h3 id="factors-heading" className="font-semibold">
          {t.factors.appetite}
        </h3>
        <span className="font-mono text-2xl font-semibold tabular-nums">{(result.appetiteIndex * 100).toFixed(0)}%</span>
      </div>
      <ul className="flex flex-col gap-3">
        {factors.map((f) => (
          <li key={f.key} className="flex flex-col gap-1.5">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{f.label}</span>
              <span className="font-mono tabular-nums">{f.value.toFixed(2)}</span>
            </div>
            <div
              className="h-2 overflow-hidden rounded-full bg-muted"
              role="progressbar"
              aria-label={f.label}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(f.value * 100)}
            >
              <div className={`h-full rounded-full transition-all ${tone(f.value)}`} style={{ width: `${f.value * 100}%` }} />
            </div>
          </li>
        ))}
      </ul>
      <dl className="grid grid-cols-3 gap-2 border-t pt-4 text-center">
        <div>
          <dt className="text-xs text-muted-foreground">{t.factors.protein}</dt>
          <dd className="font-mono text-sm font-medium">{result.protein}%</dd>
        </div>
        <div>
          <dt className="text-xs text-muted-foreground">{t.factors.pellet}</dt>
          <dd className="font-mono text-sm font-medium">{result.pelletMm} mm</dd>
        </div>
        <div>
          <dt className="text-xs text-muted-foreground">{t.factors.fcr}</dt>
          <dd className="font-mono text-sm font-medium">{result.fcr.toFixed(1)}</dd>
        </div>
      </dl>
    </section>
  )
}
