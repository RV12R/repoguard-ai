import Link from "next/link";
import { Shield, ArrowRight, Scan, FileText, GitBranch, Zap, Lock, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="relative">
      {/* Scan line effect */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden z-0">
        <div className="animate-scanline absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-foreground/5 to-transparent" />
      </div>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-6xl px-4 pt-24 pb-20">
        <div className="flex flex-col items-center text-center gap-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 border border-border/60 rounded-full px-3 py-1 text-xs font-mono text-muted-foreground">
            <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
            Autonomous security scanning
          </div>

          {/* Title */}
          <h1 className="max-w-3xl text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight font-mono">
            Find vulnerabilities
            <br />
            <span className="text-muted-foreground">before they find you</span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-xl text-sm sm:text-base text-muted-foreground leading-relaxed">
            Paste a GitHub URL. RepoGuard AI clones, analyzes with Semgrep + Bandit,
            runs AI deep-scan for bugs, vulnerabilities, and Web3 issues, then
            generates a professional PDF report with one-click fixes.
          </p>

          {/* CTA */}
          <div className="flex items-center gap-3 mt-2">
            <Link href="/scan/new">
              <Button className="font-mono gap-2 px-6 h-10">
                Start Scanning <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" className="font-mono gap-2 px-6 h-10">
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>

        {/* ASCII art separator */}
        <div className="mt-20 text-center font-mono text-xs text-muted-foreground/30 select-none overflow-hidden">
          ════════════════════════════════════════════════════════
        </div>

        {/* Features grid */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            {
              icon: Scan,
              title: "Static Analysis",
              desc: "Semgrep + Bandit rules scan for known vulnerability patterns across all major languages.",
            },
            {
              icon: Eye,
              title: "AI Deep Review",
              desc: "LLM-powered analysis detects logic bugs, AI risks (prompt injection, data leakage), and Web3 issues.",
            },
            {
              icon: FileText,
              title: "PDF Reports",
              desc: "Professional reports with risk scores, severity rankings, code snippets, and executive summaries.",
            },
            {
              icon: GitBranch,
              title: "Auto-Fix Deploy",
              desc: "One-click creates a new branch with AI-generated patches applied to your repository.",
            },
            {
              icon: Lock,
              title: "Zero Persistence",
              desc: "Code is cloned to temp storage and auto-deleted after scan. Nothing is ever stored permanently.",
            },
            {
              icon: Zap,
              title: "Live Tracking",
              desc: "Real-time progress bar and terminal log stream. Watch every step of the analysis live.",
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="group border border-border/40 rounded-md p-5 hover:border-border transition-colors"
            >
              <feature.icon className="h-5 w-5 mb-3 text-muted-foreground group-hover:text-foreground transition-colors" />
              <h3 className="font-mono text-sm font-semibold mb-1">
                {feature.title}
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-20 text-center">
          <p className="font-mono text-xs text-muted-foreground mb-4">
            Used by security researchers &amp; audit teams
          </p>
          <div className="flex items-center justify-center gap-6 text-muted-foreground/40 font-mono text-xs">
            <a href="https://rekt.news" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
              rekt.news
            </a>
            <span>·</span>
            <span>Open Source</span>
            <span>·</span>
            <span>Free Tier</span>
          </div>
        </div>
      </section>
    </div>
  );
}
