"use client"

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Save, ChevronRight, ChevronLeft, Check } from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

type SkinType = 'normal' | 'dry' | 'oily' | 'combination' | 'sensitive'
type SkinCondition = 'eczema' | 'psoriasis' | 'rosacea' | 'acne' | 'none'

export interface SkinProfile {
  skin_type: SkinType
  conditions: SkinCondition[]
  eye_sensitive: boolean
  respiratory_sensitive: boolean
}

const DEFAULT_PROFILE: SkinProfile = {
  skin_type: 'normal',
  conditions: [],
  eye_sensitive: false,
  respiratory_sensitive: false,
}

// ─── Skin Type Options ────────────────────────────────────────────────────────

const SKIN_TYPES: { value: SkinType; label: string; emoji: string; desc: string; color: string }[] = [
  {
    value: 'normal',
    label: 'Normal',
    emoji: '✨',
    desc: 'Well-balanced — neither too oily nor too dry',
    color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/40',
  },
  {
    value: 'dry',
    label: 'Dry',
    emoji: '🌵',
    desc: 'Tight, flaky, or rough — needs extra hydration',
    color: 'from-amber-500/20 to-orange-500/20 border-amber-500/40',
  },
  {
    value: 'oily',
    label: 'Oily',
    emoji: '💧',
    desc: 'Shiny, enlarged pores — prone to congestion',
    color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/40',
  },
  {
    value: 'combination',
    label: 'Combination',
    emoji: '☯️',
    desc: 'Oily T-zone with dry or normal cheeks',
    color: 'from-violet-500/20 to-indigo-500/20 border-violet-500/40',
  },
  {
    value: 'sensitive',
    label: 'Sensitive',
    emoji: '🌸',
    desc: 'Easily irritated — redness, stinging, or burning',
    color: 'from-rose-500/20 to-pink-500/20 border-rose-500/40',
  },
]

// ─── Condition Options ────────────────────────────────────────────────────────

const SKIN_CONDITIONS: { value: SkinCondition; label: string; emoji: string; desc: string }[] = [
  { value: 'eczema',    label: 'Eczema',    emoji: '🔴', desc: 'Chronic inflammation causing dry, itchy patches' },
  { value: 'psoriasis', label: 'Psoriasis', emoji: '🟡', desc: 'Autoimmune — scaly plaques on skin surface' },
  { value: 'rosacea',   label: 'Rosacea',   emoji: '🌹', desc: 'Persistent facial redness and visible blood vessels' },
  { value: 'acne',      label: 'Acne-prone',emoji: '⚡', desc: 'Prone to breakouts, whiteheads, or blackheads' },
  { value: 'none',      label: 'None',      emoji: '✅', desc: 'No specific skin conditions' },
]

// ─── Step Component Helper ────────────────────────────────────────────────────

function StepIndicator({ total, current }: { total: number; current: number }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {Array.from({ length: total }).map((_, i) => (
        <React.Fragment key={i}>
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
              i < current
                ? 'bg-indigo-500 text-white shadow-[0_0_12px_rgba(99,102,241,0.5)]'
                : i === current
                ? 'bg-indigo-500/20 border-2 border-indigo-500 text-indigo-400'
                : 'bg-white/5 border border-white/10 text-slate-500'
            }`}
          >
            {i < current ? <Check className="w-4 h-4" /> : i + 1}
          </div>
          {i < total - 1 && (
            <div className={`flex-1 h-px transition-all duration-500 ${i < current ? 'bg-indigo-500' : 'bg-white/10'}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}

// ─── Toggle Card ──────────────────────────────────────────────────────────────

function ToggleCard({
  emoji, label, desc, active, color, onClick,
}: {
  emoji: string; label: string; desc: string; active: boolean; color?: string; onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-2xl border transition-all duration-200 group ${
        active
          ? `bg-gradient-to-br ${color ?? 'from-indigo-500/20 to-indigo-500/10 border-indigo-500/50'} shadow-lg`
          : 'bg-zinc-900/50 border-white/10 hover:border-white/20 hover:bg-zinc-800/60'
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl mt-0.5 select-none">{emoji}</span>
        <div className="flex-1 min-w-0">
          <p className={`font-semibold ${active ? 'text-white' : 'text-slate-200'}`}>{label}</p>
          <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{desc}</p>
        </div>
        <div
          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-all ${
            active ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600'
          }`}
        >
          {active && <Check className="w-3 h-3 text-white" />}
        </div>
      </div>
    </button>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

const TOTAL_STEPS = 3

export default function PreferencesPage() {
  const [profile,    setProfile]    = useState<SkinProfile>(DEFAULT_PROFILE)
  const [step,       setStep]       = useState(0)
  const [saved,      setSaved]      = useState(false)
  const [saveAnim,   setSaveAnim]   = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('safedip_skin_profile')
    if (stored) {
      try { setProfile(JSON.parse(stored)) } catch {}
    }
  }, [])

  const selectSkinType = (type: SkinType) =>
    setProfile(p => ({ ...p, skin_type: type }))

  const toggleCondition = (cond: SkinCondition) => {
    setProfile(p => {
      if (cond === 'none') return { ...p, conditions: ['none'] }
      const without = p.conditions.filter(c => c !== 'none')
      const has = without.includes(cond)
      return { ...p, conditions: has ? without.filter(c => c !== cond) : [...without, cond] }
    })
  }

  const toggleSensitivity = (key: 'eye_sensitive' | 'respiratory_sensitive') =>
    setProfile(p => ({ ...p, [key]: !p[key] }))

  const handleSave = () => {
    localStorage.setItem('safedip_skin_profile', JSON.stringify(profile))
    setSaved(true)
    setSaveAnim(true)
    setTimeout(() => setSaveAnim(false), 600)
    setTimeout(() => setSaved(false), 3000)
  }

  const canProceed = () => {
    if (step === 0) return !!profile.skin_type
    if (step === 1) return profile.conditions.length > 0
    return true
  }

  return (
    <main className="min-h-screen bg-[#030712] text-slate-200">

      {/* Navbar */}
      <nav className="h-16 border-b border-white/5 bg-black/20 backdrop-blur-3xl sticky top-0 z-50">
        <div className="max-w-2xl mx-auto px-6 h-full flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Dashboard</span>
          </Link>
          <span className="text-sm text-slate-500 font-medium">Skin Profile Setup</span>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-400 mb-2">
            Your Skin Profile
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed">
            SafeDip uses your skin biology to personalise water safety alerts. 
            Your data stays on this device — nothing is sent to any server.
          </p>
        </div>

        {/* Step Indicator */}
        <StepIndicator total={TOTAL_STEPS} current={step} />

        {/* ── Step 0: Skin Type ─────────────────────────────────── */}
        {step === 0 && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
            <h2 className="text-lg font-bold text-white mb-1">What's your skin type?</h2>
            <p className="text-slate-400 text-sm mb-5">
              This determines the baseline pH tolerance thresholds used for your safety score.
            </p>
            <div className="space-y-3">
              {SKIN_TYPES.map(t => (
                <ToggleCard
                  key={t.value}
                  emoji={t.emoji}
                  label={t.label}
                  desc={t.desc}
                  active={profile.skin_type === t.value}
                  color={t.color}
                  onClick={() => selectSkinType(t.value)}
                />
              ))}
            </div>
          </div>
        )}

        {/* ── Step 1: Conditions ────────────────────────────────── */}
        {step === 1 && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
            <h2 className="text-lg font-bold text-white mb-1">Any skin conditions?</h2>
            <p className="text-slate-400 text-sm mb-5">
              Select all that apply. These tighten the safe pH and chlorine limits further.
            </p>
            <div className="space-y-3">
              {SKIN_CONDITIONS.map(c => (
                <ToggleCard
                  key={c.value}
                  emoji={c.emoji}
                  label={c.label}
                  desc={c.desc}
                  active={profile.conditions.includes(c.value)}
                  color="from-rose-500/15 to-pink-500/15 border-rose-500/40"
                  onClick={() => toggleCondition(c.value)}
                />
              ))}
            </div>
          </div>
        )}

        {/* ── Step 2: Sensitivities ─────────────────────────────── */}
        {step === 2 && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
            <h2 className="text-lg font-bold text-white mb-1">Additional sensitivities</h2>
            <p className="text-slate-400 text-sm mb-5">
              These affect chlorine (ORP) and chloramine (TDS) alert thresholds.
            </p>
            <div className="space-y-3">
              <ToggleCard
                emoji="👁️"
                label="Eye Sensitivity"
                desc="Easily irritated by chlorine — alerts trigger at lower ORP levels (chlorine) to protect your eyes"
                active={profile.eye_sensitive}
                color="from-emerald-500/15 to-teal-500/15 border-emerald-500/40"
                onClick={() => toggleSensitivity('eye_sensitive')}
              />
              <ToggleCard
                emoji="🫁"
                label="Respiratory Sensitivity (Asthma)"
                desc="Chloramine vapours can trigger breathing issues — stricter TDS limits applied to reduce chloramine exposure"
                active={profile.respiratory_sensitive}
                color="from-amber-500/15 to-orange-500/15 border-amber-500/40"
                onClick={() => toggleSensitivity('respiratory_sensitive')}
              />
              <ToggleCard
                emoji="🚫"
                label="No additional sensitivities"
                desc="Standard thresholds apply — no extra restrictions beyond your skin type"
                active={!profile.eye_sensitive && !profile.respiratory_sensitive}
                color="from-slate-500/15 to-zinc-500/15 border-slate-500/40"
                onClick={() => setProfile(p => ({ ...p, eye_sensitive: false, respiratory_sensitive: false }))}
              />
            </div>

            {/* Profile Summary */}
            <div className="mt-6 p-4 rounded-2xl bg-indigo-500/5 border border-indigo-500/20">
              <p className="text-xs font-semibold text-indigo-400 mb-2 uppercase tracking-wider">Your Profile Summary</p>
              <div className="space-y-1 text-sm">
                <div className="flex gap-2">
                  <span className="text-slate-500 w-24 flex-shrink-0">Skin type:</span>
                  <span className="text-slate-200 font-medium capitalize">{profile.skin_type}</span>
                </div>
                <div className="flex gap-2">
                  <span className="text-slate-500 w-24 flex-shrink-0">Conditions:</span>
                  <span className="text-slate-200 font-medium capitalize">
                    {profile.conditions.length === 0 ? 'None selected' : profile.conditions.join(', ')}
                  </span>
                </div>
                <div className="flex gap-2">
                  <span className="text-slate-500 w-24 flex-shrink-0">Eye:</span>
                  <span className={`font-medium ${profile.eye_sensitive ? 'text-emerald-400' : 'text-slate-400'}`}>
                    {profile.eye_sensitive ? 'Sensitive' : 'Standard'}
                  </span>
                </div>
                <div className="flex gap-2">
                  <span className="text-slate-500 w-24 flex-shrink-0">Respiratory:</span>
                  <span className={`font-medium ${profile.respiratory_sensitive ? 'text-amber-400' : 'text-slate-400'}`}>
                    {profile.respiratory_sensitive ? 'Sensitive' : 'Standard'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8">

          {/* Back / Step info */}
          <div>
            {step > 0 ? (
              <button
                onClick={() => setStep(s => s - 1)}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors px-4 py-2 rounded-xl hover:bg-white/5"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </button>
            ) : (
              <span className="text-xs text-slate-600">Step {step + 1} of {TOTAL_STEPS}</span>
            )}
          </div>

          {/* Next / Save */}
          <div className="flex items-center gap-3">
            {step > 0 && (
              <span className="text-xs text-slate-600">Step {step + 1} of {TOTAL_STEPS}</span>
            )}

            {step < TOTAL_STEPS - 1 ? (
              <button
                onClick={() => setStep(s => s + 1)}
                disabled={!canProceed()}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 disabled:text-indigo-700 text-white px-6 py-3 rounded-xl font-semibold transition-all hover:scale-[1.02] active:scale-95 disabled:cursor-not-allowed disabled:scale-100"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSave}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all active:scale-95 ${
                  saved
                    ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]'
                    : 'bg-white text-black hover:bg-slate-100 hover:scale-[1.02]'
                } ${saveAnim ? 'scale-95' : ''}`}
              >
                {saved ? (
                  <>
                    <Check className="w-5 h-5" />
                    Saved!
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    Save Profile
                  </>
                )}
              </button>
            )}
          </div>
        </div>

      </div>
    </main>
  )
}
