import React from 'react';
import { AlertTriangle, CheckCircle, AlertOctagon } from 'lucide-react';

type Status = 'safe' | 'caution' | 'unsafe';

const statusConfig = {
  safe: {
    bg: 'bg-emerald-500/20',
    border: 'border-emerald-500/50',
    text: 'text-emerald-400',
    message: 'All parameters nominal. Pool is safe for swimming.',
    icon: CheckCircle,
    animation: ''
  },
  caution: {
    bg: 'bg-amber-500/20',
    border: 'border-amber-500/50',
    text: 'text-amber-400',
    message: 'Caution: Parameters nearing limits. Monitor closely.',
    icon: AlertTriangle,
    animation: ''
  },
  unsafe: {
    bg: 'bg-red-600/30',
    border: 'border-red-500/70',
    text: 'text-red-400',
    message: 'UNSAFE: Evacuate pool immediately.',
    icon: AlertOctagon,
    animation: 'animate-pulse shadow-[0_0_20px_rgba(220,38,38,0.5)]'
  },
};

export function SafetyBanner({ status }: { status: Status | undefined }) {
  if (!status) return null;
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div className={`w-full py-4 px-6 rounded-2xl border backdrop-blur-md flex items-center justify-center gap-3 transition-all duration-500 ${config.bg} ${config.border} ${config.text} ${config.animation}`}>
      <Icon className="w-8 h-8" />
      <h1 className="text-xl md:text-2xl font-bold tracking-wide">
        {config.message}
      </h1>
    </div>
  );
}
