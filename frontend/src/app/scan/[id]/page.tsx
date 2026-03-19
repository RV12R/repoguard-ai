"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { Loader2, Download, GitBranch, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { LiveLogs } from "@/components/live-logs";
import { RiskGauge } from "@/components/risk-gauge";
import { VulnerabilityCard } from "@/components/vulnerability-card";
import { api, type ScanResult } from "@/lib/api";
import { toast } from "sonner";

const statusLabels: Record<string, string> = {
  queued: "Queued",
  cloning: "Cloning Repository",
  analyzing: "Running Static Analysis",
  ai_review: "AI Deep Review",
  generating_report: "Generating Report",
  completed: "Scan Complete",
  failed: "Scan Failed",
};

// Demo data for when backend is not running
const demoScan: ScanResult = {
  id: "demo-001",
  repo_url: "https://github.com/example/vulnerable-app",
  status: "completed",
  risk_score: 72,
  summary:
    "Found 8 vulnerabilities across 12 files. 2 critical SQL injection flaws detected in auth module. AI review identified potential prompt injection risk in LLM integration layer.",
  created_at: new Date().toISOString(),
  completed_at: new Date().toISOString(),
  progress: 100,
  languages_detected: ["TypeScript", "Python", "Solidity"],
  vulnerabilities: [
    {
      id: "v1",
      title: "SQL Injection in User Authentication",
      severity: "critical",
      category: "Injection",
      description: "Unsanitized user input directly interpolated into SQL query string, allowing arbitrary SQL execution.",
      file_path: "src/auth/login.py",
      line_number: 42,
      code_snippet: 'query = f"SELECT * FROM users WHERE email=\'{email}\' AND password=\'{password}\'"',
      fix_suggestion: "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE email=%s AND password=%s', (email, password))",
      tool: "Semgrep",
    },
    {
      id: "v2",
      title: "Reentrancy Vulnerability in Withdraw Function",
      severity: "critical",
      category: "Web3",
      description: "External call made before state update, allowing recursive withdrawal of funds.",
      file_path: "contracts/Vault.sol",
      line_number: 87,
      code_snippet: "function withdraw(uint256 amount) external {\n    require(balances[msg.sender] >= amount);\n    (bool success, ) = msg.sender.call{value: amount}(\"\");\n    balances[msg.sender] -= amount;\n}",
      fix_suggestion: "Apply checks-effects-interactions pattern: update balances[msg.sender] before the external call.",
      tool: "AI-Review",
    },
    {
      id: "v3",
      title: "Hardcoded API Key in Source",
      severity: "high",
      category: "Secrets",
      description: "API key for third-party service is hardcoded in configuration file.",
      file_path: "config/settings.py",
      line_number: 15,
      code_snippet: 'API_KEY = "sk-abc123def456ghi789"',
      fix_suggestion: "Move to environment variable: API_KEY = os.environ.get('API_KEY')",
      tool: "Bandit",
    },
    {
      id: "v4",
      title: "Prompt Injection Risk in LLM Integration",
      severity: "high",
      category: "AI Risk",
      description: "User-controlled input passed directly to LLM prompt without sanitization, enabling prompt injection attacks.",
      file_path: "src/ai/assistant.py",
      line_number: 33,
      code_snippet: 'prompt = f"Analyze this code: {user_input}"',
      fix_suggestion: "Implement input sanitization and use system/user message separation in prompt construction.",
      tool: "AI-Review",
    },
    {
      id: "v5",
      title: "Missing Access Control on Admin Endpoint",
      severity: "medium",
      category: "Authorization",
      description: "Admin API endpoint lacks authentication middleware, allowing unauthenticated access.",
      file_path: "src/routes/admin.ts",
      line_number: 8,
      code_snippet: "router.get('/admin/users', async (req, res) => {\n  const users = await db.getAll();\n  res.json(users);\n});",
      fix_suggestion: "Add authentication middleware: router.get('/admin/users', authMiddleware, requireAdmin, ...)",
      tool: "Semgrep",
    },
    {
      id: "v6",
      title: "Insecure Random Number Generation",
      severity: "medium",
      category: "Cryptography",
      description: "Using Math.random() for security-sensitive operation instead of cryptographically secure RNG.",
      file_path: "src/utils/token.ts",
      line_number: 12,
      code_snippet: "const token = Math.random().toString(36).substring(2);",
      fix_suggestion: "Use crypto.randomBytes() or crypto.randomUUID() for security tokens.",
      tool: "Bandit",
    },
    {
      id: "v7",
      title: "Data Leakage in Error Response",
      severity: "low",
      category: "Information Disclosure",
      description: "Stack trace and internal error details exposed in API error responses.",
      file_path: "src/middleware/error.ts",
      line_number: 5,
      code_snippet: "res.status(500).json({ error: err.message, stack: err.stack });",
      fix_suggestion: "Return generic error messages in production: res.status(500).json({ error: 'Internal server error' })",
      tool: "AI-Review",
    },
    {
      id: "v8",
      title: "Outdated Dependency with Known CVE",
      severity: "low",
      category: "Dependencies",
      description: "Package 'lodash' version 4.17.15 has known prototype pollution vulnerability (CVE-2020-8203).",
      file_path: "package.json",
      line_number: 22,
      code_snippet: '"lodash": "^4.17.15"',
      fix_suggestion: "Update to lodash@4.17.21 or later: npm install lodash@latest",
      tool: "Semgrep",
    },
  ],
};

export default function ScanProgressPage() {
  const params = useParams();
  const scanId = params.id as string;
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [applyingFixes, setApplyingFixes] = useState(false);
  const isDemo = scanId === "demo";

  const connectWebSocket = useCallback(() => {
    if (isDemo) return;
    try {
      const ws = api.createWebSocket(scanId);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "log") {
          setLogs((prev) => [...prev, data.message]);
        }
        if (data.type === "progress") {
          setScan((prev) => prev ? { ...prev, progress: data.progress, status: data.status } : prev);
        }
        if (data.type === "result") {
          setScan(data.scan);
        }
      };
      ws.onerror = () => {
        setLogs((prev) => [...prev, "WebSocket connection failed — using polling fallback"]);
      };
      return () => ws.close();
    } catch {
      // WebSocket not available
    }
  }, [scanId, isDemo]);

  useEffect(() => {
    if (isDemo) {
      // Show demo with animated logs
      setLoading(false);
      const demoLogs = [
        "→ Starting scan for github.com/example/vulnerable-app",
        "→ Cloning repository...",
        "✓ Repository cloned (12 files, 3 languages detected)",
        "→ Running Semgrep analysis...",
        "  CRITICAL: SQL Injection found in src/auth/login.py:42",
        "  MEDIUM: Missing access control on src/routes/admin.ts:8",
        "  MEDIUM: Insecure RNG in src/utils/token.ts:12",
        "  LOW: Outdated dependency lodash@4.17.15",
        "✓ Semgrep complete — 4 findings",
        "→ Running Bandit analysis...",
        "  HIGH: Hardcoded API key in config/settings.py:15",
        "  MEDIUM: Insecure random in src/utils/token.ts:12",
        "✓ Bandit complete — 2 findings",
        "→ Running AI deep review (Groq LLM)...",
        "  CRITICAL: Reentrancy in contracts/Vault.sol:87",
        "  HIGH: Prompt injection risk in src/ai/assistant.py:33",
        "  LOW: Data leakage in error responses",
        "✓ AI review complete — 3 findings",
        "→ Generating PDF report...",
        "✓ Report generated — Risk Score: 72/100",
        "→ Cleaning up temporary files...",
        "✓ DONE — Scan complete. 8 vulnerabilities found.",
      ];
      let i = 0;
      const interval = setInterval(() => {
        if (i < demoLogs.length) {
          setLogs((prev) => [...prev, demoLogs[i]]);
          i++;
        } else {
          clearInterval(interval);
          setScan(demoScan);
        }
      }, 300);
      return () => clearInterval(interval);
    }

    // Real scan
    const fetchScan = async () => {
      try {
        const result = await api.getScan(scanId);
        setScan(result);
        setLoading(false);
      } catch {
        toast.error("Failed to load scan");
        setLoading(false);
      }
    };
    fetchScan();
    const cleanup = connectWebSocket();

    // Polling fallback
    const poll = setInterval(async () => {
      try {
        const result = await api.getScan(scanId);
        setScan(result);
        if (result.status === "completed" || result.status === "failed") {
          clearInterval(poll);
        }
      } catch { /* ignore */ }
    }, 3000);

    return () => {
      clearInterval(poll);
      cleanup?.();
    };
  }, [scanId, isDemo, connectWebSocket]);

  const handleApplyFixes = async () => {
    const token = prompt("Enter your GitHub token to create fix branch:");
    if (!token) return;
    setApplyingFixes(true);
    try {
      const result = await api.applyFixes(scanId, token);
      toast.success(`Fix branch created: ${result.branch}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to apply fixes");
    } finally {
      setApplyingFixes(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const isRunning = scan && !["completed", "failed"].includes(scan.status);
  const isComplete = scan?.status === "completed";

  // Count by severity
  const severityCounts = scan?.vulnerabilities?.reduce(
    (acc, v) => {
      acc[v.severity] = (acc[v.severity] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  ) ?? {};

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {/* Back link */}
      <Link
        href="/dashboard"
        className="inline-flex items-center gap-1 text-xs font-mono text-muted-foreground hover:text-foreground transition-colors mb-6"
      >
        <ArrowLeft className="h-3 w-3" /> Dashboard
      </Link>

      {/* Header */}
      <div className="mb-6 animate-fade-in">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-xl font-mono font-bold mb-1">
              Scan {isDemo ? "Demo" : `#${scanId.slice(0, 8)}`}
            </h1>
            <p className="font-mono text-xs text-muted-foreground truncate max-w-md">
              {scan?.repo_url ?? "Loading..."}
            </p>
          </div>
          <Badge
            variant="outline"
            className={`font-mono text-[10px] ${
              isComplete
                ? "text-green-500 border-green-500/30"
                : scan?.status === "failed"
                ? "text-red-500 border-red-500/30"
                : "text-yellow-500 border-yellow-500/30 animate-pulse-slow"
            }`}
          >
            {statusLabels[scan?.status ?? "queued"]}
          </Badge>
        </div>
      </div>

      {/* Progress */}
      {(isRunning || !scan) && (
        <div className="mb-6 animate-fade-in">
          <div className="flex justify-between text-xs font-mono text-muted-foreground mb-2">
            <span>{statusLabels[scan?.status ?? "queued"]}</span>
            <span>{scan?.progress ?? 0}%</span>
          </div>
          <Progress value={scan?.progress ?? 0} className="h-1" />
        </div>
      )}

      {/* Live Logs */}
      <div className="mb-8 animate-fade-in">
        <LiveLogs logs={logs} />
      </div>

      {/* Results section — shown when complete */}
      {isComplete && scan && (
        <div className="space-y-8 animate-fade-in">
          <Separator />

          {/* Result header with gauge */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Risk gauge */}
            <Card className="border-border/50 flex items-center justify-center py-6">
              <RiskGauge score={scan.risk_score} />
            </Card>

            {/* Summary */}
            <Card className="border-border/50 col-span-1 md:col-span-2">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-mono">Executive Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {scan.summary}
                </p>
                <div className="flex flex-wrap gap-2">
                  {scan.languages_detected?.map((lang) => (
                    <Badge key={lang} variant="outline" className="font-mono text-[10px]">
                      {lang}
                    </Badge>
                  ))}
                </div>

                {/* Severity breakdown */}
                <div className="flex items-center gap-3 text-xs font-mono">
                  {severityCounts.critical && (
                    <span className="text-red-500">{severityCounts.critical} Critical</span>
                  )}
                  {severityCounts.high && (
                    <span className="text-orange-500">{severityCounts.high} High</span>
                  )}
                  {severityCounts.medium && (
                    <span className="text-yellow-500">{severityCounts.medium} Medium</span>
                  )}
                  {severityCounts.low && (
                    <span className="text-blue-500">{severityCounts.low} Low</span>
                  )}
                  {severityCounts.info && (
                    <span className="text-muted-foreground">{severityCounts.info} Info</span>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              className="font-mono gap-2 text-xs"
              onClick={() => window.open(api.getReportUrl(scanId), "_blank")}
            >
              <Download className="h-3.5 w-3.5" />
              Download PDF Report
            </Button>
            <Button
              variant="outline"
              className="font-mono gap-2 text-xs"
              onClick={handleApplyFixes}
              disabled={applyingFixes}
            >
              {applyingFixes ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <GitBranch className="h-3.5 w-3.5" />
              )}
              Apply Fixes &amp; Create Branch
            </Button>
          </div>

          {/* Vulnerabilities list */}
          <div>
            <h2 className="text-sm font-mono font-bold mb-4">
              Vulnerabilities ({scan.vulnerabilities?.length ?? 0})
            </h2>
            <div className="space-y-3">
              {scan.vulnerabilities?.map((vuln, i) => (
                <VulnerabilityCard key={vuln.id} vuln={vuln} index={i} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
