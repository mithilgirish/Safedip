import { useEffect, useRef, useState } from 'react'

export interface Reading {
  id: number;
  device_id: string;
  pool_id: string;
  temperature: number;
  tds: number;
  turbidity: number;
  ph: number;
  orp: number;
  safety_status: 'safe' | 'caution' | 'unsafe';
  created_at: string;
}

export interface Alert {
  message: string;
  severity: 'caution' | 'unsafe';
}

export function usePoolWebSocket(poolId: string | null) {
  const [latestReading, setLatestReading] = useState<Reading | null>(null)
  const [latestAlerts, setLatestAlerts] = useState<Alert[]>([])
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!poolId) return
    
    // Connect to WebSocket
    const socket = new WebSocket(`ws://localhost:8000/ws/pool/${poolId}`)
    ws.current = socket

    socket.onopen = () => {
      console.log(`WebSocket connected to pool: ${poolId}`)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'new_reading') {
          setLatestReading(data.reading)
          if (data.alerts && data.alerts.length > 0) {
            setLatestAlerts(prev => [...data.alerts, ...prev].slice(0, 50))
          }
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message", err)
      }
    }

    socket.onerror = (error) => {
      console.error("WebSocket error", error)
    }

    socket.onclose = () => {
      console.log("WebSocket disconnected")
    }

    return () => {
      socket.close()
    }
  }, [poolId])

  return { latestReading, latestAlerts }
}
