"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, ExternalLink } from "lucide-react";

export default function LinksPage() {
  const { id } = useParams<{ id: string }>();
  const { data: links = [], isLoading } = useQuery({ queryKey: ["links", id], queryFn: () => api.getLinks(id) });

  if (isLoading) return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Link Building Opportunities</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
          <div className="text-3xl font-bold text-brand-600">{links.length}</div>
          <div className="text-sm text-gray-500">Total Opportunities</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
          <div className="text-3xl font-bold text-green-600">{links.filter((l) => l.submission_type === "free").length}</div>
          <div className="text-sm text-gray-500">Free Submissions</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
          <div className="text-3xl font-bold text-purple-600">{links.filter((l) => l.submission_status === "submitted").length}</div>
          <div className="text-sm text-gray-500">Submitted</div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs text-gray-400 border-b"><th className="pb-2">Directory</th><th className="pb-2">Relevance</th><th className="pb-2">Est. DA</th><th className="pb-2">Type</th><th className="pb-2">Status</th></tr></thead>
          <tbody>
            {links.map((l) => (
              <tr key={l.id} className="border-b border-gray-50 last:border-0">
                <td className="py-2">
                  <a href={l.directory_url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline flex items-center gap-1">
                    {l.directory_name} <ExternalLink size={12} />
                  </a>
                </td>
                <td className="py-2">
                  <div className="flex items-center gap-1">
                    <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-1.5 bg-brand-500 rounded-full" style={{ width: `${l.relevance_score}%` }} />
                    </div>
                    <span className="text-gray-500">{l.relevance_score}</span>
                  </div>
                </td>
                <td className="py-2 text-gray-600">{l.estimated_da}</td>
                <td className="py-2"><span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{l.submission_type}</span></td>
                <td className="py-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${l.submission_status === "submitted" ? "bg-green-100 text-green-700" : l.submission_status === "approved" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-500"}`}>
                    {l.submission_status.replace(/_/g, " ")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {links.length === 0 && <p className="text-center text-gray-400 py-6 text-sm">No link opportunities yet. Run analysis first.</p>}
      </div>
    </div>
  );
}
