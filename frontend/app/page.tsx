"use client"

import { useState } from 'react'
import { usePoolWebSocket } from '@/hooks/usePoolWebSocket'
import { SafetyBanner } from '@/components/SafetyBanner'
import { MetricsGrid } from '@/components/MetricsGrid'
import { AlertsFeed } from '@/components/AlertsFeed'
import { MLForecastCard } from '@/components/MLForecastCard'
import { HistoricalChart } from '@/components/HistoricalChart'
import { SkinSafetyCard } from '@/components/SkinSafetyCard'
import { Waves, Settings } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [selectedPoolId, setSelectedPoolId] = useState<string>('pool_vit_01')
  const { latestReading, latestAlerts, recommendation } = usePoolWebSocket(selectedPoolId)

  return (
    <main className="min-h-screen bg-[#030712] text-slate-200">
      {/* Top Navbar */}
      <nav className="h-16 border-b border-white/5 bg-black/20 backdrop-blur-3xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-lg shadow-lg">
              <Waves className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 font-outfit">
              SafeDip
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedPoolId}
              onChange={(e) => setSelectedPoolId(e.target.value)}
              className="bg-zinc-900 border border-white/10 text-sm rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-medium"
            >
              <option value="pool_vit_01">Main Campus Pool (pool_vit_01)</option>
              {/* Additional pools would go here */}
            </select>
            <Link href="/preferences" className="p-2 text-slate-400 hover:text-white transition-colors bg-white/5 rounded-lg border border-white/5 hover:border-white/10">
              <Settings className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Safety Banner */}
        <section className="animate-in fade-in slide-in-from-top-4 duration-700">
          <SafetyBanner status={latestReading?.safety_status} />
        </section>

        {/* Metrics Grid */}
        <section className="animate-in fade-in slide-in-from-top-8 duration-700 delay-150">
           <MetricsGrid reading={latestReading} />
        </section>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
          
          {/* Left Column: Historical Chart */}
          <div className="lg:col-span-2 space-y-6">
            <div className="h-[450px]">
              <HistoricalChart latestReading={latestReading} poolId={selectedPoolId} />
            </div>
          </div>

          {/* Right Column: Skin Safety, AI Forecast & Alerts */}
          <div className="space-y-6 flex flex-col">
            <div className="min-h-[280px]">
              <SkinSafetyCard latestReading={latestReading} />
            </div>
            <div>
              <MLForecastCard recommendation={recommendation} />
            </div>
            <div className="max-h-[360px]">
              <AlertsFeed alerts={latestAlerts} />
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
