"use client";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  LayoutDashboard, FolderOpen, Globe, Search, Users,
  MapPin, FileText, Link2, BarChart3, Activity, ChevronRight
} from "lucide-react";

const nav = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Projects", href: "/projects", icon: FolderOpen },
  { label: "Usage & Cost", href: "/usage", icon: Activity },
];

const agentNav = [
  { label: "Website Audit", href: "audit", icon: Globe },
  { label: "Keywords", href: "keywords", icon: Search },
  { label: "Competitors", href: "competitors", icon: Users },
  { label: "GBP", href: "gbp", icon: MapPin },
  { label: "Content", href: "content", icon: FileText },
  { label: "Link Building", href: "links", icon: Link2 },
  { label: "Reports", href: "reports", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  const projectMatch = pathname.match(/^\/projects\/([^/]+)/);
  const currentProjectId = projectMatch?.[1];

  const { data: project } = useQuery({
    queryKey: ["project", currentProjectId],
    queryFn: () => api.getProject(currentProjectId!),
    enabled: !!currentProjectId,
  });

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-5 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <Image
            src="/logo.svg"
            alt="SEO Automation Bot"
            width={40}
            height={40}
            className="rounded-lg object-contain"
          />
          <div>
            <div className="font-bold text-gray-900 text-sm">SEO Automation</div>
            <div className="text-xs text-gray-500">SEO Bot</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {nav.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              pathname === item.href
                ? "bg-brand-50 text-brand-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <item.icon size={16} />
            {item.label}
          </Link>
        ))}

        {currentProjectId && (
          <>
            <div className="pt-4 pb-1">
              <div className="px-3 py-1.5 bg-gray-50 rounded-lg">
                <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-0.5">
                  Current Project
                </div>
                <Link
                  href={`/projects/${currentProjectId}`}
                  className="flex items-center gap-1 text-sm font-semibold text-brand-700 hover:text-brand-900 truncate"
                >
                  {project?.name ?? "Loading..."}
                  <ChevronRight size={12} className="flex-shrink-0" />
                </Link>
                {project?.website_url && (
                  <div className="text-xs text-gray-400 truncate mt-0.5">{project.website_url}</div>
                )}
              </div>
            </div>

            <div className="pb-1 px-3 pt-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Agents
            </div>
            {agentNav.map((item) => {
              const href = `/projects/${currentProjectId}/${item.href}`;
              const isActive = pathname === href;
              return (
                <Link
                  key={item.href}
                  href={href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-brand-50 text-brand-600"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <item.icon size={16} />
                  {item.label}
                </Link>
              );
            })}

            <div className="pt-2">
              <Link
                href={`/projects/${currentProjectId}/usage`}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  pathname === `/projects/${currentProjectId}/usage`
                    ? "bg-brand-50 text-brand-600"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Activity size={16} />
                Project Usage
              </Link>
            </div>
          </>
        )}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-center text-gray-400 leading-relaxed">
          <div>Part of BRIHA</div>
          <div>MIT License</div>
        </div>
      </div>
    </aside>
  );
}
