"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Shield,
  ArrowRight,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { ScanHistoryItem } from "@/lib/api";

// Demo history data — used when backend is not running
const demoHistory: ScanHistoryItem[] = [
  {
    id: "demo",
    repo_url: "https://github.com/example/vulnerable-app",
    status: "completed",
    risk_score: 72,
    vulnerability_count: 8,
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "demo-2",
    repo_url: "https://github.com/defi-protocol/smart-contracts",
    status: "completed",
    risk_score: 85,
    vulnerability_count: 12,
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "demo-3",
    repo_url: "https://github.com/startup/api-server",
    status: "completed",
    risk_score: 34,
    vulnerability_count: 3,
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
];

function getRiskColor(score: number) {
  if (score >= 80) return "text-red-500";
  if (score >= 60) return "text-orange-500";
  if (score >= 40) return "text-yellow-500";
  return "text-green-500";
}

function getStatusIcon(status: string) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />;
    case "failed":
      return <XCircle className="h-3.5 w-3.5 text-red-500" />;
    default:
      return <Clock className="h-3.5 w-3.5 text-yellow-500 animate-pulse" />;
  }
}

function timeAgo(dateStr: string) {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function DashboardPage() {
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Try fetching from API, fall back to demo data
    async function loadHistory() {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/scans`
        );
        if (res.ok) {
          const data = await res.json();
          setHistory(data);
        } else {
          setHistory(demoHistory);
        }
      } catch {
        setHistory(demoHistory);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 animate-fade-in">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Shield className="h-5 w-5" />
            <h1 className="text-2xl font-mono font-bold">Dashboard</h1>
          </div>
          <p className="text-sm text-muted-foreground font-mono">
            Recent scans and security reports
          </p>
        </div>
        <Link href="/scan/new">
          <Button className="font-mono gap-2 text-xs h-9">
            <Plus className="h-3.5 w-3.5" /> New Scan
          </Button>
        </Link>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-3 mb-8 animate-fade-in">
        <Card className="border-border/50">
          <CardContent className="pt-4 pb-3 px-4">
            <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider mb-1">
              Total Scans
            </p>
            <p className="text-2xl font-mono font-bold">{history.length}</p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="pt-4 pb-3 px-4">
            <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider mb-1">
              Total Vulns
            </p>
            <p className="text-2xl font-mono font-bold">
              {history.reduce((sum, s) => sum + s.vulnerability_count, 0)}
            </p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardContent className="pt-4 pb-3 px-4">
            <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider mb-1">
              Avg Risk
            </p>
            <p className="text-2xl font-mono font-bold">
              {history.length > 0
                ? Math.round(
                    history.reduce((sum, s) => sum + s.risk_score, 0) / history.length
                  )
                : 0}
            </p>
          </CardContent>
        </Card>
      </div>

      <Separator className="mb-6" />

      {/* Scan list */}
      <div className="space-y-2 animate-fade-in">
        {loading ? (
          <div className="text-center py-12 text-sm font-mono text-muted-foreground">
            Loading scans...
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-12">
            <AlertTriangle className="h-8 w-8 mx-auto text-muted-foreground/30 mb-3" />
            <p className="text-sm font-mono text-muted-foreground mb-4">
              No scans yet
            </p>
            <Link href="/scan/new">
              <Button variant="outline" className="font-mono text-xs gap-2">
                Start your first scan <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </div>
        ) : (
          history.map((scan) => (
            <Link key={scan.id} href={`/scan/${scan.id}`}>
              <Card className="border-border/40 hover:border-border transition-colors cursor-pointer group">
                <CardContent className="flex items-center justify-between py-3 px-4 gap-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    {getStatusIcon(scan.status)}
                    <div className="min-w-0">
                      <p className="text-sm font-mono truncate group-hover:text-foreground transition-colors">
                        {scan.repo_url.replace("https://github.com/", "")}
                      </p>
                      <p className="text-[10px] font-mono text-muted-foreground">
                        {timeAgo(scan.created_at)} · {scan.vulnerability_count} findings
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className={`font-mono text-sm font-bold ${getRiskColor(scan.risk_score)}`}>
                      {scan.risk_score}
                    </span>
                    <Badge variant="outline" className="font-mono text-[10px]">
                      {scan.status}
                    </Badge>
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
