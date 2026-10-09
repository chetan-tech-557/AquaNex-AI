'use client'

import { Cpu, ShieldCheck, AlertTriangle, Sparkles, Activity, Layers } from 'lucide-react'
import type { BackendRecommendation } from '@/lib/api/aquanex'

interface AiDiagnosticsProps {
  backendRecommendation?: BackendRecommendation
  isLiveBackend: boolean
}

const getRiskBadge = (level: string) => {
  const l = (level || '').toLowerCase()
  if (l.includes('low') || l.includes('optimal')) {
    return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
  }
  if (l.includes('moderate') || l.includes('medium')) {
    return 'bg-amber-500/15 text-amber-400 border-amber-500/30'
  }
  return 'bg-rose-500/15 text-rose-400 border-rose-500/30'
}

export function AiDiagnostics({ backendRecommendation, isLiveBackend }: AiDiagnosticsProps) {
  if (!isLiveBackend || !backendRecommendation) {
    return (
      <div className="glass rounded-2xl p-5 border border-dashed border-amber-500/30 bg-amber-500/5">
        <div className="flex items-center gap-2 text-amber-400">
          <AlertTriangle className="size-4 shrink-0" />
          <span className="text-sm font-medium">Local Heuristic Mode Active</span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
          Start the Python FastAPI server (<code className="rounded bg-white/10 px-1 py-0.5 font-mono text-[11px]">python -m uvicorn backend.app.server:app --port 8000</code>) to enable Gradient Boosting ML inference, SciPy SLSQP optimization, and TreeSHAP explainability.
        </p>
      </div>
    )
  }

  const { feed_prediction, waste_prediction, pollution_risk, optimization, explanation, reliability } =
    backendRecommendation

  return (
    <div className="glass flex flex-col gap-5 rounded-2xl p-5 border border-primary/20 shadow-xl shadow-primary/5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/40 pb-4">
        <div className="flex items-center gap-2">
          <div className="flex size-7 items-center justify-center rounded-lg bg-primary/20 text-primary">
            <Cpu className="size-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold tracking-tight">AI & Machine Learning Engine Diagnostics</h3>
            <p className="text-xs text-muted-foreground">Authoritative Python Backend Decision Support</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-medium text-emerald-400">
            <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Live Backend Connected
          </span>
          <span className="rounded-full bg-muted/60 px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
            {optimization.solver_status || 'SciPy SLSQP'}
          </span>
        </div>
      </div>

      {/* Grid of ML Insights */}
      <div className="grid gap-4 sm:grid-cols-3">
        {/* Feed Model Card */}
        <div className="rounded-xl border border-border/50 bg-background/40 p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
              <span>Champion ML Model</span>
              <Sparkles className="size-3.5 text-primary" />
            </div>
            <p className="font-semibold text-sm truncate" title={feed_prediction.model_name}>
              {feed_prediction.model_name.split('(')[0].trim()}
            </p>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Confidence: <span className="font-mono font-medium text-foreground">{Math.round((feed_prediction.confidence_or_uncertainty || 0.94) * 100)}%</span>
            </p>
          </div>
          {feed_prediction.applied_cap && (
            <div className="mt-2 rounded bg-amber-500/10 p-1.5 text-[10px] text-amber-300 leading-tight">
              {feed_prediction.applied_cap}
            </div>
          )}
        </div>

        {/* Waste Prediction Card */}
        <div className="rounded-xl border border-border/50 bg-background/40 p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
              <span>Feed Waste Prediction</span>
              <Activity className="size-3.5 text-accent" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-xl font-bold">{waste_prediction.expected_waste_kg.toFixed(2)} kg</span>
              <span className={`rounded border px-1.5 py-0.2 text-[10px] font-medium uppercase ${getRiskBadge(waste_prediction.risk_level)}`}>
                {waste_prediction.risk_level}
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground mt-1">
              Waste Risk Score: <span className="font-mono font-medium text-foreground">{waste_prediction.risk_score}/100</span>
            </p>
          </div>
        </div>

        {/* Pollution Risk Card */}
        <div className="rounded-xl border border-border/50 bg-background/40 p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
              <span>Pollution Risk Engine</span>
              <ShieldCheck className="size-3.5 text-primary" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-xl font-bold">{pollution_risk.risk_score}/100</span>
              <span className={`rounded border px-1.5 py-0.2 text-[10px] font-medium uppercase ${getRiskBadge(pollution_risk.risk_level)}`}>
                {pollution_risk.risk_level}
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground mt-1 truncate" title={pollution_risk.recommended_mitigation || 'Normal water quality'}>
              {pollution_risk.recommended_mitigation || 'Normal conditions maintained'}
            </p>
          </div>
        </div>
      </div>

      {/* TreeSHAP Feature Attribution */}
      {explanation?.top_features && explanation.top_features.length > 0 && (
        <div className="rounded-xl border border-border/50 bg-background/40 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Layers className="size-4 text-primary" />
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                TreeSHAP Feature Attribution (Prediction Drivers)
              </h4>
            </div>
            <span className="text-[11px] text-muted-foreground font-mono">{reliability}</span>
          </div>

          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {explanation.top_features.slice(0, 4).map((feat, idx) => (
              <div
                key={idx}
                className="flex flex-col justify-between rounded-lg border border-border/40 bg-muted/20 p-2.5"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium truncate" title={feat.display_name}>
                    {feat.display_name}
                  </span>
                  <span
                    className={`text-[10px] font-mono px-1 rounded ${
                      feat.impact_direction?.includes('INCREASE')
                        ? 'text-emerald-400 bg-emerald-500/10'
                        : 'text-rose-400 bg-rose-500/10'
                    }`}
                  >
                    {feat.shap_value > 0 ? `+${feat.shap_value.toFixed(2)}` : feat.shap_value.toFixed(2)}
                  </span>
                </div>
                <div className="mt-1 flex items-baseline justify-between text-[11px] text-muted-foreground">
                  <span>Value: {String(feat.value)}</span>
                  <span className="text-[10px]">{feat.impact_direction.replace('_', ' ').toLowerCase()}</span>
                </div>
              </div>
            ))}
          </div>

          {explanation.summary && (
            <p className="mt-3 text-xs text-muted-foreground italic border-t border-border/30 pt-2">
              &ldquo;{explanation.summary}&rdquo;
            </p>
          )}
        </div>
      )}
    </div>
  )
}
