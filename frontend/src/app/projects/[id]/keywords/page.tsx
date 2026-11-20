"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, Star } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function KeywordsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: keywords = [], isLoading } = useQuery({ queryKey: ["keywords", id], queryFn: () => api.getKeywords(id) });

  if (isLoading) return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;

  const chartData = keywords.slice(0, 10).map((k) => ({ name: k.keyword.slice(0, 20), volume: k.search_volume || 0 }));
  const quickWins = keywords.filter((k) => k.is_quick_win);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Keyword Research</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
          <div className="text-3xl font-bold text-brand-600">{keywords.length}</div>
          <div className="text-sm text-gray-500">Total Keywords</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
          <div className="text-3xl font-bold text-green-600">{quickWins.length}</div>
          <div className="text-sm text-gray-500">Quick Wins</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
          <div className="text-3xl font-bold text-purple-600">{new Set(keywords.map((k) => k.cluster).filter(Boolean)).size}</div>
          <div className="text-sm text-gray-500">Keyword Clusters</div>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Search Volume — Top 10</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="volume" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="font-semibold text-gray-900 mb-3">All Keywords</h2>
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs text-gray-400 border-b"><th className="pb-2">Keyword</th><th className="pb-2">Volume</th><th className="pb-2">Difficulty</th><th className="pb-2">Cluster</th><th className="pb-2"></th></tr></thead>
          <tbody>
            {keywords.map((kw) => (
              <tr key={kw.id} className="border-b border-gray-50 last:border-0">
                <td className="py-2 font-medium text-gray-800">{kw.keyword}</td>
                <td className="py-2 text-gray-600">{kw.search_volume ?? "—"}</td>
                <td className="py-2">
                  {kw.difficulty != null && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${kw.difficulty < 40 ? "bg-green-100 text-green-700" : kw.difficulty < 65 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"}`}>
                      {kw.difficulty}
                    </span>
                  )}
                </td>
                <td className="py-2 text-xs text-gray-500">{kw.cluster || "—"}</td>
                <td className="py-2">{kw.is_quick_win && <Star size={14} className="text-yellow-500" />}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
