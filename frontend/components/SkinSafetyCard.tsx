"use client"

import React, { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import { Fingerprint, AlertTriangle, CheckCircle2, ShieldAlert, Loader2, Settings } from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface SkinProfile {
  skin_type: string
  conditions: string[]
  eye_sensitive: boolean
  respiratory_sensitive: boolean
}

interface WaterReading {
  ph: number
  tds: number
  turbidity: number
  temperature: number
  orp?: number
  safety_status?: string
}

interface ParameterEntry {
  parameter: string
  label: string
  status: 'safe' | 'caution' | 'unsafe'
  advice: string
}

interface SkinAssessment {
  personal_status: 'safe' | 'caution' | 'unsafe'
  status_label: string
  score: number
  concerns: ParameterEntry[]
  parameter_breakdown: ParameterEntry[]
  advice: string
  skin_type_used: string
  conditions_used: string[]
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const STATUS_CONFIG = {
  safe: {
    banner: 'bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border-emerald-500/30',
    badge:  'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    icon:   CheckCircle2,
    iconColor: 'text-emerald-400',
    glow:   'shadow-[0_0_30px_rgba(16,185,129,0.12)]',
    ring:   'stroke-emerald-500',
    track:  'stroke-emerald-500/10',
  },
  caution: {
    banner: 'bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/30',
    badge:  'bg-amber-500/20 text-amber-300 border border-amber-500/30',
    icon:   AlertTriangle,
    iconColor: 'text-amber-400',
    glow:   'shadow-[0_0_30px_rgba(245,158,11,0.12)]',
    ring:   'stroke-amber-500',
    track:  'stroke-amber-500/10',
  },
  unsafe: {
    banner: 'bg-gradient-to-r from-red-500/10 to-rose-500/10 border-red-500/30',
    badge:  'bg-red-500/20 text-red-300 border border-red-500/30',
    icon:   ShieldAlert,
    iconColor: 'text-red-400',
    glow:   'shadow-[0_0_30px_rgba(239,68,68,0.15)]',
    ring:   'stroke-red-500',
    track:  'stroke-red-500/10',
  },
}

const PARAM_ICONS: Record<string, string> = {
  ph: 'pH', tds: 'TDS', turbidity: 'TURB', temperature: 'TEMP', orp: 'ORP',
}

// ─── Score Ring ───────────────────────────────────────────────────────────────

function ScoreRing({ score, status }: { score: number; status: 'safe' | 'caution' | 'unsafe' }) {
  const cfg = STATUS_CONFIG[status]
  const r = 44
  const circumference = 2 * Math.PI * r
  const dash = (score / 100) * circumference

  return (
    <div className="relative w-28 h-28 flex-shrink-0">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" strokeWidth="8" className={cfg.track} />
        <circle
          cx="50" cy="50" r={r} fill="none" strokeWidth="8"
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
          className={`${cfg.ring} transition-all duration-700`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-black text-white leading-none">{score}</span>
        <span className="text-[10px] text-slate-400 font-semibold mt-0.5">/ 100</span>
      </div>
    </div>
  )
}

// ─── Parameter Row ────────────────────────────────────────────────────────────

function ParamRow({ entry }: { entry: ParameterEntry }) {
  const [expanded, setExpanded] = useState(false)
  const color = entry.status === 'safe' ? 'text-emerald-400' : entry.status === 'caution' ? 'text-amber-400' : 'text-red-400'
  const dot   = entry.status === 'safe' ? 'bg-emerald-500' : entry.status === 'caution' ? 'bg-amber-500' : 'bg-red-500'

  return (
    <button
      onClick={() => setExpanded(e => !e)}
      className="w-full text-left"
    >
      <div className="flex items-center gap-3 py-2">
        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
        <span className={`text-xs font-bold w-10 flex-shrink-0 ${color}`}>
          {PARAM_ICONS[entry.parameter] ?? entry.parameter.toUpperCase()}
        </span>
        <span className="text-sm text-slate-300 flex-1 text-left">{entry.label}</span>
        <span className={`text-xs font-semibold capitalize px-2 py-0.5 rounded-full ${
          entry.status === 'safe' ? 'bg-emerald-500/15 text-emerald-300' :
          entry.status === 'caution' ? 'bg-amber-500/15 text-amber-300' :
          'bg-red-500/15 text-red-300'
        }`}>
          {entry.status}
        </span>
      </div>
      {expanded && (
        <p className="text-xs text-slate-400 pl-11 pr-2 pb-2 leading-relaxed animate-in fade-in duration-200">
          {entry.advice}
        </p>
      )}
    </button>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

interface SkinSafetyCardProps {
  latestReading: WaterReading | null
}

export function SkinSafetyCard({ latestReading }: SkinSafetyCardProps) {
  const [profile,    setProfile]    = useState<SkinProfile | null>(null)
  const [assessment, setAssessment] = useState<SkinAssessment | null>(null)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState<string | null>(null)

  // Load skin profile from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('safedip_skin_profile')
    if (stored) {
      try { setProfile(JSON.parse(stored)) } catch {}
    }
  }, [])

  // Run assessment whenever reading or profile changes
  const runAssessment = useCallback(async (reading: WaterReading, p: SkinProfile) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/v1/skin/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reading, skin_profile: p }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: SkinAssessment = await res.json()
      setAssessment(data)
    } catch (e) {
      setError('Could not reach SafeDip backend. Is it running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (latestReading && profile) {
      runAssessment(latestReading, profile)
    }
  }, [latestReading, profile, runAssessment])

  // ── No profile yet ────────────────────────────────────────────────
  if (!profile) {
    return (
      <div className="h-full rounded-2xl border border-white/10 bg-zinc-900/50 backdrop-blur-xl p-6 flex flex-col items-center justify-center text-center gap-4">
        <div className="p-4 rounded-full bg-indigo-500/10 border border-indigo-500/20">
          <Fingerprint className="w-8 h-8 text-indigo-400" />
        </div>
        <div>
          <h3 className="font-bold text-white mb-1">Set Up Your Skin Profile</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Get personalised water safety analysis based on your skin type and conditions.
          </p>
        </div>
        <Link
          href="/preferences"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition-all hover:scale-[1.02] active:scale-95"
        >
          <Settings className="w-4 h-4" />
          Set Up Profile
        </Link>
      </div>
    )
  }

  // ── No reading yet ────────────────────────────────────────────────
  if (!latestReading) {
    return (
      <div className="h-full rounded-2xl border border-white/10 bg-zinc-900/50 backdrop-blur-xl p-6 flex flex-col items-center justify-center text-center gap-3">
        <Loader2 className="w-7 h-7 text-indigo-400 animate-spin" />
        <p className="text-sm text-slate-400">Waiting for sensor data…</p>
      </div>
    )
  }

  const status = assessment?.personal_status ?? 'safe'
  const cfg    = STATUS_CONFIG[status]
  const Icon   = cfg.icon

  return (
    <div className={`h-full rounded-2xl border backdrop-blur-xl transition-all duration-500 ${cfg.banner} ${cfg.glow} overflow-hidden`}>

      {/* Header */}
      <div className="px-5 pt-5 pb-4 border-b border-white/5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <Fingerprint className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Skin Safety</span>
          </div>
          <Link
            href="/preferences"
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors flex items-center gap-1"
          >
            <Settings className="w-3 h-3" />
            Edit Profile
          </Link>
        </div>

        {/* Score + Status */}
        <div className="flex items-center gap-5 mt-4">
          {loading ? (
            <div className="w-28 h-28 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
            </div>
          ) : assessment ? (
            <ScoreRing score={assessment.score} status={status} />
          ) : null}

          <div className="flex-1">
            {assessment && (
              <>
                <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold mb-2 ${cfg.badge}`}>
                  <Icon className={`w-3.5 h-3.5 ${cfg.iconColor}`} />
                  {assessment.status_label}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {assessment.advice}
                </p>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  <span className="text-[10px] text-slate-500 bg-white/5 px-2 py-0.5 rounded-full capitalize">
                    {assessment.skin_type_used} skin
                  </span>
                  {assessment.conditions_used.filter(c => c !== 'none').map(c => (
                    <span key={c} className="text-[10px] text-slate-500 bg-white/5 px-2 py-0.5 rounded-full capitalize">
                      {c}
                    </span>
                  ))}
                </div>
              </>
            )}
            {error && (
              <p className="text-xs text-red-400 leading-relaxed">{error}</p>
            )}
          </div>
        </div>
      </div>

      {/* Parameter Breakdown */}
      {assessment && (
        <div className="px-5 py-3">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Parameter Breakdown <span className="normal-case text-slate-600">(tap to expand)</span>
          </p>
          <div className="divide-y divide-white/5">
            {assessment.parameter_breakdown.map(entry => (
              <ParamRow key={entry.parameter} entry={entry} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
