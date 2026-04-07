"use client"

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Save, Eye, Wind, Activity } from 'lucide-react'

interface Prefs {
  skin_sensitive: boolean;
  eye_sensitive: boolean;
  respiratory_sensitive: boolean;
}

const DEFAULT_PREFS: Prefs = {
  skin_sensitive: false,
  eye_sensitive: false,
  respiratory_sensitive: false,
}

export default function PreferencesPage() {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('safedip_user_prefs')
    if (stored) {
      try {
        setPrefs(JSON.parse(stored))
      } catch (e) {
        console.error("Failed to parse preferences", e)
      }
    }
  }, [])

  const handleToggle = (key: keyof Prefs) => {
    setPrefs(p => ({ ...p, [key]: !p[key] }))
    setSaved(false)
  }

  const handleSave = () => {
    localStorage.setItem('safedip_user_prefs', JSON.stringify(prefs))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <main className="min-h-screen bg-[#030712] text-slate-200">
      {/* Top Navbar */}
      <nav className="h-16 border-b border-white/5 bg-black/20 backdrop-blur-3xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center">
          <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Dashboard</span>
          </Link>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
          User Settings & Sensitivities
        </h1>
        <p className="text-slate-400 mb-8">
          Configure your personal health sensitivities. The SafeDip dashboard and mobile alerts will automatically lower the "safe" threshold limits for specific pool parameters to prevent irritation.
        </p>

        <div className="space-y-4">
          
          {/* Skin Sensitivity */}
          <div 
            onClick={() => handleToggle('skin_sensitive')}
            className={`p-5 rounded-2xl border backdrop-blur-xl cursor-pointer transition-all ${
              prefs.skin_sensitive 
                ? 'bg-indigo-500/10 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.2)]' 
                : 'bg-zinc-900/50 border-white/10 hover:border-white/20 hover:bg-zinc-800/80'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${prefs.skin_sensitive ? 'bg-indigo-500/20 text-indigo-400' : 'bg-white/5 text-slate-400'}`}>
                  <Activity className="w-6 h-6" />
                </div>
                <div>
                  <h3 className={`font-bold ${prefs.skin_sensitive ? 'text-white' : 'text-slate-200'}`}>Sensitive Skin / Eczema</h3>
                  <p className="text-sm text-slate-400 mt-1">Narrows safe pH range from 7.2-7.6 down to 7.0-7.8.</p>
                </div>
              </div>
              <div className={`w-12 h-6 rounded-full transition-colors relative ${prefs.skin_sensitive ? 'bg-indigo-500' : 'bg-slate-700'}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${prefs.skin_sensitive ? 'left-7' : 'left-1'}`} />
              </div>
            </div>
          </div>

          {/* Eye Sensitivity */}
          <div 
            onClick={() => handleToggle('eye_sensitive')}
            className={`p-5 rounded-2xl border backdrop-blur-xl cursor-pointer transition-all ${
              prefs.eye_sensitive 
                ? 'bg-emerald-500/10 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.2)]' 
                : 'bg-zinc-900/50 border-white/10 hover:border-white/20 hover:bg-zinc-800/80'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${prefs.eye_sensitive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 text-slate-400'}`}>
                  <Eye className="w-6 h-6" />
                </div>
                <div>
                  <h3 className={`font-bold ${prefs.eye_sensitive ? 'text-white' : 'text-slate-200'}`}>Eye Sensitivity</h3>
                  <p className="text-sm text-slate-400 mt-1">Alerts proactively on high Chlorine/ORP levels ({'>'} 800mV).</p>
                </div>
              </div>
              <div className={`w-12 h-6 rounded-full transition-colors relative ${prefs.eye_sensitive ? 'bg-emerald-500' : 'bg-slate-700'}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${prefs.eye_sensitive ? 'left-7' : 'left-1'}`} />
              </div>
            </div>
          </div>

          {/* Respiratory Sensitivity */}
          <div 
            onClick={() => handleToggle('respiratory_sensitive')}
            className={`p-5 rounded-2xl border backdrop-blur-xl cursor-pointer transition-all ${
              prefs.respiratory_sensitive 
                ? 'bg-amber-500/10 border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.2)]' 
                : 'bg-zinc-900/50 border-white/10 hover:border-white/20 hover:bg-zinc-800/80'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${prefs.respiratory_sensitive ? 'bg-amber-500/20 text-amber-400' : 'bg-white/5 text-slate-400'}`}>
                  <Wind className="w-6 h-6" />
                </div>
                <div>
                  <h3 className={`font-bold ${prefs.respiratory_sensitive ? 'text-white' : 'text-slate-200'}`}>Respiratory Sensitivity (Asthma)</h3>
                  <p className="text-sm text-slate-400 mt-1">Alerts proactively on high TDS levels mapping to chloramine buildup.</p>
                </div>
              </div>
              <div className={`w-12 h-6 rounded-full transition-colors relative ${prefs.respiratory_sensitive ? 'bg-amber-500' : 'bg-slate-700'}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${prefs.respiratory_sensitive ? 'left-7' : 'left-1'}`} />
              </div>
            </div>
          </div>

        </div>

        <div className="mt-8 flex items-center justify-end">
          <button 
            onClick={handleSave}
            className="flex items-center gap-2 bg-white text-black px-6 py-3 rounded-xl font-bold transition-all hover:bg-slate-200 hover:scale-[1.02] active:scale-95"
          >
            {saved ? (
              <>
                Saved Successfully
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Save Preferences
              </>
            )}
          </button>
        </div>

      </div>
    </main>
  )
}
