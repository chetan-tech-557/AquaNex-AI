import { SiteHeader } from '@/components/site-header'
import { Hero } from '@/components/hero'
import { Optimizer } from '@/components/optimizer/optimizer'
import { ImpactSection } from '@/components/impact-section'
import { OceanBackground } from '@/components/ocean-background'
import { LanguagePicker } from '@/components/language-picker'
import { LanguageProvider } from '@/lib/i18n'

export default function Page() {
  return (
    <LanguageProvider>
      <OceanBackground />
      <SiteHeader />
      <main>
        <Hero />
        <Optimizer />
        <ImpactSection />
      </main>
      <LanguagePicker />
    </LanguageProvider>
  )
}
