import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { Reading } from '@/hooks/usePoolWebSocket';
import { Activity } from 'lucide-react';

const METRICS = [
  { key: 'temperature', label: 'Temperature', unit: '°C', color: '#f97316' },
  { key: 'ph', label: 'pH Level', unit: '', color: '#3b82f6' },
  { key: 'tds', label: 'TDS', unit: 'ppm', color: '#8b5cf6' },
  { key: 'turbidity', label: 'Turbidity', unit: 'NTU', color: '#06b6d4' },
  { key: 'orp', label: 'ORP', unit: 'mV', color: '#10b981' },
];

export function HistoricalChart({ latestReading, poolId }: { latestReading: Reading | null, poolId: string }) {
  const [data, setData] = useState<Reading[]>([]);
  const [activeMetric, setActiveMetric] = useState(METRICS[1]);

  useEffect(() => {
    // Attempt to fetch historical from REST API
    fetch(`http://localhost:8000/api/v1/readings/${poolId}?limit=40`)
      .then(res => res.json())
      .then(json => {
        if (Array.isArray(json)) {
          // ensure oldest is first if backend sends newest first
          const sorted = json.sort((a,b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
          setData(sorted);
        }
      })
      .catch(err => console.error("Error fetching historical readings", err));
  }, [poolId]);

  useEffect(() => {
    // Append newest via WebSocket
    if (latestReading) {
      setData(prev => {
        const newData = [...prev, latestReading];
        if (newData.length > 40) return newData.slice(newData.length - 40);
        return newData;
      });
    }
  }, [latestReading]);

  const chartData = data.map(d => ({
    time: new Date(d.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    temperature: d.temperature,
    ph: d.ph,
    tds: d.tds,
    turbidity: d.turbidity,
    orp: d.orp,
  }));

  return (
    <div className="h-full flex flex-col p-6 bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-2xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <h2 className="text-xl font-bold tracking-wide text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          Real-Time Telemetry
        </h2>

        <div className="flex flex-wrap gap-2">
          {METRICS.map(m => (
            <button
              key={m.key}
              onClick={() => setActiveMetric(m)}
              className={`px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${
                activeMetric.key === m.key
                  ? 'bg-zinc-800 text-white border-zinc-600 shadow-md'
                  : 'bg-zinc-900/50 text-slate-400 border-zinc-800 hover:bg-zinc-800/80 hover:text-slate-200'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 w-full min-h-[300px]">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff1a" vertical={false} />
              <XAxis dataKey="time" stroke="#ffffff66" fontSize={12} tickMargin={10} minTickGap={30} />
              <YAxis 
                stroke="#ffffff66" 
                fontSize={12} 
                domain={['auto', 'auto']} 
                width={45}
                tickFormatter={(val) => Number.isInteger(val) ? val : val.toFixed(1)}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(24, 24, 27, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                itemStyle={{ color: activeMetric.color, fontWeight: 'bold' }}
                labelStyle={{ color: '#94a3b8', marginBottom: '8px' }}
              />
              <Line 
                type="monotone" 
                dataKey={activeMetric.key} 
                stroke={activeMetric.color} 
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: activeMetric.color, stroke: '#18181b', strokeWidth: 2 }}
                isAnimationActive={false} // Disable animation for smoother real-time feel visually
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 animate-pulse">
            Loading telemetry...
          </div>
        )}
      </div>
    </div>
  );
}
