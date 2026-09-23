import { useEffect, useState, useRef } from 'react';
import { TelemetryTick } from '../types';

export type WebSocketStatus = 'connected' | 'reconnecting' | 'disconnected' | 'dev_stream';

export function useWebSocket(missionId: string) {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [latestTick, setLatestTick] = useState<TelemetryTick | null>(null);
  const [tickHistory, setTickHistory] = useState<TelemetryTick[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const devIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    let isCancelled = false;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/telemetry/ws/${missionId}`;

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isCancelled) return;
          setStatus('connected');
        };

        ws.onmessage = (event) => {
          if (isCancelled) return;
          try {
            const data: TelemetryTick = JSON.parse(event.data);
            setLatestTick(data);
            setTickHistory((prev) => [...prev.slice(-30), data]);
          } catch (e) {
            console.error('Error parsing WebSocket tick:', e);
          }
        };

        ws.onerror = () => {
          if (isCancelled) return;
          fallbackToDevStream();
        };

        ws.onclose = () => {
          if (isCancelled) return;
          setStatus('disconnected');
        };
      } catch {
        fallbackToDevStream();
      }
    };

    // Dev Fallback stream simulator if WebSocket server is offline
    const fallbackToDevStream = () => {
      setStatus('dev_stream');
      let cycle = 0;
      devIntervalRef.current = window.setInterval(() => {
        if (isCancelled) return;
        cycle++;
        const simulatedTick: TelemetryTick = {
          timestamp: new Date().toISOString(),
          engine_hours: 1420.5 + cycle * 0.005,
          fuel_used_l: 120 + cycle * 0.2,
          load_cycles: 8 + Math.floor(cycle * 0.5),
          idle_minutes: cycle > 3 ? (cycle - 3) * 2 : 0,
          seatbelt_status: true,
          machine_moving: cycle <= 3,
          machine_speed_kph: cycle <= 3 ? 14.5 : 0.0,
          control_smoothness_score: 92,
          safety_alert_triggered: false,
          safety_signal_pattern: 'normal_operation',
        };
        setLatestTick(simulatedTick);
        setTickHistory((prev) => [...prev.slice(-30), simulatedTick]);
      }, 2000);
    };

    connect();

    return () => {
      isCancelled = true;
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (devIntervalRef.current) {
        clearInterval(devIntervalRef.current);
      }
    };
  }, [missionId]);

  return { status, latestTick, tickHistory };
}
