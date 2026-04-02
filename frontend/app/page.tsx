"use client"

import { useState } from 'react'
import { usePoolWebSocket } from '@/hooks/usePoolWebSocket'

export default function Home() {
  const [selectedPoolId, setSelectedPoolId] = useState<string>('pool_vit_01')
  const { latestReading, latestAlerts } = usePoolWebSocket(selectedPoolId)

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
          SafeDip Dashboard &nbsp;
          <code className="font-bold">{selectedPoolId}</code>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-6xl mt-12">
        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700">
          <h2 className="text-xl font-bold mb-4">Latest Reading</h2>
          {latestReading ? (
            <div className="space-y-2">
              <p>Status: <span className={
                latestReading.safety_status === 'safe' ? 'text-emerald-400' :
                latestReading.safety_status === 'caution' ? 'text-amber-400' : 'text-red-400'
              }>{latestReading.safety_status.toUpperCase()}</span></p>
              <p>pH: {latestReading.ph}</p>
              <p>TDS: {latestReading.tds} ppm</p>
              <p>Temp: {latestReading.temperature}°C</p>
              <p>ORP: {latestReading.orp} mV</p>
              <p>Turbidity: {latestReading.turbidity} NTU</p>
            </div>
          ) : (
            <p className="text-slate-400 italic">Waiting for data...</p>
          )}
        </div>

        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 md:col-span-2">
          <h2 className="text-xl font-bold mb-4">Active Alerts</h2>
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {latestAlerts.length > 0 ? (
              latestAlerts.map((alert, idx) => (
                <div key={idx} className={`p-3 rounded border ${
                  alert.severity === 'unsafe' ? 'bg-red-900/30 border-red-800 text-red-200' : 'bg-amber-900/30 border-amber-800 text-amber-200'
                }`}>
                  {alert.message}
                </div>
              ))
            ) : (
              <p className="text-slate-400 italic">No active alerts.</p>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
