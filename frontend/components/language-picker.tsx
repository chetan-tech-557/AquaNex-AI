'use client'

import Image from 'next/image'
import { useEffect, useRef } from 'react'
import { Languages } from 'lucide-react'
import { LANGUAGES, useI18n } from '@/lib/i18n'

export function LanguagePicker() {
  const { needsChoice, setLang } = useI18n()
  const firstButton = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (needsChoice) firstButton.current?.focus()
  }, [needsChoice])

  if (!needsChoice) return null

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-[oklch(0.12_0.04_240/0.75)] p-4 backdrop-blur-md">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="language-picker-title"
        className="glass flex w-full max-w-md animate-fade-up flex-col items-center gap-6 rounded-3xl p-6 text-center md:p-8"
      >
        <Image
          src="/images/aquanex-logo.png"
          alt=""
          width={72}
          height={72}
          className="size-16 rounded-2xl ring-1 ring-white/15"
        />
        <div className="flex flex-col gap-1.5">
          <h2 id="language-picker-title" className="flex items-center justify-center gap-2 text-xl font-bold">
            <Languages className="size-5 text-accent" aria-hidden="true" />
            Choose your language
          </h2>
          <p className="text-sm text-muted-foreground">
            <span lang="hi">अपनी भाषा चुनें</span>
            {' · '}
            <span lang="mr">तुमची भाषा निवडा</span>
          </p>
        </div>
        <ul className="flex w-full flex-col gap-3">
          {LANGUAGES.map((l, i) => (
            <li key={l.id}>
              <button
                ref={i === 0 ? firstButton : undefined}
                type="button"
                lang={l.id}
                onClick={() => setLang(l.id)}
                className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-left transition-all hover:-translate-y-0.5 hover:border-primary/60 hover:bg-primary/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span className="text-lg font-semibold">{l.native}</span>
                <span className="text-sm text-muted-foreground">{l.english}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
