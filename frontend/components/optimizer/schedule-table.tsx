'use client'

import { CalendarClock, CheckCircle2, Moon, Sunrise, Sunset } from 'lucide-react'
import { findNextMeal, formatHour, type FeedingResult } from '@/lib/feeding'
import { useNow } from '@/lib/use-now'
import { fmt, useI18n } from '@/lib/i18n'

const fmtGrams = (g: number) => (g >= 1000 ? `${(g / 1000).toFixed(2)} kg` : `${g.toFixed(0)} g`)
const pct = (hour: number) => `${(hour / 24) * 100}%`

export function ScheduleTable({ result }: { result: FeedingResult }) {
  const { t } = useI18n()
  const now = useNow()
  const nowDate = now === null ? null : new Date(now)
  const next = nowDate ? findNextMeal(result.meals, nowDate) : null
  const nowHour = nowDate ? nowDate.getHours() + nowDate.getMinutes() / 60 : null
  const maxShare = Math.max(...result.meals.map((m) => m.share), 0.0001)
  const [winStart, winEnd] = result.feedingWindow

  return (
    <section aria-labelledby="schedule-heading" className="glass flex flex-col gap-6 rounded-2xl p-5 md:p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 id="schedule-heading" className="flex items-center gap-2 text-lg font-semibold">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <CalendarClock className="size-4" aria-hidden="true" />
          </span>
          {t.schedule.title}
        </h3>
        <span className="rounded-full bg-white/5 px-3 py-1 font-mono text-xs text-muted-foreground">
          {fmt(t.schedule.meals, { n: result.meals.length })} · {formatHour(winStart)}–{formatHour(winEnd)}
        </span>
      </div>

      {result.meals.length === 0 ? (
        <p className="rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {t.schedule.none}
        </p>
      ) : (
        <>
          <div className="flex flex-col gap-2">
            <div
              className="relative h-24 rounded-2xl border border-white/10"
              style={{
                background: `linear-gradient(90deg,
                  oklch(0.2 0.06 265) 0%,
                  oklch(0.22 0.06 265) ${pct(winStart - 1.5)},
                  oklch(0.55 0.12 50 / 0.6) ${pct(winStart)},
                  oklch(0.55 0.1 215 / 0.55) ${pct((winStart + winEnd) / 2)},
                  oklch(0.55 0.13 40 / 0.6) ${pct(winEnd)},
                  oklch(0.22 0.06 265) ${pct(winEnd + 1.5)},
                  oklch(0.2 0.06 265) 100%)`,
              }}
              role="img"
              aria-label={`${t.schedule.timeline}: ${result.meals.map((m) => `${m.time} ${fmtGrams(m.grams)}`).join(', ')}`}
            >
              <div
                className="absolute inset-y-2 rounded-xl border border-dashed border-accent/50 bg-accent/10"
                style={{ left: pct(winStart), width: pct(winEnd - winStart) }}
              />
              <Sunrise
                className="absolute top-2 size-4 -translate-x-1/2 text-warning"
                style={{ left: pct(winStart) }}
                aria-hidden="true"
              />
              <Sunset
                className="absolute top-2 size-4 -translate-x-1/2 text-warning"
                style={{ left: pct(winEnd) }}
                aria-hidden="true"
              />
              <Moon className="absolute left-3 top-2 size-4 text-muted-foreground" aria-hidden="true" />

              {result.meals.map((m, i) => {
                const size = 22 + (m.share / maxShare) * 26
                const isNext = next?.index === i
                return (
                  <div
                    key={m.time}
                    className="absolute top-1/2 flex -translate-x-1/2 -translate-y-1/2 items-center justify-center"
                    style={{ left: pct(m.hour) }}
                  >
                    {isNext && (
                      <span
                        className="absolute animate-ping-soft rounded-full bg-accent/60"
                        style={{ width: size, height: size }}
                      />
                    )}
                    <span
                      className={`relative flex items-center justify-center rounded-full font-mono text-[10px] font-bold text-primary-foreground shadow-lg transition-all duration-500 ${
                        isNext ? 'bg-accent shadow-accent/40' : 'bg-primary shadow-primary/30'
                      }`}
                      style={{ width: size, height: size }}
                    >
                      {i + 1}
                    </span>
                  </div>
                )
              })}

              {nowHour !== null && (
                <div className="absolute inset-y-0 w-0.5 bg-white/80" style={{ left: pct(nowHour) }}>
                  <span className="absolute -top-5 left-1/2 -translate-x-1/2 rounded bg-white px-1.5 py-0.5 text-[10px] font-semibold text-background">
                    {t.schedule.now}
                  </span>
                </div>
              )}
            </div>
            <div className="flex justify-between px-1 font-mono text-[10px] text-muted-foreground">
              {[0, 3, 6, 9, 12, 15, 18, 21, 24].map((h) => (
                <span key={h}>{String(h).padStart(2, '0')}</span>
              ))}
            </div>
          </div>

          <ol className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {result.meals.map((m, i) => {
              const isNext = next?.index === i
              const isDone = nowHour !== null && m.hour < nowHour && !isNext
              return (
                <li
                  key={m.time}
                  className={`relative flex flex-col gap-3 overflow-hidden rounded-xl border p-4 transition-all duration-300 hover:-translate-y-0.5 ${
                    isNext
                      ? 'border-accent/60 bg-accent/10 shadow-lg shadow-accent/10'
                      : 'border-white/10 bg-white/5'
                  } ${isDone ? 'opacity-60' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <span
                        className={`flex size-6 items-center justify-center rounded-full font-mono text-xs font-bold text-primary-foreground ${
                          isNext ? 'bg-accent' : 'bg-primary'
                        }`}
                      >
                        {i + 1}
                      </span>
                      <span className="font-mono text-lg font-semibold tabular-nums">{m.time}</span>
                    </span>
                    {isNext ? (
                      <span className="rounded-full bg-accent px-2 py-0.5 text-[10px] font-bold uppercase text-accent-foreground">
                        {t.schedule.next}
                      </span>
                    ) : isDone ? (
                      <CheckCircle2 className="size-4 text-success" aria-label={t.schedule.done} />
                    ) : null}
                  </div>
                  <div className="flex items-end justify-between gap-2">
                    <span className="font-mono text-2xl font-bold tabular-nums">{fmtGrams(m.grams)}</span>
                    <span className="font-mono text-xs text-muted-foreground">{fmt(t.schedule.ofDay, { pct: (m.share * 100).toFixed(0) })}</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-all duration-700"
                      style={{ width: `${(m.share / maxShare) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs leading-relaxed text-muted-foreground">{t.schedule.notes[m.note]}</p>
                </li>
              )
            })}
          </ol>
        </>
      )}
    </section>
  )
}
