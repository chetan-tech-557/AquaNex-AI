/**
 * AquaNex AI Frontend API Client
 * Connects the Next.js frontend to the authoritative Python FastAPI ML backend.
 */

import { type FeedingInput, type FeedingResult, calculateFeeding } from '@/lib/feeding'

export interface MealScheduleItem {
  time: string
  quantity_kg: number
  percentage_of_daily: number
}

export interface BaselineComparison {
  baseline_feed_kg: number
  baseline_daily_cost: number
  feed_saved_kg: number
  cost_saved_usd: number
  savings_percentage: number
}

export interface FeedPrediction {
  recommended_daily_feed_kg: number
  model_name: string
  confidence_or_uncertainty: number
  unadjusted_ml_feed_kg: number
  applied_cap?: string | null
}

export interface WastePrediction {
  expected_waste_kg: number
  waste_percentage: number
  risk_level: string
  risk_score: number
  primary_cause?: string | null
}

export interface PollutionRisk {
  risk_score: number
  risk_level: string
  contributing_factors: string[]
  recommended_mitigation?: string | null
}

export interface OptimizationResult {
  optimized_daily_feed_kg: number
  number_of_meals: number
  meal_schedule: MealScheduleItem[]
  baseline_comparison?: BaselineComparison | null
  solver_status: string
}

export interface FeatureImportance {
  feature_name: string
  display_name: string
  value: number | string
  shap_value: number
  impact_direction: string
}

export interface ExplanationResult {
  summary: string
  top_features: FeatureImportance[]
}

export interface BackendRecommendation {
  pond_id: string
  feed_prediction: FeedPrediction
  waste_prediction: WastePrediction
  pollution_risk: PollutionRisk
  optimization: OptimizationResult
  explanation: ExplanationResult
  warnings: string[]
  outside_validated_range: boolean
  reliability: string
  frontend_feeding_result?: Record<string, any>
}

export interface BackendHealthResponse {
  status: string
  service: string
  environment: string
  models_loaded: boolean
  feed_model: string
  waste_model: string
  pollution_model: string
}

export interface RecommendationResponse {
  success: boolean
  feedingResult: FeedingResult
  backendRecommendation?: BackendRecommendation
  isLiveBackend: boolean
  error?: string
}

export const getApiBaseUrl = (): string => {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

/**
 * Fetch recommendation from Python backend with ML & SciPy optimization.
 * Falls back to local deterministic calculations if backend is currently offline.
 */
export async function getRecommendation(input: FeedingInput): Promise<RecommendationResponse> {
  const baseUrl = getApiBaseUrl()

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 8000)

    const res = await fetch(`${baseUrl}/api/v1/recommendation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!res.ok) {
      const errText = await res.text()
      throw new Error(`Backend error (${res.status}): ${errText}`)
    }

    const json: BackendRecommendation = await res.json()

    if (json.frontend_feeding_result) {
      // Backend returned authoritative adapted FeedingResult directly!
      const feResult = json.frontend_feeding_result as FeedingResult
      return {
        success: true,
        feedingResult: feResult,
        backendRecommendation: json,
        isLiveBackend: true,
      }
    }

    // Backend returned recommendation without adapted struct, adapt using standard formula
    const localFallback = calculateFeeding(input)
    return {
      success: true,
      feedingResult: {
        ...localFallback,
        optimizedFeedKg: json.optimization.optimized_daily_feed_kg,
        baseFeedKg: json.optimization.baseline_comparison?.baseline_feed_kg ?? localFallback.baseFeedKg,
        savedKg: json.optimization.baseline_comparison?.feed_saved_kg ?? localFallback.savedKg,
        savedPct: json.optimization.baseline_comparison?.savings_percentage ?? localFallback.savedPct,
      },
      backendRecommendation: json,
      isLiveBackend: true,
    }
  } catch (err: any) {
    // Graceful offline fallback: allows UI exploration even if backend is temporarily starting up
    const fallback = calculateFeeding(input)
    return {
      success: false,
      feedingResult: fallback,
      isLiveBackend: false,
      error: err?.message || 'Failed to connect to AquaNex Python backend',
    }
  }
}

/**
 * Health check verification for AquaNex backend and ML models
 */
export async function checkBackendHealth(): Promise<{ healthy: boolean; data?: BackendHealthResponse }> {
  const baseUrl = getApiBaseUrl()
  try {
    const res = await fetch(`${baseUrl}/api/v1/health`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) return { healthy: false }
    const data: BackendHealthResponse = await res.json()
    return { healthy: data.status === 'healthy', data }
  } catch {
    return { healthy: false }
  }
}
