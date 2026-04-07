import React from 'react';
import { Reading } from '@/hooks/usePoolWebSocket';
import { Settings, Thermometer, Droplets, Activity, Beaker } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: number;
  unit: string;
  icon: React.ReactNode;
  status: 'safe' | 'caution' | 'unsafe';
}

function MetricCard({ label, value, unit, icon, status }: MetricCardProps) {
  const statusColors = {
    safe: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    caution: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    unsafe: 'text-red-400 bg-red-400/10 border-red-400/20 shadow-[0_0_15px_rgba(248,113,113,0.3)]',
  };

  return (
    <div className="flex flex-col p-5 bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-2xl transition-all duration-300 hover:bg-zinc-800/80 hover:-translate-y-1 hover:shadow-xl hover:border-white/20">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-white/5 rounded-lg text-slate-300">
          {icon}
        </div>
        <div className={`px-2.5 py-1 text-xs font-semibold rounded-full border uppercase tracking-wider ${statusColors[status]}`}>
          {status}
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-4xl font-bold text-white tracking-tight">{value.toFixed(label === 'pH' ? 2 : 1)}</span>
        <span className="text-sm font-medium text-slate-400">{unit}</span>
      </div>
      <div className="mt-1 text-sm text-slate-400 font-medium">{label}</div>
    </div>
  );
}

// Logic based on Threshold Matrix from Context Docs
function getPhStatus(ph: number) {
  if (ph < 6.8 || ph > 8.0) return 'unsafe';
  if (ph < 7.0 || ph > 7.8) return 'caution';
  return 'safe';
}

function getTdsStatus(tds: number) {
  if (tds > 1000) return 'unsafe';
  if (tds > 500) return 'caution';
  return 'safe';
}

function getTurbidityStatus(turb: number) {
  if (turb > 100) return 'unsafe';
  if (turb > 50) return 'caution';
  return 'safe';
}

function getTempStatus(temp: number) {
  if (temp < 18 || temp > 38) return 'unsafe';
  if (temp < 20 || temp > 35) return 'caution';
  return 'safe';
}

function getOrpStatus(orp: number) {
  if (orp < 550 || orp > 850) return 'unsafe';
  if (orp < 600 || orp > 800) return 'caution';
  return 'safe';
}

export function MetricsGrid({ reading }: { reading: Reading | null }) {
  if (!reading) {
    return (
      <div className="w-full text-center py-10 text-slate-500 animate-pulse">
        Waiting for initial reading...
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <MetricCard label="Temperature" value={reading.temperature} unit="°C" icon={<Thermometer className="w-5 h-5" />} status={getTempStatus(reading.temperature)} />
      <MetricCard label="pH Level" value={reading.ph} unit="" icon={<Beaker className="w-5 h-5" />} status={getPhStatus(reading.ph)} />
      <MetricCard label="TDS" value={reading.tds} unit="ppm" icon={<Settings className="w-5 h-5" />} status={getTdsStatus(reading.tds)} />
      <MetricCard label="Turbidity" value={reading.turbidity} unit="NTU" icon={<Droplets className="w-5 h-5" />} status={getTurbidityStatus(reading.turbidity)} />
      <MetricCard label="ORP" value={reading.orp} unit="mV" icon={<Activity className="w-5 h-5" />} status={getOrpStatus(reading.orp)} />
    </div>
  );
}
