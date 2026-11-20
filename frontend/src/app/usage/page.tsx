"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import { Loader2, Cpu, DollarSign, Search, Zap, ExternalLink } from "lucide-react";

export default function GlobalUsagePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["global-usage"],
    queryFn: () => fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/usage`).then((r) => r.json()),
    refetchInterval: 15000,
  });

  if (isLoading) {
    return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;
  }

  const formatTokens = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n));
  const formatUSD = (n: number) => n < 0.001 ? `$${(n * 100).toFixed(4)}¢` : `$${n.toFixed(4)}`;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Global Usage & Cost</h1>
        <p className="text-sm text-gray-500 mt-1">All projects combined · Groq llama-3.3-70b · $0.59/1M input · $0.79/1M output</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <Cpu size={16} className="text-purple-500" />
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Tokens</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{formatTokens(data?.total_tokens ?? 0)}</div>
          <div className="text-xs text-gray-400 mt-1">
            {formatTokens(data?.total_input_tokens ?? 0)} in · {formatTokens(data?.total_output_tokens ?? 0)} out
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <Zap size={16} className="text-yellow-500" />
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">AI Cost</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{formatUSD(data?.total_ai_cost_usd ?? 0)}</div>
          <div className="text-xs text-gray-400 mt-1">Groq API</div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <Search size={16} className="text-blue-500" />
            <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">SERP Calls</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{data?.total_serp_calls ?? 0}</div>
          <div className="text-xs text-gray-400 mt-1">{formatUSD(data?.total_serp_cost_usd ?? 0)} est.</div>
        </div>

        <div className="bg-white border border-brand-200 bg-brand-50 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign size={16} className="text-brand-600" />
            <span className="text-xs text-brand-600 font-medium uppercase tracking-wide">Total Cost</span>
          </div>
          <div className="text-2xl font-bold text-brand-700">{formatUSD(data?.total_cost_usd ?? 0)}</div>
          <div className="text-xs text-brand-400 mt-1">All projects</div>
        </div>
      </div>

      {/* Per-project breakdown */}
      {data?.by_project?.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Cost per Domain / Project</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-400 border-b">
                <th className="pb-2">Project</th>
                <th className="pb-2 text-right">Input</th>
                <th className="pb-2 text-right">Output</th>
                <th className="pb-2 text-right">AI Cost</th>
                <th className="pb-2 text-right">SERP Calls</th>
                <th className="pb-2 text-right">Total Cost</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {data.by_project.map((p: any) => (
                <tr key={p.project_id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50">
                  <td className="py-3 font-medium text-gray-800">{p.project_name}</td>
                  <td className="py-3 text-right text-gray-600">{formatTokens(p.input_tokens)}</td>
                  <td className="py-3 text-right text-gray-600">{formatTokens(p.output_tokens)}</td>
                  <td className="py-3 text-right text-gray-600">{formatUSD(p.ai_cost_usd)}</td>
                  <td className="py-3 text-right text-gray-500">{p.serp_calls}</td>
                  <td className="py-3 text-right font-semibold text-brand-600">{formatUSD(p.total_cost_usd)}</td>
                  <td className="py-3 text-right">
                    <Link
                      href={`/projects/${p.project_id}/usage`}
                      className="text-xs text-gray-400 hover:text-brand-600 flex items-center gap-1 justify-end"
                    >
                      Details <ExternalLink size={10} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(!data?.by_project || data.by_project.length === 0) && (
        <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
          <p className="text-gray-500 text-sm">No usage data yet. Run an analysis first.</p>
        </div>
      )}
    </div>
  );
}
