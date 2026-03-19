"use client";

import { useEffect, useRef } from "react";

interface LiveLogsProps {
  logs: string[];
}

export function LiveLogs({ logs }: LiveLogsProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="relative rounded-md border border-border bg-black text-green-400 font-mono text-xs overflow-hidden">
      {/* Terminal header */}
      <div className="flex items-center gap-1.5 px-3 py-2 border-b border-border/50 bg-muted/10">
        <div className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
        <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
        <div className="h-2.5 w-2.5 rounded-full bg-green-500/80" />
        <span className="ml-2 text-muted-foreground text-[10px]">scan.log</span>
      </div>

      {/* Log output */}
      <div className="h-52 overflow-y-auto p-3 space-y-0.5">
        {logs.length === 0 && (
          <span className="text-muted-foreground animate-pulse">
            Waiting for scan to start...
          </span>
        )}
        {logs.map((log, i) => (
          <div key={i} className="flex gap-2">
            <span className="text-muted-foreground/50 select-none shrink-0">
              {String(i + 1).padStart(3, "0")}
            </span>
            <span
              className={
                log.includes("ERROR") || log.includes("CRITICAL")
                  ? "text-red-400"
                  : log.includes("WARN") || log.includes("HIGH")
                  ? "text-yellow-400"
                  : log.includes("✓") || log.includes("DONE") || log.includes("SAFE")
                  ? "text-green-400"
                  : "text-foreground/70"
              }
            >
              {log}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
