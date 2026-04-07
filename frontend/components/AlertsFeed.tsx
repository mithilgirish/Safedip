import React from 'react';
import { Alert } from '@/hooks/usePoolWebSocket';
import { AlertCircle, AlertTriangle } from 'lucide-react';

export function AlertsFeed({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="h-full bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex flex-col gap-4">
      <h2 className="text-xl font-bold tracking-wide text-white flex items-center gap-2">
        <AlertCircle className="w-5 h-5 text-indigo-400" />
        Real-Time Alerts Feed
      </h2>
      
      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar min-h-[300px]">
        {alerts.length > 0 ? (
          alerts.map((alert, idx) => (
            <div 
              key={idx} 
              className={`p-4 rounded-xl border backdrop-blur-md flex items-start gap-3 transition-colors ${
                alert.severity === 'unsafe' 
                  ? 'bg-red-500/10 border-red-500/30 text-red-200' 
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-200'
              }`}
            >
              <div className="mt-0.5 mt-0.5 shrink-0">
                {alert.severity === 'unsafe' ? <AlertCircle className="w-5 h-5 text-red-400" /> : <AlertTriangle className="w-5 h-5 text-amber-400" />}
              </div>
              <div>
                <p className="text-sm font-medium leading-snug">{alert.message}</p>
                <p className="text-xs mt-1 opacity-60 uppercase tracking-widest">{alert.severity}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-2 opacity-50">
            <CheckCircleIcon />
            <p>No active alerts recorded.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function CheckCircleIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check-circle">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>
    </svg>
  );
}
