'use client'

import { createContext, useCallback, useContext, useEffect, useSyncExternalStore } from 'react'
import type { SpeciesId, StageId } from '@/lib/feeding'
import { en, type Dict } from './en'
import { hi } from './hi'
import { mr } from './mr'

export type Lang = 'en' | 'hi' | 'mr'

export const LANGUAGES: { id: Lang; native: string; english: string }[] = [
  { id: 'en', native: 'English', english: 'English' },
  { id: 'hi', native: 'हिंदी', english: 'Hindi' },
  { id: 'mr', native: 'मराठी', english: 'Marathi' },
]

const DICTS: Record<Lang, Dict> = { en, hi, mr }
const STORAGE_KEY = 'aquanex-lang'
const SERVER_SNAPSHOT = 'ssr'
const listeners = new Set<() => void>()

function isLang(v: string | null): v is Lang {
  return v === 'en' || v === 'hi' || v === 'mr'
}

function subscribe(cb: () => void) {
  listeners.add(cb)
  window.addEventListener('storage', cb)
  return () => {
    listeners.delete(cb)
    window.removeEventListener('storage', cb)
  }
}

function getSnapshot() {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

/** Replaces `{name}` placeholders with values from `params`. */
export function fmt(template: string, params: Record<string, string | number> = {}) {
  return template.replace(/\{(\w+)\}/g, (_, k: string) => (k in params ? String(params[k]) : `{${k}}`))
}

export function stageLabel(t: Dict, species: SpeciesId, stage: StageId) {
  if (species === 'shrimp' && stage === 'fry') return t.stages.postlarvae
  if (species === 'shrimp' && stage === 'fingerling') return t.stages.nursery
  return t.stages[stage]
}

interface LanguageContextValue {
  lang: Lang
  t: Dict
  setLang: (lang: Lang) => void
  needsChoice: boolean
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const stored = useSyncExternalStore(subscribe, getSnapshot, () => SERVER_SNAPSHOT)
  const lang: Lang = isLang(stored) ? stored : 'en'
  const needsChoice = stored === null

  const setLang = useCallback((next: Lang) => {
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // Storage can be unavailable (private mode); the choice still applies via listeners below.
    }
    listeners.forEach((l) => l())
  }, [])

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  return (
    <LanguageContext.Provider value={{ lang, t: DICTS[lang], setLang, needsChoice }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useI18n() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useI18n must be used within LanguageProvider')
  return ctx
}
