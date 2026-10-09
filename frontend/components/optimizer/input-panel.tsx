'use client'

import { useId } from 'react'
import { CloudRain, Flower2, Leaf, Snowflake, Sun } from 'lucide-react'
import {
  SEASONS,
  SPECIES,
  STAGE_ORDER,
  formatHour,
  type FeedingInput,
  type SeasonId,
  type SpeciesId,
  type StageId,
} from '@/lib/feeding'
import { fmt, stageLabel, useI18n } from '@/lib/i18n'

const SEASON_ICONS: Record<SeasonId, typeof Sun> = {
  spring: Flower2,
  summer: Sun,
  monsoon: CloudRain,
  autumn: Leaf,
  winter: Snowflake,
}

interface InputPanelProps {
  value: FeedingInput
  onChange: (next: FeedingInput) => void
}

const fieldClass =
  'h-10 w-full rounded-lg border border-input bg-white/5 px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring'

function SliderField({
  label,
  unit,
  min,
  max,
  step,
  value,
  onChange,
  hint,
}: {
  label: string
  unit: string
  min: number
  max: number
  step: number
  value: number
  onChange: (v: number) => void
  hint?: string
}) {
  const id = useId()
  const { t } = useI18n()
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between gap-2">
        <label htmlFor={id} className="text-sm font-medium">
          {label}
        </label>
        <div className="flex items-baseline gap-1">
          <input
            type="number"
            aria-label={`${label} ${t.input.value}`}
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            className="h-8 w-20 rounded-md border border-input bg-white/5 px-2 text-right font-mono text-sm tabular-nums outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          <span className="w-10 text-xs text-muted-foreground">{unit}</span>
        </div>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

function NumberField({
  label,
  unit,
  value,
  min,
  step,
  onChange,
}: {
  label: string
  unit: string
  value: number
  min: number
  step: number
  onChange: (v: number) => void
}) {
  const id = useId()
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium">
        {label} <span className="font-normal text-muted-foreground">({unit})</span>
      </label>
      <input
        id={id}
        type="number"
        min={min}
        step={step}
        value={value}
        onChange={(e) => onChange(Math.max(min, Number(e.target.value)))}
        className={`${fieldClass} font-mono tabular-nums`}
      />
    </div>
  )
}

export function InputPanel({ value, onChange }: InputPanelProps) {
  const { t } = useI18n()
  const speciesId = useId()
  const stageId = useId()
  const species = SPECIES[value.species]
  const set = <K extends keyof FeedingInput>(key: K, v: FeedingInput[K]) => onChange({ ...value, [key]: v })

  const handleStage = (stage: StageId) => {
    const [a, b] = species.stages[stage].weightRange
    const mid = Number(Math.sqrt(a * b).toFixed(a < 1 ? 2 : 0))
    onChange({ ...value, stage, avgWeight: mid })
  }

  const handleSpecies = (id: SpeciesId) => {
    const [a, b] = SPECIES[id].stages[value.stage].weightRange
    const mid = Number(Math.sqrt(a * b).toFixed(a < 1 ? 2 : 0))
    const [, optLo, optHi] = SPECIES[id].temp
    onChange({
      ...value,
      species: id,
      avgWeight: mid,
      temperature: Math.round((optLo + optHi) / 2),
      oxygen: SPECIES[id].doOptimal + 1,
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <fieldset className="flex flex-col gap-4">
        <legend className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
          {t.input.stock}
        </legend>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <label htmlFor={speciesId} className="text-sm font-medium">
              {t.input.species}
            </label>
            <select
              id={speciesId}
              value={value.species}
              onChange={(e) => handleSpecies(e.target.value as SpeciesId)}
              className={fieldClass}
            >
              {Object.values(SPECIES).map((s) => (
                <option key={s.id} value={s.id}>
                  {t.species[s.id]}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label htmlFor={stageId} className="text-sm font-medium">
              {t.input.stage}
            </label>
            <select
              id={stageId}
              value={value.stage}
              onChange={(e) => handleStage(e.target.value as StageId)}
              className={fieldClass}
            >
              {STAGE_ORDER.map((s) => (
                <option key={s} value={s}>
                  {stageLabel(t, value.species, s)} ({species.stages[s].weightRange[0]}–{species.stages[s].weightRange[1]} g)
                </option>
              ))}
            </select>
          </div>
          <NumberField
            label={t.input.stockCount}
            unit={t.input.pcs}
            min={0}
            step={100}
            value={value.stockCount}
            onChange={(v) => set('stockCount', v)}
          />
          <NumberField
            label={t.input.avgWeight}
            unit="g"
            min={0}
            step={0.1}
            value={value.avgWeight}
            onChange={(v) => set('avgWeight', v)}
          />
          <NumberField
            label={t.input.survival}
            unit="%"
            min={0}
            step={1}
            value={value.survival}
            onChange={(v) => set('survival', Math.min(100, v))}
          />
          <NumberField
            label={t.input.volume}
            unit="m³"
            min={1}
            step={10}
            value={value.pondVolume}
            onChange={(v) => set('pondVolume', v)}
          />
        </div>
      </fieldset>

      <fieldset className="flex flex-col gap-5">
        <legend className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
          {t.input.water}
        </legend>
        <SliderField
          label={t.input.temp}
          unit="°C"
          min={0}
          max={40}
          step={0.5}
          value={value.temperature}
          onChange={(v) => set('temperature', v)}
          hint={fmt(t.input.tempHint, { species: t.species[value.species], lo: species.temp[1], hi: species.temp[2] })}
        />
        <SliderField
          label={t.input.oxygen}
          unit="mg/L"
          min={0}
          max={14}
          step={0.1}
          value={value.oxygen}
          onChange={(v) => set('oxygen', v)}
          hint={fmt(t.input.doHint, { critical: species.doCritical, optimal: species.doOptimal })}
        />
        <SliderField
          label={t.input.tan}
          unit="mg/L"
          min={0}
          max={5}
          step={0.1}
          value={value.ammonia}
          onChange={(v) => set('ammonia', v)}
          hint={t.input.tanHint}
        />
        <SliderField
          label={t.input.ph}
          unit="pH"
          min={4}
          max={11}
          step={0.1}
          value={value.ph}
          onChange={(v) => set('ph', v)}
          hint={t.input.phHint}
        />
      </fieldset>

      <fieldset className="flex flex-col gap-3">
        <legend className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">{t.input.season}</legend>
        <div role="radiogroup" aria-label={t.input.season} className="grid grid-cols-3 gap-2 sm:grid-cols-5 lg:grid-cols-3">
          {Object.values(SEASONS).map((s) => {
            const Icon = SEASON_ICONS[s.id]
            const active = value.season === s.id
            return (
              <button
                key={s.id}
                type="button"
                role="radio"
                aria-checked={active}
                onClick={() => set('season', s.id)}
                className={`flex flex-col items-center gap-1 rounded-xl border px-2 py-2.5 text-xs font-medium transition-all ${
                  active
                    ? 'border-primary/60 bg-primary/20 text-foreground shadow-md shadow-primary/20'
                    : 'border-white/10 bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-foreground'
                }`}
              >
                <Icon className={`size-4 ${active ? 'text-primary' : ''}`} aria-hidden="true" />
                {t.seasons[s.id].label}
              </button>
            )
          })}
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          {t.seasons[value.season].note}{' '}
          {fmt(t.input.window, {
            start: formatHour(SEASONS[value.season].window[0]),
            end: formatHour(SEASONS[value.season].window[1]),
          })}
        </p>
      </fieldset>
    </div>
  )
}
