'use client'

import Image from 'next/image'
import { Clock, Mail, MapPin, Phone } from 'lucide-react'
import { useI18n } from '@/lib/i18n'

export function ImpactSection() {
  const { t } = useI18n()

  return (
    <>
      <section id="impact" aria-labelledby="impact-heading" className="scroll-mt-20">
        <div className="mx-auto max-w-7xl px-4 py-16 md:px-6">
          <div className="glass grid gap-10 rounded-3xl p-8 md:p-10 lg:grid-cols-[1fr_2fr] lg:items-center">
            <div className="flex flex-col gap-3">
              <h2 id="impact-heading" className="text-3xl font-bold tracking-tight">
                {t.impact.titleA}
                <span className="text-gradient">{t.impact.titleB}</span>
                {t.impact.titleC}
              </h2>
              <p className="leading-relaxed text-muted-foreground">{t.impact.body}</p>
            </div>
            <ul className="grid gap-4 sm:grid-cols-3">
              {t.impact.stats.map((s, i) => (
                <li
                  key={i}
                  className="flex flex-col gap-2 rounded-2xl border border-white/10 bg-white/5 p-5 transition-transform hover:-translate-y-1"
                >
                  <span className="text-gradient font-mono text-3xl font-bold">{s.value}</span>
                  <span className="text-sm leading-relaxed text-muted-foreground">{s.label}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <footer id="contact" className="scroll-mt-20 border-t border-white/10 bg-[oklch(0.13_0.045_240/0.85)] backdrop-blur-xl">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 md:grid-cols-[1.2fr_1fr] md:px-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <Image
                src="/images/aquanex-logo.png"
                alt=""
                width={48}
                height={48}
                className="size-12 rounded-xl ring-1 ring-white/15"
              />
              <span className="text-xl font-semibold">
                AquaNex <span className="text-gradient">AI</span>
              </span>
            </div>
            <p className="font-medium">
              {t.hero.taglineGrow} {t.hero.taglineRest}
            </p>
            <p className="max-w-md text-sm leading-relaxed text-muted-foreground">{t.footer.disclaimer}</p>
          </div>

          <div className="flex flex-col gap-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-primary">{t.footer.helpline}</h2>
            <ul className="flex flex-col gap-3 text-sm">
              <li>
                <a
                  href="tel:+918001234567"
                  className="glass flex items-center gap-3 rounded-xl p-3 transition-colors hover:bg-white/10"
                >
                  <span className="flex size-9 items-center justify-center rounded-lg bg-primary/15 text-primary">
                    <Phone className="size-4" aria-hidden="true" />
                  </span>
                  <span className="flex flex-col">
                    <span className="text-xs text-muted-foreground">{t.footer.tollfree}</span>
                    <span className="font-mono font-semibold">1800-123-4567</span>
                  </span>
                </a>
              </li>
              <li>
                <a
                  href="mailto:support@aquanexai.com"
                  className="glass flex items-center gap-3 rounded-xl p-3 transition-colors hover:bg-white/10"
                >
                  <span className="flex size-9 items-center justify-center rounded-lg bg-accent/15 text-accent">
                    <Mail className="size-4" aria-hidden="true" />
                  </span>
                  <span className="flex flex-col">
                    <span className="text-xs text-muted-foreground">{t.footer.email}</span>
                    <span className="font-semibold">support@aquanexai.com</span>
                  </span>
                </a>
              </li>
            </ul>
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Clock className="size-3.5" aria-hidden="true" />
                {t.footer.hours}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="size-3.5" aria-hidden="true" />
                {t.footer.regions}
              </span>
            </div>
          </div>
        </div>
        <div className="border-t border-white/10 py-4 text-center text-xs text-muted-foreground">
          {t.footer.copyright}
        </div>
      </footer>
    </>
  )
}
