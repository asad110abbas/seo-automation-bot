"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { Globe, Search, Users, MapPin, FileText, Link2, BarChart3, Play, Loader2, CheckCircle2, Square, Activity } from "lucide-react";
import { api } from "@/lib/api";
import { useAgentRun } from "@/hooks/useAgentRun";

const agentLinks = [
  { label: "Website Audit", href: "audit", icon: Globe, color: "bg-blue-100 text-blue-600" },
  { label: "Keywords", href: "keywords", icon: Search, color: "bg-purple-100 text-purple-600" },
  { label: "Competitors", href: "competitors", icon: Users, color: "bg-orange-100 text-orange-600" },
  { label: "GBP", href: "gbp", icon: MapPin, color: "bg-green-100 text-green-600" },
  { label: "Content", href: "content", icon: FileText, color: "bg-pink-100 text-pink-600" },
  { label: "Link Building", href: "links", icon: Link2, color: "bg-yellow-100 text-yellow-600" },
  { label: "Reports", href: "reports", icon: BarChart3, color: "bg-indigo-100 text-indigo-600" },
];

export default function ProjectPage() {
  const { id } = useParams<{ id: string }>();
  const [runId, setRunId] = useState<string | null>(null);

  const { data: project } = useQuery({
    queryKey: ["project", id],
    queryFn: () => api.getProject(id),
  });

  const [pollingActive, setPollingActive] = useState(false);

  const { data: runs, refetch: refetchRuns } = useQuery({
    queryKey: ["runs", id],
    queryFn: () => api.getRuns(id),
    // Poll fast only when analysis is running, otherwise check once on focus
    refetchInterval: pollingActive ? 4000 : false,
    refetchOnWindowFocus: true,
  });

  const activeRun = runs?.find((r) => r.status === "pending" || r.status === "running");

  // Auto-reconnect WebSocket if an active run exists, control polling speed
  useEffect(() => {
    if (!runId && activeRun) {
      setRunId(activeRun.id);
      setPollingActive(true);
    }
    // Clear runId when run finishes, slow down polling
    if (runId && runs) {
      const current = runs.find((r) => r.id === runId);
      if (current && current.status !== "pending" && current.status !== "running") {
        setRunId(null);
        setPollingActive(false);
        refetchRuns();
      }
    }
    // Start polling when activeRun detected
    if (activeRun) {
      setPollingActive(true);
    } else {
      setPollingActive(false);
    }
  }, [activeRun, runs, runId, refetchRuns]);

  const { events, latestEvent, isConnected } = useAgentRun(id, runId);

  const run = useMutation({
    mutationFn: () => api.runAnalysis(id),
    onSuccess: (data) => {
      setRunId(data.run_id);
      setPollingActive(true);
      refetchRuns();
    },
  });

  const stop = useMutation({
    mutationFn: () => api.stopAnalysis(id, activeRun!.id),
    onSuccess: () => {
      setRunId(null);
      refetchRuns();
    },
  });

  const isRunning = run.isPending || !!activeRun;
  const lastRun = runs?.[0];

  return (
    <div className="max-w-4xl mx-auto">
      {project && (
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
              <p className="text-gray-500 text-sm mt-1">{project.website_url}</p>
              {lastRun && !isRunning && (
                <p className="text-xs text-gray-400 mt-1">
                  Last analysis: {lastRun.status === "completed" ? "✓ Completed" : "✗ Failed"}{" "}
                  {lastRun.completed_at ? `· ${new Date(lastRun.completed_at).toLocaleString()}` : ""}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {isRunning && activeRun && (
                <button
                  onClick={() => stop.mutate()}
                  disabled={stop.isPending}
                  className="flex items-center gap-2 bg-red-50 text-red-600 border border-red-200 px-4 py-2.5 rounded-lg font-semibold hover:bg-red-100 disabled:opacity-60 transition-colors"
                >
                  <Square size={14} fill="currentColor" />
                  {stop.isPending ? "Stopping..." : "Stop"}
                </button>
              )}
              <button
                onClick={() => run.mutate()}
                disabled={isRunning}
                className="flex items-center gap-2 bg-brand-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-brand-700 disabled:opacity-60 transition-colors"
              >
                {isRunning ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
                {isRunning ? "Analysis Running..." : "Run Full Analysis"}
              </button>
              <Link
                href={`/projects/${id}/usage`}
                className="flex items-center gap-2 bg-gray-100 text-gray-600 px-4 py-2.5 rounded-lg font-semibold hover:bg-gray-200 transition-colors text-sm"
              >
                <Activity size={15} />
                Usage
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Real-time progress box — shows when running */}
      {isRunning && (
        <div className="bg-white border border-brand-200 rounded-xl p-5 mb-6 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-yellow-400 animate-pulse"}`} />
            <span className="text-sm font-semibold text-gray-800">
              {isConnected ? "Analysis in progress..." : "Analysis running in background..."}
            </span>
          </div>

          {latestEvent ? (
            <>
              <div className="w-full bg-gray-100 rounded-full h-2.5 mb-2">
                <div
                  className="bg-brand-600 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${latestEvent.progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mb-3">
                <span className="font-medium capitalize">{latestEvent.agent.replace(/_/g, " ")}</span>:{" "}
                {latestEvent.message}
              </p>
            </>
          ) : (
            <div className="w-full bg-gray-100 rounded-full h-2.5 mb-3">
              <div className="bg-brand-600 h-2.5 rounded-full animate-pulse" style={{ width: "10%" }} />
            </div>
          )}

          <div className="max-h-28 overflow-y-auto space-y-1 border-t border-gray-100 pt-2">
            {events.length === 0 ? (
              <p className="text-xs text-gray-400">Waiting for agent updates...</p>
            ) : (
              events.slice(-10).reverse().map((e, i) => (
                <div key={i} className="text-xs text-gray-400 flex items-center gap-1.5">
                  <CheckCircle2 size={10} className="text-green-400 flex-shrink-0" />
                  <span className="text-gray-500 font-medium capitalize">{e.agent.replace(/_/g, " ")}:</span>
                  {e.message}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Agent cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {agentLinks.map((agent) => (
          <Link
            key={agent.href}
            href={`/projects/${id}/${agent.href}`}
            className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow group"
          >
            <div className={`inline-flex p-2 rounded-lg ${agent.color} mb-3`}>
              <agent.icon size={20} />
            </div>
            <h3 className="font-medium text-gray-900 text-sm group-hover:text-brand-600">{agent.label}</h3>
            {isRunning && (
              <p className="text-xs text-yellow-500 mt-1 flex items-center gap-1">
                <Loader2 size={10} className="animate-spin" /> updating...
              </p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
