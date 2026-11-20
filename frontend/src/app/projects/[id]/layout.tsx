"use client";
import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ArrowLeft, ChevronRight } from "lucide-react";

const agentLabels: Record<string, string> = {
  audit: "Website Audit",
  keywords: "Keywords",
  competitors: "Competitors",
  gbp: "GBP Optimization",
  content: "Content",
  links: "Link Building",
  reports: "Reports",
  usage: "Usage & Cost",
};

export default function ProjectLayout({ children }: { children: React.ReactNode }) {
  const { id } = useParams<{ id: string }>();
  const pathname = usePathname();

  const { data: project } = useQuery({
    queryKey: ["project", id],
    queryFn: () => api.getProject(id),
  });

  // Detect which sub-page we're on
  const segments = pathname.split("/").filter(Boolean);
  const agentSlug = segments.length > 2 ? segments[segments.length - 1] : null;
  const isSubPage = !!agentSlug && agentSlug !== id;
  const agentLabel = agentSlug ? agentLabels[agentSlug] : null;

  return (
    <div>
      {/* Breadcrumb — only on sub-pages */}
      {isSubPage && (
        <div className="max-w-4xl mx-auto mb-5">
          <div className="flex items-center gap-1.5 text-sm text-gray-400">
            <Link href="/projects" className="hover:text-gray-600 transition-colors">
              Projects
            </Link>
            <ChevronRight size={13} />
            <Link
              href={`/projects/${id}`}
              className="hover:text-gray-600 transition-colors font-medium text-gray-600 truncate max-w-[160px]"
            >
              {project?.name ?? "..."}
            </Link>
            <ChevronRight size={13} />
            <span className="text-brand-600 font-semibold">{agentLabel ?? agentSlug}</span>
          </div>

          <Link
            href={`/projects/${id}`}
            className="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-brand-600 transition-colors mt-1.5 group"
          >
            <ArrowLeft size={13} className="group-hover:-translate-x-0.5 transition-transform" />
            Back to Project
          </Link>
        </div>
      )}
      {children}
    </div>
  );
}
