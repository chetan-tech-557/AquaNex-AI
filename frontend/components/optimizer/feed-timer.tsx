'use client'

import { useEffect, useRef, useState } from 'react'
import { Bell, BellRing, ChevronDown, ChevronUp, Timer, X } from 'lucide-react'
import { findNextMeal, type Meal } from '@/lib/feeding'
import { useNow } from '@/lib/use-now'
import { fmt, useI18n } from '@/lib/i18n'

const fmtGrams = (g: number) => (g >= 1000 ? `${(g / 1000).toFixed(2)} kg` : `${g.toFixed(0)} g`)

function formatCountdown(ms: number) {
  const total = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  return [h, m, s].map((v) => String(v).padStart(2, '0')).join(':')
}

function playChime() {
  try {
    const ctx = new AudioContext()
    ;[880, 1320].forEach((freq, i) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.frequency.value = freq
      osc.connect(gain)
      gain.connect(ctx.destination)
      const t = ctx.currentTime + i * 0.25
      gain.gain.setValueAtTime(0.0001, t)
      gain.gain.exponentialRampToValueAtTime(0.25, t + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.6)
      osc.start(t)
      osc.stop(t + 0.65)
    })
  } catch {
    // Audio can be blocked until the user interacts with the page.
  }
}

interface FeedTimerProps {
  meals: Meal[]
  suspended: boolean
}

export function FeedTimer({ meals, suspended }: FeedTimerProps) {
  const { t } = useI18n()
  const now = useNow()
  const [open, setOpen] = useState(true)
  const [toast, setToast] = useState<string | null>(null)
  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>('default')
  const lastTargetRef = useRef<number | null>(null)

  const next = now === null ? null : findNextMeal(meals, new Date(now))
  const target = next?.date.getTime() ?? null

  const notify = (message: string) => {
    setToast(message)
    playChime()
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      new Notification(t.timer.notifTitle, { body: message, icon: '/images/aquanex-logo.png' })
    }
  }

  useEffect(() => {
    if (now === null) return
    const previous = lastTargetRef.current
    if (previous !== null && target !== previous && now >= previous) {
      const due = meals.find((m) => Math.abs(m.hour - (new Date(previous).getHours() + new Date(previous).getMinutes() / 60)) < 0.02)
      notify(due ? fmt(t.timer.dueMsg, { g: fmtGrams(due.grams), t: due.time }) : t.timer.reached)
    }
    lastTargetRef.current = target
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [now, target])

  useEffect(() => {
    if (!toast) return
    const id = setTimeout(() => setToast(null), 12000)
    return () => clearTimeout(id)
  }, [toast])

  const requestPermission = async () => {
    if (typeof Notification === 'undefined') {
      setPermission('unsupported')
      return
    }
    setPermission(await Notification.requestPermission())
  }

  const remaining = next && now !== null ? next.date.getTime() - now : 0
  const span = next ? next.date.getTime() - next.previous.getTime() : 1
  const progress = next ? 1 - remaining / span : 0
  const R = 34
  const C = 2 * Math.PI * R

  return (
    <>
      <aside
        aria-label={t.timer.aria}
        className="glass fixed right-3 top-[4.75rem] z-40 w-[17.5rem] animate-fade-up rounded-2xl md:right-6"
      >
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          className="flex w-full items-center justify-between gap-2 px-4 py-3 text-sm font-semibold"
        >
          <span className="flex items-center gap-2">
            <Timer className="size-4 text-accent" aria-hidden="true" />
            {t.timer.next}
            {!open && next && (
              <span className="font-mono text-xs font-medium text-primary tabular-nums">
                {formatCountdown(remaining)}
              </span>
            )}
          </span>
          {open ? (
            <ChevronUp className="size-4" aria-hidden="true" />
          ) : (
            <ChevronDown className="size-4" aria-hidden="true" />
          )}
        </button>

        {open && (
          <div className="flex flex-col gap-4 border-t border-white/10 px-4 pb-4 pt-4">
            {suspended || meals.length === 0 ? (
              <p className="text-sm text-destructive">{t.timer.suspended}</p>
            ) : (
              <>
                <div className="flex items-center gap-4">
                  <div className="relative size-20 shrink-0">
                    <svg viewBox="0 0 80 80" className="size-20 -rotate-90" aria-hidden="true">
                      <defs>
                        <linearGradient id="timer-grad" x1="0" y1="0" x2="1" y2="1">
                          <stop offset="0%" stopColor="var(--primary)" />
                          <stop offset="100%" stopColor="var(--accent)" />
                        </linearGradient>
                      </defs>
                      <circle cx="40" cy="40" r={R} fill="none" stroke="oklch(1 0 0 / 0.1)" strokeWidth="6" />
                      <circle
                        cx="40"
                        cy="40"
                        r={R}
                        fill="none"
                        stroke="url(#timer-grad)"
                        strokeWidth="6"
                        strokeLinecap="round"
                        strokeDasharray={C}
                        strokeDashoffset={C * (1 - Math.min(1, Math.max(0, progress)))}
                        className="transition-[stroke-dashoffset] duration-1000 ease-linear"
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center font-mono text-sm font-bold">
                      {next ? next.meal.time : '--:--'}
                    </span>
                  </div>
                  <div className="flex min-w-0 flex-col gap-0.5">
                    <span className="text-xs text-muted-foreground">{t.timer.timeLeft}</span>
                    <span className="font-mono text-2xl font-bold tabular-nums" aria-live="off">
                      {next ? formatCountdown(remaining) : '--:--:--'}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {next ? `${fmt(t.timer.meal, { n: next.index + 1 })} · ${fmtGrams(next.meal.grams)}` : t.timer.loading}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  {permission === 'granted' ? (
                    <span className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-success/15 px-2 py-2 text-xs font-medium text-success">
                      <BellRing className="size-3.5" aria-hidden="true" />
                      {t.timer.alertsOn}
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={requestPermission}
                      className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-primary/15 px-2 py-2 text-xs font-medium text-primary transition-colors hover:bg-primary/25"
                    >
                      <Bell className="size-3.5" aria-hidden="true" />
                      {permission === 'denied' || permission === 'unsupported' ? t.timer.inAppOnly : t.timer.enable}
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => next && notify(fmt(t.timer.testMsg, { g: fmtGrams(next.meal.grams), t: next.meal.time }))}
                    className="rounded-lg border border-white/10 px-3 py-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground"
                  >
                    {t.timer.test}
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </aside>

      {toast && (
        <div
          role="alert"
          className="fixed bottom-6 left-1/2 z-50 flex w-[min(92vw,26rem)] -translate-x-1/2 animate-fade-up items-start gap-3 rounded-2xl border border-accent/50 bg-[oklch(0.22_0.06_200/0.95)] p-4 shadow-2xl shadow-accent/20 backdrop-blur-xl"
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
            <BellRing className="size-4" aria-hidden="true" />
          </span>
          <div className="flex flex-1 flex-col gap-0.5">
            <p className="text-sm font-semibold">{t.timer.toastTitle}</p>
            <p className="text-sm text-muted-foreground">{toast}</p>
          </div>
          <button
            type="button"
            onClick={() => setToast(null)}
            aria-label={t.timer.dismiss}
            className="rounded-md p-1 text-muted-foreground hover:bg-white/10 hover:text-foreground"
          >
            <X className="size-4" aria-hidden="true" />
          </button>
        </div>
      )}
    </>
  )
}
