"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, TrendingUp } from "lucide-react";

export default function CompetitorsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: competitors = [], isLoading: loadingComps } = useQuery({ queryKey: ["competitors", id], queryFn: () => api.getCompetitors(id) });
  const { data: gapData } = useQuery({ queryKey: ["gaps", id], queryFn: () => api.getContentGaps(id) });

  const gaps = gapData?.content_gaps || [];

  if (loadingComps) return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Competitor Analysis</h1>

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="font-semibold text-gray-900 mb-3">Top Competitors</h2>
        {competitors.length === 0 ? (
          <p className="text-gray-400 text-sm">No competitor data yet. Run analysis first.</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs text-gray-400 border-b"><th className="pb-2">URL</th><th className="pb-2">Rank</th><th className="pb-2">Est. Keywords</th></tr></thead>
            <tbody>
              {competitors.map((c) => (
                <tr key={c.id} className="border-b border-gray-50 last:border-0">
                  <td className="py-2 text-brand-600 hover:underline"><a href={c.competitor_url} target="_blank" rel="noreferrer">{c.competitor_url}</a></td>
                  <td className="py-2 text-gray-600">#{c.rank_position ?? "—"}</td>
                  <td className="py-2 text-gray-600">{c.estimated_keywords}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {gaps.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><TrendingUp size={16} className="text-brand-600" /> Content Gaps</h2>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs text-gray-400 border-b"><th className="pb-2">Keyword</th><th className="pb-2">Competitors</th><th className="pb-2">Opportunity</th></tr></thead>
            <tbody>
              {gaps.map((g, i) => (
                <tr key={i} className="border-b border-gray-50 last:border-0">
                  <td className="py-2 font-medium text-gray-800">{g.keyword}</td>
                  <td className="py-2 text-gray-600">{g.competitors_with_it}</td>
                  <td className="py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${g.opportunity === "high" ? "bg-red-100 text-red-700" : g.opportunity === "medium" ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>
                      {g.opportunity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
