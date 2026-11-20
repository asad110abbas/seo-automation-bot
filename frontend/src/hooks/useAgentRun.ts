"use client";
import { useEffect, useRef, useState } from "react";

export interface ProgressEvent {
  agent: string;
  message: string;
  progress: number;
  timestamp: string;
}

export function useAgentRun(projectId: string, runId: string | null) {
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!runId) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/projects/${projectId}/runs/${runId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "heartbeat") return;
        setEvents((prev) => [...prev, data as ProgressEvent]);
      } catch {}
    };

    ws.onclose = () => setIsConnected(false);

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [projectId, runId]);

  const latestEvent = events[events.length - 1];

  return { events, latestEvent, isConnected };
}
