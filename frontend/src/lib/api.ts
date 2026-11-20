const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  // Projects
  getProjects: () => request<Project[]>("/api/v1/projects"),
  getProject: (id: string) => request<Project>(`/api/v1/projects/${id}`),
  createProject: (data: CreateProjectInput) =>
    request<Project>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
  deleteProject: (id: string) => request<void>(`/api/v1/projects/${id}`, { method: "DELETE" }),
  runAnalysis: (id: string) =>
    request<RunResponse>(`/api/v1/projects/${id}/run`, { method: "POST", body: JSON.stringify({}) }),

  // Results
  getAudit: (id: string) => request<AuditResult>(`/api/v1/projects/${id}/audit`),
  getKeywords: (id: string) => request<Keyword[]>(`/api/v1/projects/${id}/keywords`),
  getCompetitors: (id: string) => request<Competitor[]>(`/api/v1/projects/${id}/competitors`),
  getContentGaps: (id: string) => request<{ content_gaps: ContentGap[] }>(`/api/v1/projects/${id}/competitors/gaps`),
  getGBPSuggestions: (id: string) => request<GBPSuggestion[]>(`/api/v1/projects/${id}/gbp/suggestions`),
  getContent: (id: string) => request<ContentItem[]>(`/api/v1/projects/${id}/content`),
  getContentDetail: (projectId: string, contentId: string) =>
    request<ContentDetail>(`/api/v1/projects/${projectId}/content/${contentId}`),
  getLinks: (id: string) => request<LinkOpportunity[]>(`/api/v1/projects/${id}/links`),
  getReports: (id: string) => request<Report[]>(`/api/v1/projects/${id}/reports`),
  getRuns: (id: string) => request<AgentRun[]>(`/api/v1/projects/${id}/runs`),
  stopAnalysis: (projectId: string, runId: string) =>
    request<{ message: string }>(`/api/v1/projects/${projectId}/runs/${runId}/stop`, { method: "POST" }),
  getUsage: (id: string) => request<UsageSummary>(`/api/v1/projects/${id}/usage`),
};

// Types
export interface Project {
  id: string;
  name: string;
  website_url: string;
  business_type: string | null;
  location: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectInput {
  name: string;
  website_url: string;
  business_type?: string;
  location?: string;
}

export interface RunResponse {
  run_id: string;
  project_id: string;
  status: string;
  message: string;
}

export interface AuditResult {
  seo_score: number;
  pages_crawled: number;
  issues: { critical: Issue[]; warning: Issue[]; info: Issue[] };
  recommendations: string[];
}

export interface Issue {
  type: string;
  severity: string;
  url?: string;
  count?: number;
  length?: number;
}

export interface Keyword {
  id: string;
  keyword: string;
  search_volume: number | null;
  difficulty: number | null;
  type: string | null;
  cluster: string | null;
  is_quick_win: boolean;
}

export interface Competitor {
  id: string;
  competitor_url: string;
  competitor_name: string | null;
  rank_position: number | null;
  top_keywords: string[];
  content_gaps: ContentGap[];
}

export interface ContentGap {
  keyword: string;
  competitors_with_it: number;
  opportunity: "high" | "medium" | "low";
}

export interface GBPSuggestion {
  id: string;
  category: string;
  suggestion: string;
  priority: "high" | "medium" | "low";
  status: string;
}

export interface ContentItem {
  id: string;
  title: string;
  content_type: string;
  target_keyword: string | null;
  word_count: number;
  seo_score: number;
  status: string;
}

export interface ContentDetail extends ContentItem {
  content: string;
  project_id: string;
  created_at: string;
}

export interface LinkOpportunity {
  id: string;
  directory_name: string;
  directory_url: string;
  category: string | null;
  relevance_score: number;
  estimated_da: number;
  submission_type: string;
  submission_status: string;
}

export interface Report {
  id: string;
  report_month: string;
  report_type: string;
  pdf_path: string | null;
  generated_at: string;
}

export interface AgentRun {
  id: string;
  agent_type: string;
  status: string;
  progress: number;
  message: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface UsageSummary {
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  total_ai_cost_usd: number;
  total_serp_calls: number;
  total_serp_cost_usd: number;
  total_cost_usd: number;
  by_agent: Record<string, { input_tokens: number; output_tokens: number; cost_usd: number; calls: number }>;
  logs: Array<{
    agent: string;
    model: string;
    input_tokens: number;
    output_tokens: number;
    ai_cost_usd: number;
    serp_calls: number;
    serp_cost_usd: number;
    timestamp: string;
  }>;
}
