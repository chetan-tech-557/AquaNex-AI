export type SpeciesId = 'tilapia' | 'trout' | 'shrimp' | 'catfish'
export type StageId = 'fry' | 'fingerling' | 'juvenile' | 'growout' | 'brood'
export type SeasonId = 'spring' | 'summer' | 'monsoon' | 'autumn' | 'winter'

export interface SeasonProfile {
  id: SeasonId
  label: string
  /** Hours (24h) between which feeding is allowed, set by day length and the dawn oxygen low */
  window: [number, number]
  factor: number
  note: string
}

export const SEASONS: Record<SeasonId, SeasonProfile> = {
  spring: { id: 'spring', label: 'Spring', window: [7, 18], factor: 1, note: 'Rising temperatures drive strong growth — feed the full ration.' },
  summer: { id: 'summer', label: 'Summer', window: [6.5, 18.5], factor: 0.95, note: 'Long days but warm water holds less oxygen — avoid heavy meals in the midday heat.' },
  monsoon: { id: 'monsoon', label: 'Monsoon / Rainy', window: [8, 17.5], factor: 0.85, note: 'Overcast skies cut photosynthesis and runoff lowers water quality — ration trimmed by 15%.' },
  autumn: { id: 'autumn', label: 'Autumn', window: [7.5, 17.5], factor: 0.95, note: 'Shortening days slow metabolism — taper rations gradually.' },
  winter: { id: 'winter', label: 'Winter', window: [9, 16.5], factor: 0.8, note: 'Short, cool days lower appetite — fewer, smaller meals in the warmest hours.' },
}

interface StageProfile {
  label: string
  weightRange: [number, number]
  /** Feeding rate as % of body weight per day at optimal conditions */
  rate: number
  meals: number
  protein: number
  fcr: number
  pelletMm: string
}

export interface SpeciesProfile {
  id: SpeciesId
  name: string
  scientific: string
  /** [lethal min, optimal min, optimal max, lethal max] in °C */
  temp: [number, number, number, number]
  /** Dissolved oxygen thresholds in mg/L */
  doCritical: number
  doOptimal: number
  stages: Record<StageId, StageProfile>
}

export const SPECIES: Record<SpeciesId, SpeciesProfile> = {
  tilapia: {
    id: 'tilapia',
    name: 'Nile Tilapia',
    scientific: 'Oreochromis niloticus',
    temp: [16, 26, 30, 36],
    doCritical: 2.5,
    doOptimal: 5,
    stages: {
      fry: { label: 'Fry', weightRange: [0.02, 1], rate: 12, meals: 6, protein: 45, fcr: 0.9, pelletMm: '0.3–0.5' },
      fingerling: { label: 'Fingerling', weightRange: [1, 10], rate: 7, meals: 5, protein: 40, fcr: 1.1, pelletMm: '0.8–1.2' },
      juvenile: { label: 'Juvenile', weightRange: [10, 100], rate: 4, meals: 4, protein: 35, fcr: 1.3, pelletMm: '2.0' },
      growout: { label: 'Grow-out', weightRange: [100, 600], rate: 2, meals: 3, protein: 30, fcr: 1.6, pelletMm: '3.0–4.0' },
      brood: { label: 'Broodstock', weightRange: [600, 2000], rate: 1, meals: 2, protein: 32, fcr: 2.0, pelletMm: '6.0' },
    },
  },
  trout: {
    id: 'trout',
    name: 'Rainbow Trout',
    scientific: 'Oncorhynchus mykiss',
    temp: [3, 12, 17, 23],
    doCritical: 5,
    doOptimal: 8,
    stages: {
      fry: { label: 'Fry', weightRange: [0.2, 2], rate: 8, meals: 8, protein: 52, fcr: 0.8, pelletMm: '0.5' },
      fingerling: { label: 'Fingerling', weightRange: [2, 20], rate: 4.5, meals: 5, protein: 48, fcr: 0.9, pelletMm: '1.0–1.5' },
      juvenile: { label: 'Juvenile', weightRange: [20, 150], rate: 2.5, meals: 4, protein: 45, fcr: 1.0, pelletMm: '2.0–3.0' },
      growout: { label: 'Grow-out', weightRange: [150, 1000], rate: 1.4, meals: 3, protein: 42, fcr: 1.1, pelletMm: '4.0–6.0' },
      brood: { label: 'Broodstock', weightRange: [1000, 4000], rate: 0.8, meals: 2, protein: 45, fcr: 1.4, pelletMm: '8.0' },
    },
  },
  shrimp: {
    id: 'shrimp',
    name: 'Whiteleg Shrimp',
    scientific: 'Litopenaeus vannamei',
    temp: [18, 27, 31, 35],
    doCritical: 3,
    doOptimal: 5,
    stages: {
      fry: { label: 'Post-larvae', weightRange: [0.01, 0.5], rate: 15, meals: 6, protein: 45, fcr: 0.8, pelletMm: 'Crumble' },
      fingerling: { label: 'Nursery', weightRange: [0.5, 3], rate: 8, meals: 5, protein: 40, fcr: 1.0, pelletMm: '0.5–0.8' },
      juvenile: { label: 'Juvenile', weightRange: [3, 10], rate: 5, meals: 4, protein: 38, fcr: 1.2, pelletMm: '1.2' },
      growout: { label: 'Grow-out', weightRange: [10, 30], rate: 2.8, meals: 4, protein: 35, fcr: 1.4, pelletMm: '1.8–2.2' },
      brood: { label: 'Broodstock', weightRange: [30, 60], rate: 2, meals: 3, protein: 40, fcr: 1.8, pelletMm: '2.5' },
    },
  },
  catfish: {
    id: 'catfish',
    name: 'Channel Catfish',
    scientific: 'Ictalurus punctatus',
    temp: [12, 26, 30, 35],
    doCritical: 3,
    doOptimal: 5,
    stages: {
      fry: { label: 'Fry', weightRange: [0.05, 1], rate: 10, meals: 6, protein: 45, fcr: 0.9, pelletMm: '0.4' },
      fingerling: { label: 'Fingerling', weightRange: [1, 30], rate: 5, meals: 4, protein: 36, fcr: 1.2, pelletMm: '1.5' },
      juvenile: { label: 'Juvenile', weightRange: [30, 200], rate: 3, meals: 3, protein: 32, fcr: 1.5, pelletMm: '3.0' },
      growout: { label: 'Grow-out', weightRange: [200, 1000], rate: 1.8, meals: 2, protein: 28, fcr: 1.8, pelletMm: '5.0' },
      brood: { label: 'Broodstock', weightRange: [1000, 4000], rate: 0.9, meals: 1, protein: 32, fcr: 2.2, pelletMm: '8.0' },
    },
  },
}

export const STAGE_ORDER: StageId[] = ['fry', 'fingerling', 'juvenile', 'growout', 'brood']

export interface FeedingInput {
  species: SpeciesId
  stage: StageId
  stockCount: number
  avgWeight: number
  survival: number
  temperature: number
  oxygen: number
  ammonia: number
  pondVolume: number
  ph: number
  season: SeasonId
}

export type AlertLevel = 'critical' | 'warning' | 'info'

export type AlertId =
  | 'doCritical'
  | 'doLow'
  | 'tempLethal'
  | 'tempCold'
  | 'tempHot'
  | 'ammonia'
  | 'phLethal'
  | 'phAcidic'
  | 'phAlkaline'
  | 'season'
  | 'weight'
  | 'density'
  | 'optimal'

export interface AlertParams {
  [key: string]: string | number | boolean | undefined
  species?: SpeciesId
  stage?: StageId
  better?: StageId
  season?: SeasonId
  toxic?: boolean
}

export interface Alert {
  level: AlertLevel
  id: AlertId
  params: AlertParams
}

export type MealNoteId = 'steady' | 'light' | 'peak' | 'taper'

export interface Meal {
  hour: number
  time: string
  grams: number
  share: number
  note: MealNoteId
}

export interface ProjectionDay {
  day: number
  avgWeight: number
  biomassKg: number
  feedKg: number
}

export interface FeedingResult {
  biomassKg: number
  stockingDensity: number
  baseFeedKg: number
  optimizedFeedKg: number
  savedKg: number
  savedPct: number
  tempFactor: number
  oxygenFactor: number
  ammoniaFactor: number
  phFactor: number
  seasonFactor: number
  feedingWindow: [number, number]
  appetiteIndex: number
  protein: number
  fcr: number
  pelletMm: string
  expectedGainKg: number
  nitrogenBaseKg: number
  nitrogenOptKg: number
  phosphorusOptKg: number
  meals: Meal[]
  projection: ProjectionDay[]
  alerts: Alert[]
  suspended: boolean
}

const NITROGEN_IN_PROTEIN = 0.16
const NITROGEN_RETENTION = 0.3
const PHOSPHORUS_IN_FEED = 0.01
const PHOSPHORUS_RETENTION = 0.3
const UNEATEN_FRACTION_WHEN_OVERFED = 0.85

const clamp = (v: number, min = 0, max = 1) => Math.min(max, Math.max(min, v))

/** Appetite response to temperature: ramps up to the optimal band, then falls sharply toward the lethal maximum. */
export function temperatureFactor(t: number, [lo, optLo, optHi, hi]: SpeciesProfile['temp']) {
  if (t <= lo || t >= hi) return 0
  if (t < optLo) return clamp(((t - lo) / (optLo - lo)) ** 1.3)
  if (t <= optHi) return 1
  return clamp(((hi - t) / (hi - optHi)) ** 1.5)
}

/** Below critical DO, digestion fails and feeding must stop; between critical and optimal appetite scales from 40% to 100%. */
export function oxygenFactor(dO: number, critical: number, optimal: number) {
  if (dO < critical) return 0
  if (dO >= optimal) return 1
  return 0.4 + 0.6 * ((dO - critical) / (optimal - critical))
}

/** Total ammonia nitrogen (mg/L) suppresses appetite and feeding adds further ammonia load. */
export function ammoniaFactor(tan: number) {
  if (tan <= 0.5) return 1
  if (tan <= 1) return 0.9
  if (tan <= 2) return 0.7
  if (tan <= 3) return 0.5
  return 0.25
}

/** Fish feed best between pH 6.5 and 8.5; outside that range gill stress suppresses appetite. */
export function phFactor(ph: number) {
  if (ph < 5 || ph > 10) return 0
  if (ph < 6.5) return clamp(0.4 + 0.6 * ((ph - 5) / 1.5))
  if (ph <= 8.5) return 1
  return clamp(1 - 0.6 * ((ph - 8.5) / 1.5))
}

export function formatHour(h: number) {
  const hours = Math.floor(h)
  const minutes = Math.round((h - hours) * 60)
  const adjH = minutes === 60 ? hours + 1 : hours
  const adjM = minutes === 60 ? 0 : minutes
  return `${String(adjH).padStart(2, '0')}:${String(adjM).padStart(2, '0')}`
}

/**
 * Meals avoid the dawn oxygen minimum and the post-dusk decline.
 * Portions follow a daylight curve because photosynthesis pushes DO and temperature to their peak in early afternoon.
 */
function buildSchedule(totalKg: number, mealCount: number, [start, end]: [number, number], oxygenTight: boolean): Meal[] {
  if (totalKg <= 0 || mealCount <= 0) return []
  const windowStart = start + (oxygenTight ? 1 : 0)
  const windowEnd = end - (oxygenTight ? 1 : 0)
  const span = Math.max(1, windowEnd - windowStart)
  const peak = windowStart + span * 0.6

  const slots = Array.from({ length: mealCount }, (_, i) =>
    mealCount === 1 ? peak : windowStart + (span * i) / (mealCount - 1),
  )
  const weights = slots.map((h) => 0.55 + 0.45 * Math.cos(((h - peak) / span) * Math.PI))
  const weightSum = weights.reduce((a, b) => a + b, 0)

  return slots.map((h, i) => {
    const share = weights[i] / weightSum
    const relative = (h - windowStart) / span
    let note: MealNoteId = 'steady'
    if (relative < 0.2) note = 'light'
    else if (Math.abs(h - peak) < span * 0.2) note = 'peak'
    else if (relative > 0.85) note = 'taper'
    return { hour: h, time: formatHour(h), grams: totalKg * 1000 * share, share, note }
  })
}

export function calculateFeeding(input: FeedingInput): FeedingResult {
  const species = SPECIES[input.species]
  const stage = species.stages[input.stage]

  const liveCount = input.stockCount * clamp(input.survival / 100)
  const biomassKg = (liveCount * input.avgWeight) / 1000
  const stockingDensity = input.pondVolume > 0 ? biomassKg / input.pondVolume : 0

  const tF = temperatureFactor(input.temperature, species.temp)
  const oF = oxygenFactor(input.oxygen, species.doCritical, species.doOptimal)
  const aF = ammoniaFactor(input.ammonia)
  const pF = phFactor(input.ph)
  const season = SEASONS[input.season]
  const sF = season.factor
  const appetiteIndex = tF * oF * aF * pF * sF

  const baseFeedKg = biomassKg * (stage.rate / 100)
  const optimizedFeedKg = baseFeedKg * appetiteIndex
  const savedKg = Math.max(0, baseFeedKg - optimizedFeedKg)
  const savedPct = baseFeedKg > 0 ? (savedKg / baseFeedKg) * 100 : 0

  const nitrogenPerKgFeed = (stage.protein / 100) * NITROGEN_IN_PROTEIN
  const nitrogenOptKg = optimizedFeedKg * nitrogenPerKgFeed * (1 - NITROGEN_RETENTION)
  const nitrogenBaseKg = nitrogenOptKg + savedKg * UNEATEN_FRACTION_WHEN_OVERFED * nitrogenPerKgFeed
  const phosphorusOptKg = optimizedFeedKg * PHOSPHORUS_IN_FEED * (1 - PHOSPHORUS_RETENTION)

  const expectedGainKg = optimizedFeedKg / stage.fcr
  const suspended = appetiteIndex === 0

  const oxygenTight = input.oxygen < species.doOptimal
  const reduceMeals = oF < 0.7 || tF < 0.5 || pF < 0.7 || input.season === 'winter'
  const mealCount = suspended ? 0 : reduceMeals ? Math.max(1, stage.meals - 1) : stage.meals
  const meals = buildSchedule(optimizedFeedKg, mealCount, season.window, oxygenTight)

  const projection: ProjectionDay[] = []
  let weight = input.avgWeight
  for (let day = 1; day <= 7; day++) {
    const bio = (liveCount * weight) / 1000
    const feed = bio * (stage.rate / 100) * appetiteIndex
    projection.push({ day, avgWeight: weight, biomassKg: bio, feedKg: feed })
    const gain = liveCount > 0 ? ((feed / stage.fcr) * 1000) / liveCount : 0
    weight += gain
  }

  const alerts: Alert[] = []
  const [lo, optLo, optHi, hi] = species.temp

  if (input.oxygen < species.doCritical) {
    alerts.push({
      level: 'critical',
      id: 'doCritical',
      params: { oxygen: input.oxygen.toFixed(1), critical: species.doCritical },
    })
  } else if (input.oxygen < species.doOptimal) {
    alerts.push({
      level: 'warning',
      id: 'doLow',
      params: { pct: (oF * 100).toFixed(0), optimal: species.doOptimal },
    })
  }

  if (input.temperature <= lo || input.temperature >= hi) {
    alerts.push({
      level: 'critical',
      id: 'tempLethal',
      params: { temp: input.temperature, lo, hi, species: species.id },
    })
  } else if (input.temperature < optLo || input.temperature > optHi) {
    alerts.push({
      level: 'warning',
      id: input.temperature < optLo ? 'tempCold' : 'tempHot',
      params: { lo: optLo, hi: optHi, pct: (tF * 100).toFixed(0) },
    })
  }

  if (input.ammonia > 1) {
    alerts.push({
      level: input.ammonia > 2 ? 'critical' : 'warning',
      id: 'ammonia',
      params: { tan: input.ammonia.toFixed(1) },
    })
  }

  if (input.ph < 5 || input.ph > 10) {
    alerts.push({ level: 'critical', id: 'phLethal', params: { ph: input.ph.toFixed(1) } })
  } else if (input.ph < 6.5 || input.ph > 8.5) {
    alerts.push({
      level: 'warning',
      id: input.ph < 6.5 ? 'phAcidic' : 'phAlkaline',
      params: { pct: (pF * 100).toFixed(0), toxic: input.ph > 8.5 && input.ammonia > 0.5 },
    })
  }

  if (sF < 1) {
    alerts.push({ level: 'info', id: 'season', params: { season: season.id } })
  }

  const [wMin, wMax] = stage.weightRange
  if (input.avgWeight < wMin || input.avgWeight > wMax) {
    const better = STAGE_ORDER.find((s) => {
      const [a, b] = species.stages[s].weightRange
      return input.avgWeight >= a && input.avgWeight <= b
    })
    alerts.push({
      level: 'info',
      id: 'weight',
      params: { species: species.id, stage: input.stage, lo: wMin, hi: wMax, weight: input.avgWeight, better },
    })
  }

  if (stockingDensity > 40) {
    alerts.push({ level: 'warning', id: 'density', params: { density: stockingDensity.toFixed(1) } })
  }

  if (alerts.length === 0 || alerts.every((a) => a.id === 'season')) {
    alerts.push({ level: 'info', id: 'optimal', params: {} })
  }

  return {
    biomassKg,
    stockingDensity,
    baseFeedKg,
    optimizedFeedKg,
    savedKg,
    savedPct,
    tempFactor: tF,
    oxygenFactor: oF,
    ammoniaFactor: aF,
    phFactor: pF,
    seasonFactor: sF,
    feedingWindow: season.window,
    appetiteIndex,
    protein: stage.protein,
    fcr: stage.fcr,
    pelletMm: stage.pelletMm,
    expectedGainKg,
    nitrogenBaseKg,
    nitrogenOptKg,
    phosphorusOptKg,
    meals,
    projection,
    alerts,
    suspended,
  }
}

/** Finds the next upcoming meal relative to `now`, rolling over to tomorrow's first meal after the last one. */
export function findNextMeal(meals: Meal[], now: Date) {
  if (meals.length === 0) return null
  const at = (hour: number, dayOffset: number) => {
    const d = new Date(now)
    d.setHours(0, 0, 0, 0)
    d.setDate(d.getDate() + dayOffset)
    d.setTime(d.getTime() + Math.round(hour * 60) * 60_000)
    return d
  }
  const timeline = [-1, 0, 1].flatMap((offset) => meals.map((meal, index) => ({ meal, index, date: at(meal.hour, offset) })))
  const nextIdx = timeline.findIndex((t) => t.date.getTime() > now.getTime())
  const next = timeline[nextIdx]
  const prev = timeline[nextIdx - 1]
  return { ...next, previous: prev.date }
}
