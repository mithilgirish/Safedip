import React from 'react';
import { Recommendation } from '@/hooks/usePoolWebSocket';
import { BrainCircuit, Clock, Zap, Target } from 'lucide-react';

export function MLForecastCard({ recommendation }: { recommendation: Recommendation | null }) {
  if (!recommendation) {
    return (
      <div className="h-full items-center justify-center flex flex-col p-6 bg-zinc-900/50 backdrop-blur-xl border border-white/10 text-slate-500 rounded-2xl animate-pulse">
        <BrainCircuit className="w-10 h-10 mb-4 opacity-30" />
        <p>Awaiting SafeDip AI Model Forecast...</p>
      </div>
    );
  }

  const { action, urgency, reason, instruction, forecast_summary } = recommendation;

  const bgConfig = {
    immediate: 'bg-red-500/20 border-red-500/50',
    within_2_hours: 'bg-orange-500/20 border-orange-500/50',
    within_4_hours: 'bg-amber-500/20 border-amber-500/50',
    within_24_hours: 'bg-blue-500/20 border-blue-500/50',
    within_48_hours: 'bg-indigo-500/20 border-indigo-500/50',
    monitor: 'bg-purple-500/20 border-purple-500/50',
    none: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
  };

  const badgeClass = bgConfig[urgency as keyof typeof bgConfig] || bgConfig.none;

  return (
    <div className="relative overflow-hidden h-full flex flex-col p-6 bg-gradient-to-br from-zinc-900/80 to-black/80 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-xl">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 text-white/5 rotate-12 pointer-events-none">
        <BrainCircuit className="w-64 h-64" />
      </div>

      <div className="flex justify-between items-center mb-6 z-10">
        <h2 className="text-xl font-bold tracking-wide text-white flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-fuchsia-400" />
          SafeDip AI Agent Forecast
        </h2>
        <div className={`px-4 py-1.5 rounded-full border text-xs font-bold uppercase tracking-widest ${badgeClass}`}>
          Urgency: {urgency.replace(/_/g, ' ')}
        </div>
      </div>

      <div className="space-y-6 z-10 flex-1">
        <div>
          <h3 className="text-sm uppercase tracking-wider text-slate-400 font-semibold mb-2 flex items-center gap-2">
            <Target className="w-4 h-4" />
            Predicted Path Summary
          </h3>
          <p className="text-slate-200 leading-relaxed text-sm">
            {reason}
          </p>
        </div>

        {action !== 'nominal' && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <h3 className="text-sm uppercase tracking-wider text-indigo-300 font-semibold mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Action Required
            </h3>
            <p className="text-white leading-relaxed text-sm font-medium">
              {instruction}
            </p>
          </div>
        )}

        {forecast_summary && action !== 'nominal' && (
          <div className="grid grid-cols-2 gap-3 mt-auto">
             {forecast_summary.ph_breach_eta_min !== null && (
               <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                 <Clock className="w-4 h-4 text-red-400" />
                 <div className="text-xs">
                   <span className="block text-slate-400 uppercase">pH Breach ETA</span>
                   <span className="text-red-300 font-bold">{forecast_summary.ph_breach_eta_min} min</span>
                 </div>
               </div>
             )}
             {forecast_summary.tds_breach_eta_min !== null && (
               <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                 <Clock className="w-4 h-4 text-amber-400" />
                 <div className="text-xs">
                   <span className="block text-slate-400 uppercase">TDS Limit ETA</span>
                   <span className="text-amber-300 font-bold">{forecast_summary.tds_breach_eta_min} min</span>
                 </div>
               </div>
             )}
             {forecast_summary.orp_breach_eta_min !== null && (
               <div className="flex items-center gap-2 p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                 <Clock className="w-4 h-4 text-orange-400" />
                 <div className="text-xs">
                   <span className="block text-slate-400 uppercase">ORP Drop ETA</span>
                   <span className="text-orange-300 font-bold">{forecast_summary.orp_breach_eta_min} min</span>
                 </div>
               </div>
             )}
          </div>
        )}
      </div>
    </div>
  );
}
