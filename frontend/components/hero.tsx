'use client'

import Image from 'next/image'
import { CloudSun, Droplets, FlaskConical, Sprout, Thermometer } from 'lucide-react'
import { useI18n } from '@/lib/i18n'

const icons = [Thermometer, Droplets, FlaskConical, Sprout, CloudSun]

export function Hero() {
  const { t } = useI18n()

  return (
    <section className="relative">
      <div className="mx-auto grid max-w-7xl gap-12 px-4 py-14 md:px-6 lg:grid-cols-[1.15fr_1fr] lg:items-center lg:py-24">
        <div className="flex animate-fade-up flex-col gap-6">
          <p className="glass w-fit rounded-full px-3 py-1 text-xs font-medium text-primary">{t.hero.badge}</p>
          <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight md:text-6xl">
            <span className="text-gradient">{t.hero.taglineGrow}</span> {t.hero.taglineRest}
          </h1>
          <p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">{t.hero.intro}</p>
          <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {t.hero.inputs.map(({ label, detail }, i) => {
              const Icon = icons[i]
              return (
                <li
                  key={i}
                  className="glass flex animate-fade-up flex-col gap-2 rounded-xl p-3 transition-transform hover:-translate-y-1"
                  style={{ animationDelay: `${0.1 + i * 0.08}s` }}
                >
                  <Icon className="size-5 text-accent" aria-hidden="true" />
                  <span className="text-sm font-medium leading-tight">{label}</span>
                  <span className="text-xs leading-snug text-muted-foreground">{detail}</span>
                </li>
              )
            })}
          </ul>
          <div className="flex flex-wrap gap-3">
            <a
              href="#optimizer"
              className="rounded-full bg-gradient-to-r from-primary to-accent px-6 py-3 font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-transform hover:scale-105"
            >
              {t.hero.start}
            </a>
            <a
              href="#impact"
              className="glass rounded-full px-6 py-3 font-medium transition-colors hover:bg-white/10"
            >
              {t.hero.why}
            </a>
          </div>
        </div>
        <div className="relative mx-auto w-full max-w-md animate-fade-up" style={{ animationDelay: '0.2s' }}>
          <div className="absolute inset-6 rounded-full bg-gradient-to-tr from-primary/40 to-accent/30 blur-3xl" />
          <div className="relative animate-float-slow overflow-hidden rounded-3xl ring-1 ring-white/15 shadow-2xl shadow-primary/20">
            <Image
              src="/images/aquanex-logo.png"
              alt={t.hero.logoAlt}
              width={1254}
              height={1254}
              priority
              sizes="(min-width: 1024px) 28rem, 90vw"
              className="h-auto w-full"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
