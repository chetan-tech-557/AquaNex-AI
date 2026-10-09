'use client'

import { AlertOctagon, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import type { Alert } from '@/lib/feeding'
import { fmt, stageLabel, useI18n } from '@/lib/i18n'
import type { Dict } from '@/lib/i18n/en'

const styles = {
  critical: { icon: AlertOctagon, cls: 'border-destructive/30 bg-destructive/10 text-destructive' },
  warning: { icon: AlertTriangle, cls: 'border-warning/50 bg-warning/15 text-warning-foreground' },
  info: { icon: Info, cls: 'border-primary/20 bg-secondary text-secondary-foreground' },
}

function translateAlert(t: Dict, { id, params }: Alert) {
  const values: Record<string, string | number> = {}
  for (const [k, v] of Object.entries(params)) {
    if (typeof v === 'string' || typeof v === 'number') values[k] = v
  }
  if (params.species) values.species = t.species[params.species]
  if (params.species && params.stage) values.stage = stageLabel(t, params.species, params.stage)
  if (params.species && params.better) values.better = stageLabel(t, params.species, params.better)
  if (params.season) {
    values.season = t.seasons[params.season].label
    values.note = t.seasons[params.season].note
  }

  const entry = t.alerts[id]
  let detail = fmt(entry.detail, values)
  if (id === 'weight' && params.better) detail += fmt(t.alerts.weightBetter, values)
  if (params.toxic) detail += t.alerts.phToxic
  return { title: fmt(entry.title, values), detail }
}

export function AlertsList({ alerts }: { alerts: Alert[] }) {
  const { t } = useI18n()

  return (
    <section aria-labelledby="alerts-heading" aria-live="polite" className="flex flex-col gap-3">
      <h3 id="alerts-heading" className="sr-only">
        {t.alerts.heading}
      </h3>
      {alerts.map((a) => {
        const Icon = a.id === 'optimal' ? CheckCircle2 : styles[a.level].icon
        const { title, detail } = translateAlert(t, a)
        return (
          <div key={a.id} className={`flex gap-3 rounded-xl border p-4 ${styles[a.level].cls}`}>
            <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <div className="flex flex-col gap-0.5">
              <p className="text-sm font-semibold">{title}</p>
              <p className="text-sm leading-relaxed opacity-90">{detail}</p>
            </div>
          </div>
        )
      })}
    </section>
  )
}
