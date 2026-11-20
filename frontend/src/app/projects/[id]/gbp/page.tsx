"use client";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, CheckCircle2, Circle } from "lucide-react";

export default function GBPPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const { data: suggestions = [], isLoading } = useQuery({ queryKey: ["gbp", id], queryFn: () => api.getGBPSuggestions(id) });

  const update = useMutation({
    mutationFn: ({ sid, status }: { sid: string; status: string }) =>
      fetch(`/api/v1/projects/${id}/gbp/${sid}/status?status=${status}`, { method: "PUT" }).then((r) => r.json()),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["gbp", id] }),
  });

  const done = suggestions.filter((s) => s.status === "implemented").length;
  const pct = suggestions.length ? Math.round((done / suggestions.length) * 100) : 0;

  if (isLoading) return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">GBP Optimization</h1>

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Progress: {done}/{suggestions.length} completed</span>
          <span className="text-sm font-bold text-brand-600">{pct}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-2 bg-brand-600 rounded-full transition-all" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {["high", "medium", "low"].map((priority) => {
        const items = suggestions.filter((s) => s.priority === priority);
        if (!items.length) return null;
        return (
          <div key={priority} className="bg-white border border-gray-200 rounded-xl p-5">
            <h2 className="font-semibold text-gray-900 mb-3 capitalize">
              <span className={`text-xs px-2 py-0.5 rounded-full mr-2 ${priority === "high" ? "bg-red-100 text-red-700" : priority === "medium" ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>
                {priority}
              </span>
              Priority
            </h2>
            <ul className="space-y-3">
              {items.map((s) => (
                <li key={s.id} className="flex items-start gap-3">
                  <button onClick={() => update.mutate({ sid: s.id, status: s.status === "implemented" ? "pending" : "implemented" })}>
                    {s.status === "implemented" ? <CheckCircle2 size={20} className="text-green-500 flex-shrink-0" /> : <Circle size={20} className="text-gray-300 flex-shrink-0" />}
                  </button>
                  <div>
                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded mr-2">{s.category}</span>
                    <span className={`text-sm ${s.status === "implemented" ? "line-through text-gray-400" : "text-gray-700"}`}>{s.suggestion}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        );
      })}

      {suggestions.length === 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-8 text-center text-gray-400">
          No GBP suggestions yet. Run analysis first.
        </div>
      )}
    </div>
  );
}
