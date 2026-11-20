"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { AlertTriangle, Info, CheckCircle2, Loader2 } from "lucide-react";

export default function AuditPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useQuery({ queryKey: ["audit", id], queryFn: () => api.getAudit(id) });

  if (isLoading) return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;

  if (!data || "message" in data) {
    return (
      <div className="max-w-3xl mx-auto bg-white rounded-xl border border-gray-200 p-8 text-center">
        <p className="text-gray-500">No audit results yet. Run a full analysis from the project page.</p>
      </div>
    );
  }

  const scoreColor = data.seo_score >= 70 ? "text-green-600" : data.seo_score >= 40 ? "text-yellow-600" : "text-red-600";

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Website Audit</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
          <div className={`text-5xl font-bold ${scoreColor}`}>{data.seo_score}</div>
          <div className="text-sm text-gray-500 mt-1">SEO Score</div>
          <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-2 bg-brand-600 rounded-full" style={{ width: `${data.seo_score}%` }} />
          </div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
          <div className="text-4xl font-bold text-red-500">{data.issues.critical?.length || 0}</div>
          <div className="text-sm text-gray-500 mt-1">Critical Issues</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
          <div className="text-4xl font-bold text-gray-700">{data.pages_crawled}</div>
          <div className="text-sm text-gray-500 mt-1">Pages Crawled</div>
        </div>
      </div>

      {data.recommendations?.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-3">AI Recommendations</h2>
          <ul className="space-y-2">
            {data.recommendations.map((rec: any, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle2 size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                {typeof rec === "string" ? rec : rec.recommendation || rec.text || JSON.stringify(rec)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {[
        { label: "Critical Issues", items: data.issues.critical, icon: AlertTriangle, color: "text-red-500" },
        { label: "Warnings", items: data.issues.warning, icon: AlertTriangle, color: "text-yellow-500" },
        { label: "Info", items: data.issues.info, icon: Info, color: "text-blue-500" },
      ].map(({ label, items, icon: Icon, color }) => items?.length > 0 && (
        <div key={label} className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Icon size={16} className={color} /> {label} ({items.length})
          </h2>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-gray-400 text-xs border-b"><th className="pb-2">Issue</th><th className="pb-2">URL</th></tr></thead>
            <tbody>
              {items.slice(0, 20).map((issue, i) => (
                <tr key={i} className="border-b border-gray-50 last:border-0">
                  <td className="py-2 text-gray-700">{issue.type?.replace(/_/g, " ")}</td>
                  <td className="py-2 text-gray-400 text-xs truncate max-w-xs">{issue.url || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
