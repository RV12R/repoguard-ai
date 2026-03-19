"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Shield, Lock, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { toast } from "sonner";

const scanSchema = z.object({
  repo_url: z
    .string()
    .url("Must be a valid URL")
    .regex(/github\.com\/[\w.-]+\/[\w.-]+/i, "Must be a valid GitHub repository URL"),
  github_token: z.string().optional(),
});

type ScanFormData = z.infer<typeof scanSchema>;

export default function NewScanPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ScanFormData>({
    resolver: zodResolver(scanSchema),
    defaultValues: {
      repo_url: "",
      github_token: "",
    },
  });

  const onSubmit = async (data: ScanFormData) => {
    setLoading(true);
    try {
      const scan = await api.startScan({
        repo_url: data.repo_url,
        github_token: data.github_token || undefined,
      });
      toast.success("Scan started successfully");
      router.push(`/scan/${scan.id}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to start scan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-16">
      <div className="mb-8 animate-fade-in">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="h-5 w-5" />
          <h1 className="text-2xl font-mono font-bold">New Scan</h1>
        </div>
        <p className="text-sm text-muted-foreground font-mono">
          Paste a GitHub repository URL to start the security analysis.
        </p>
      </div>

      <Card className="animate-fade-in border-border/50">
        <CardHeader>
          <CardTitle className="text-sm font-mono">Repository Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Repo URL */}
            <div className="space-y-2">
              <Label htmlFor="repo_url" className="text-xs font-mono">
                GitHub Repository URL <span className="text-destructive">*</span>
              </Label>
              <Input
                id="repo_url"
                placeholder="https://github.com/owner/repository"
                className="font-mono text-sm h-10"
                {...register("repo_url")}
              />
              {errors.repo_url && (
                <p className="text-xs text-destructive font-mono">
                  {errors.repo_url.message}
                </p>
              )}
            </div>

            {/* GitHub Token */}
            <div className="space-y-2">
              <Label htmlFor="github_token" className="text-xs font-mono flex items-center gap-1.5">
                <Lock className="h-3 w-3" />
                GitHub Token
                <span className="text-muted-foreground">(optional, for private repos)</span>
              </Label>
              <Input
                id="github_token"
                type="password"
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                className="font-mono text-sm h-10"
                {...register("github_token")}
              />
              <p className="text-[11px] text-muted-foreground font-mono">
                Token is used only during the scan and never stored. Required for private repositories.
              </p>
            </div>

            {/* Info box */}
            <div className="rounded-md border border-border/50 bg-accent/30 p-3 space-y-1">
              <p className="text-xs font-mono font-semibold">What happens next:</p>
              <ul className="text-[11px] font-mono text-muted-foreground space-y-0.5">
                <li>→ Repository cloned to temporary storage</li>
                <li>→ Semgrep + Bandit static analysis</li>
                <li>→ AI deep review (Groq LLM)</li>
                <li>→ PDF report generated</li>
                <li>→ Code auto-deleted from server</li>
              </ul>
            </div>

            {/* Submit */}
            <Button
              type="submit"
              className="w-full font-mono gap-2 h-10"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Starting scan...
                </>
              ) : (
                <>
                  Start Security Scan <ArrowRight className="h-4 w-4" />
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
