const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ScanRequest {
  repo_url: string;
  github_token?: string;
}

export interface Vulnerability {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  category: string;
  description: string;
  file_path: string;
  line_number?: number;
  code_snippet?: string;
  fix_suggestion?: string;
  tool: string;
}

export interface ScanResult {
  id: string;
  repo_url: string;
  status: "queued" | "cloning" | "analyzing" | "ai_review" | "generating_report" | "completed" | "failed";
  risk_score: number;
  vulnerabilities: Vulnerability[];
  summary: string;
  created_at: string;
  completed_at?: string;
  report_url?: string;
  progress: number;
  languages_detected: string[];
}

export interface ScanHistoryItem {
  id: string;
  repo_url: string;
  status: string;
  risk_score: number;
  vulnerability_count: number;
  created_at: string;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  startScan: (data: ScanRequest) =>
    apiFetch<ScanResult>("/api/scan", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getScan: (id: string) => apiFetch<ScanResult>(`/api/scan/${id}`),

  getHistory: () => apiFetch<ScanHistoryItem[]>("/api/scans"),

  getReportUrl: (id: string) => `${API_BASE}/api/scan/${id}/report`,

  applyFixes: (scanId: string, token: string) =>
    apiFetch<{ branch: string; pr_url: string }>(`/api/fix/${scanId}`, {
      method: "POST",
      body: JSON.stringify({ github_token: token }),
    }),

  createWebSocket: (scanId: string) => {
    const wsBase = API_BASE.replace(/^http/, "ws");
    return new WebSocket(`${wsBase}/ws/scan/${scanId}`);
  },
};
