import Link from "next/link";
import Image from "next/image";
import { ArrowRight, Globe, Search, Users, MapPin, FileText, Link2, BarChart3 } from "lucide-react";

const agents = [
  { icon: Globe, label: "Website Audit", desc: "Crawl & score your SEO health", color: "bg-blue-100 text-blue-600" },
  { icon: Search, label: "Keyword Research", desc: "Find local Pakistani keywords", color: "bg-purple-100 text-purple-600" },
  { icon: Users, label: "Competitor Analysis", desc: "Uncover content gaps", color: "bg-orange-100 text-orange-600" },
  { icon: MapPin, label: "GBP Optimization", desc: "Google Business Profile tips", color: "bg-green-100 text-green-600" },
  { icon: FileText, label: "Content Agent", desc: "AI-written blog posts & pages", color: "bg-pink-100 text-pink-600" },
  { icon: Link2, label: "Link Building", desc: "Directory & backlink opportunities", color: "bg-yellow-100 text-yellow-600" },
  { icon: BarChart3, label: "Monthly Report", desc: "Professional PDF reports", color: "bg-indigo-100 text-indigo-600" },
];

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center py-12">
        <div className="flex justify-center mb-6">
          <Image src="/logo.svg" alt="SEO Automation Bot" width={80} height={80} className="rounded-2xl object-contain" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">SEO Automation Bot</h1>
        <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
          Enter your domain — 7 AI agents automatically audit your site, research keywords,
          analyze competitors, and generate a full SEO strategy.
        </p>
        <Link
          href="/projects"
          className="inline-flex items-center gap-2 bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-colors"
        >
          Get Started <ArrowRight size={18} />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
        {agents.map((agent) => (
          <div key={agent.label} className="bg-white rounded-xl p-5 border border-gray-200 hover:shadow-md transition-shadow">
            <div className={`inline-flex p-2 rounded-lg ${agent.color} mb-3`}>
              <agent.icon size={20} />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">{agent.label}</h3>
            <p className="text-sm text-gray-500">{agent.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
