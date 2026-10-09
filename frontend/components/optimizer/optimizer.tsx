'use client'

import { useEffect, useState } from 'react'
import { RotateCcw, Loader2 } from 'lucide-react'
import { calculateFeeding, type FeedingInput, type FeedingResult } from '@/lib/feeding'
import { getRecommendation, type BackendRecommendation } from '@/lib/api/aquanex'
import { InputPanel } from './input-panel'
import { KpiCards } from './kpi-cards'
import { FactorBars } from './factor-bars'
import { ScheduleTable } from './schedule-table'
import { ProjectionChart } from './projection-chart'
import { AlertsList } from './alerts-list'
import { FeedTimer } from './feed-timer'
import { AiDiagnostics } from './ai-diagnostics'
import { useI18n } from '@/lib/i18n'

const DEFAULT_INPUT: FeedingInput = {
  species: 'tilapia',
  stage: 'juvenile',
  stockCount: 10000,
  avgWeight: 45,
  survival: 92,
  temperature: 24,
  oxygen: 4.2,
  ammonia: 0.6,
  pondVolume: 800,
  ph: 7.4,
  season: 'summer',
}

const PRESETS: { id: 'ideal' | 'cold' | 'monsoon' | 'hypoxia'; patch: Partial<FeedingInput> }[] = [
  { id: 'ideal', patch: { temperature: 28, oxygen: 6.5, ammonia: 0.3, ph: 7.5, season: 'spring' } },
  { id: 'cold', patch: { temperature: 19, oxygen: 7, ammonia: 0.4, ph: 7.2, season: 'winter' } },
  { id: 'monsoon', patch: { temperature: 26, oxygen: 4, ammonia: 1.2, ph: 6.2, season: 'monsoon' } },
  { id: 'hypoxia', patch: { temperature: 31, oxygen: 2.2, ammonia: 1.4, ph: 8.8, season: 'summer' } },
]

export function Optimizer() {
  const { t } = useI18n()
  const [input, setInput] = useState<FeedingInput>(DEFAULT_INPUT)
  const [result, setResult] = useState<FeedingResult>(() => calculateFeeding(DEFAULT_INPUT))
  const [backendData, setBackendData] = useState<BackendRecommendation | undefined>(undefined)
  const [isLiveBackend, setIsLiveBackend] = useState<boolean>(false)
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false)

  useEffect(() => {
    let cancelled = false
    setIsAnalyzing(true)

    const timer = setTimeout(async () => {
      try {
        const response = await getRecommendation(input)
        if (!cancelled) {
          setResult(response.feedingResult)
          setBackendData(response.backendRecommendation)
          setIsLiveBackend(response.isLiveBackend)
        }
      } catch {
        if (!cancelled) {
          setResult(calculateFeeding(input))
          setIsLiveBackend(false)
        }
      } finally {
        if (!cancelled) {
          setIsAnalyzing(false)
        }
      }
    }, 150)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [input])

  return (
    <section id="optimizer" aria-labelledby="optimizer-heading" className="scroll-mt-20">
      <FeedTimer meals={result.meals} suspended={result.suspended} />
      <div className="mx-auto max-w-7xl px-4 py-14 md:px-6">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3">
              <h2 id="optimizer-heading" className="text-3xl font-bold tracking-tight md:text-4xl">
                {t.optimizer.titleA}
                <span className="text-gradient">{t.optimizer.titleB}</span>
              </h2>
              {isAnalyzing && (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary animate-pulse">
                  <Loader2 className="size-3 animate-spin" />
                  ML Optimizing...
                </span>
              )}
            </div>
            <p className="max-w-2xl text-muted-foreground">{t.optimizer.intro}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-muted-foreground">{t.optimizer.scenarios}</span>
            {PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => setInput((prev) => ({ ...prev, ...p.patch }))}
                className="glass rounded-full px-3 py-1.5 text-xs font-medium transition-all hover:-translate-y-0.5 hover:bg-white/10"
              >
                {t.optimizer.presets[p.id]}
              </button>
            ))}
            <button
              type="button"
              onClick={() => setInput(DEFAULT_INPUT)}
              className="flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground"
            >
              <RotateCcw className="size-3" aria-hidden="true" />
              {t.optimizer.reset}
            </button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,380px)_minmax(0,1fr)]">
          <div className="glass h-fit rounded-2xl p-5 lg:sticky lg:top-20">
            <InputPanel value={input} onChange={setInput} />
          </div>
          <div className="flex min-w-0 flex-col gap-6">
            <KpiCards result={result} />
            <AlertsList alerts={result.alerts} />
            <AiDiagnostics backendRecommendation={backendData} isLiveBackend={isLiveBackend} />
            <ScheduleTable result={result} />
            <div className="grid gap-6 xl:grid-cols-2">
              <FactorBars result={result} />
              <ProjectionChart result={result} />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
