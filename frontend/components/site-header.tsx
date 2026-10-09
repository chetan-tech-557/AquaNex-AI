'use client'

import Image from 'next/image'
import { Globe } from 'lucide-react'
import { LANGUAGES, useI18n, type Lang } from '@/lib/i18n'

export function SiteHeader() {
  const { t, lang, setLang } = useI18n()
  const links = [
    { href: '#optimizer', label: t.header.optimizer },
    { href: '#impact', label: t.header.impact },
    { href: '#contact', label: t.header.helpline },
  ]

  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-[oklch(0.17_0.05_240/0.6)] backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-2 px-4 md:px-6">
        <a href="#" className="flex shrink-0 items-center gap-2.5 font-semibold tracking-tight">
          <Image
            src="/images/aquanex-logo.png"
            alt=""
            width={40}
            height={40}
            className="size-10 rounded-xl ring-1 ring-white/15"
          />
          <span className="hidden text-lg min-[400px]:inline">
            AquaNex <span className="text-gradient">AI</span>
          </span>
        </a>
        <nav aria-label="Main" className="flex items-center gap-1 text-sm">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="hidden rounded-md px-3 py-2 text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground lg:inline-block"
            >
              {l.label}
            </a>
          ))}
          <label className="glass relative flex items-center gap-1.5 rounded-full py-1.5 pl-3 pr-2">
            <Globe className="size-4 text-accent" aria-hidden="true" />
            <span className="sr-only">{t.header.language}</span>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value as Lang)}
              className="cursor-pointer appearance-none bg-transparent pr-1 text-sm font-medium outline-none"
            >
              {LANGUAGES.map((l) => (
                <option key={l.id} value={l.id} lang={l.id} className="bg-background text-foreground">
                  {l.native}
                </option>
              ))}
            </select>
          </label>
          <a
            href="#optimizer"
            className="ml-1 hidden rounded-full bg-gradient-to-r from-primary to-accent px-4 py-2 font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition-transform hover:scale-105 sm:inline-block"
          >
            {t.header.cta}
          </a>
        </nav>
      </div>
    </header>
  )
}
