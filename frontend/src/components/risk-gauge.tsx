"use client";

import { useEffect, useState } from "react";

interface RiskGaugeProps {
  score: number;
  size?: number;
}

export function RiskGauge({ score, size = 160 }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const radius = (size - 20) / 2;
  const circumference = Math.PI * radius;
  const progress = (animatedScore / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 80) return "var(--destructive)";
    if (s >= 60) return "oklch(0.75 0.18 55)"; // orange
    if (s >= 40) return "oklch(0.80 0.15 85)"; // yellow
    return "oklch(0.72 0.19 149)"; // green
  };

  const getLabel = (s: number) => {
    if (s >= 80) return "CRITICAL";
    if (s >= 60) return "HIGH";
    if (s >= 40) return "MEDIUM";
    if (s >= 20) return "LOW";
    return "SAFE";
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        {/* Background arc */}
        <path
          d={`M 10 ${size / 2 + 10} A ${radius} ${radius} 0 0 1 ${size - 10} ${size / 2 + 10}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-muted/30"
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <path
          d={`M 10 ${size / 2 + 10} A ${radius} ${radius} 0 0 1 ${size - 10} ${size / 2 + 10}`}
          fill="none"
          stroke={getColor(animatedScore)}
          strokeWidth="8"
          strokeDasharray={`${progress} ${circumference}`}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
        {/* Score text */}
        <text
          x={size / 2}
          y={size / 2 - 5}
          textAnchor="middle"
          className="fill-foreground font-mono text-3xl font-bold"
          style={{ fontSize: size / 4.5 }}
        >
          {animatedScore}
        </text>
        <text
          x={size / 2}
          y={size / 2 + 15}
          textAnchor="middle"
          className="fill-muted-foreground font-mono"
          style={{ fontSize: size / 14 }}
        >
          / 100
        </text>
      </svg>
      <span
        className="font-mono text-xs font-bold tracking-widest"
        style={{ color: getColor(animatedScore) }}
      >
        {getLabel(animatedScore)}
      </span>
    </div>
  );
}
