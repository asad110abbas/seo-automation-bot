"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, Cpu, DollarSign, Search, Zap } from "lucide-react";

export default function UsagePage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["usage", id],
    queryFn: () => api.getUsage(id),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="animate-spin text-gray-400" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-3xl mx-auto bg-white rounded-xl border border-gray-200 p-8 text-center">
        <p className="text-gray-500">No usage data yet. Run an analysis first.</p>
      </div>
    );
  }

  const formatTokens = (n: number) =>
    n >= 1000 ? `${(n / 1000).toFixed(1)}k` : n.toString();

  const formatUSD = (n: number) =>
    n < 0.001 ? `$${(n * 100).toFixed(4)}¢` : `$${n.toFixed(4)}`;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Usage & Cost Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Groq AI (llama-3.3-70b) · $0.59/1M input · $0.79/1M output</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <Cpu size={16} className="text-purple-500" />
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Tokens</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{formatTokens(data.total_tokens)}</div>
          <div className="text-xs text-gray-400 mt-1">
            {formatTokens(data.total_input_tokens)} in · {formatTokens(data.total_output_tokens)} out
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <Zap size={16} className="text-yellow-500" />
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">AI Cost</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{formatUSD(data.total_ai_cost_usd)}</div>
          <div className="text-xs text-gray-400 mt-1">Groq API charges</div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <Search size={16} className="text-blue-500" />
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">SERP Calls</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{data.total_serp_calls}</div>
          <div className="text-xs text-gray-400 mt-1">{formatUSD(data.total_serp_cost_usd)} est. cost</div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 border-brand-200 bg-brand-50">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign size={16} className="text-brand-600" />
            <span className="text-xs text-brand-600 font-medium uppercase tracking-wide">Total Cost</span>
          </div>
          <div className="text-2xl font-bold text-brand-700">{formatUSD(data.total_cost_usd)}</div>
          <div className="text-xs text-brand-400 mt-1">AI + SERP combined</div>
        </div>
      </div>

      {/* Per-agent breakdown */}
      {Object.keys(data.by_agent).length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Cost by Agent Phase</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-400 border-b pb-2">
                <th className="pb-2">Agent / Phase</th>
                <th className="pb-2 text-right">Input Tokens</th>
                <th className="pb-2 text-right">Output Tokens</th>
                <th className="pb-2 text-right">AI Cost</th>
                <th className="pb-2 text-right">Calls</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data.by_agent).map(([agent, stats]) => (
                <tr key={agent} className="border-b border-gray-50 last:border-0">
                  <td className="py-2.5 font-medium text-gray-700 capitalize">
                    {agent.replace(/_/g, " ")}
                  </td>
                  <td className="py-2.5 text-right text-gray-600">{formatTokens(stats.input_tokens)}</td>
                  <td className="py-2.5 text-right text-gray-600">{formatTokens(stats.output_tokens)}</td>
                  <td className="py-2.5 text-right text-gray-600">{formatUSD(stats.cost_usd)}</td>
                  <td className="py-2.5 text-right text-gray-500">{stats.calls}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Per-run log */}
      {data.logs.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Detailed Log</h2>
          <div className="space-y-2">
            {data.logs.map((log, i) => (
              <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-gray-50 last:border-0">
                <div>
                  <span className="font-medium text-gray-700 capitalize">{log.agent.replace(/_/g, " ")}</span>
                  <span className="text-xs text-gray-400 ml-2">{new Date(log.timestamp).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-4 text-right text-xs text-gray-500">
                  <span>{formatTokens(log.input_tokens + log.output_tokens)} tokens</span>
                  <span className="text-brand-600 font-medium">{formatUSD(log.ai_cost_usd)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
