"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, FileText, Eye, EyeOff } from "lucide-react";

export default function ContentPage() {
  const { id } = useParams<{ id: string }>();
  const { data: content = [], isLoading } = useQuery({ queryKey: ["content", id], queryFn: () => api.getContent(id) });
  const [selected, setSelected] = useState<string | null>(null);

  const { data: detail, isLoading: detailLoading } = useQuery({
    queryKey: ["content-detail", id, selected],
    queryFn: () => api.getContentDetail(id, selected!),
    enabled: !!selected,
  });

  if (isLoading) return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Generated Content</h1>

      {content.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-xl p-8 text-center text-gray-400">
          <FileText size={40} className="mx-auto mb-3 text-gray-200" />
          No content generated yet. Run analysis first.
        </div>
      ) : (
        <div className="grid gap-4">
          {content.map((item) => (
            <div key={item.id} className="bg-white border border-gray-200 rounded-xl p-5 flex items-center justify-between">
              <div>
                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded mr-2">{item.content_type.replace(/_/g, " ")}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${item.status === "approved" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>{item.status}</span>
                <h3 className="font-medium text-gray-900 mt-2">{item.title}</h3>
                <p className="text-xs text-gray-500 mt-1">{item.word_count} words • SEO score: {item.seo_score}/100 {item.target_keyword && `• Target: "${item.target_keyword}"`}</p>
              </div>
              <button onClick={() => setSelected(selected === item.id ? null : item.id)} className="flex items-center gap-1.5 text-sm text-brand-600 hover:text-brand-700 font-medium">
                {selected === item.id ? <EyeOff size={15} /> : <Eye size={15} />}
                {selected === item.id ? "Close" : "Preview"}
              </button>
            </div>
          ))}
        </div>
      )}

      {selected && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          {detailLoading ? (
            <div className="flex justify-center py-8"><Loader2 className="animate-spin text-gray-400" /></div>
          ) : detail?.content ? (
            <>
              <h2 className="font-semibold text-gray-900 mb-4">{detail.title}</h2>
              <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                {detail.content}
              </div>
            </>
          ) : (
            <p className="text-gray-400 text-sm text-center py-4">Could not load content.</p>
          )}
        </div>
      )}
    </div>
  );
}
