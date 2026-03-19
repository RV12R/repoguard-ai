import type { Metadata } from "next";
import { ThemeProvider } from "@/components/theme-provider";
import { Navbar } from "@/components/navbar";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "RepoGuard AI — Autonomous Security Scanner",
  description:
    "AI-powered static analysis and vulnerability detection for GitHub repositories. Professional security reports with one-click fix deployment.",
  keywords: [
    "security",
    "vulnerability scanner",
    "AI",
    "GitHub",
    "static analysis",
    "code audit",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col font-sans">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <Navbar />
          <main className="flex-1">{children}</main>

          {/* Footer */}
          <footer className="border-t border-border/40 py-6 mt-10">
            <div className="mx-auto max-w-6xl px-4 flex flex-col items-center justify-center gap-4 text-xs font-mono text-muted-foreground text-center">
              <span>© 2026 RepoGuard AI — Built for security researchers</span>
              
              <div className="flex flex-col items-center gap-2 mt-2 p-3 bg-muted/20 border border-border/30 rounded-md max-w-sm">
                <span className="font-semibold text-foreground/80">Support the project on GitHub:</span>
                <a
                  href="https://github.com/RV12R/repoguard-ai"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 bg-accent text-foreground hover:bg-muted transition-colors rounded border border-border/50 flex flex-col items-center"
                >
                  <span className="font-bold tracking-widest text-sm">GITHUB</span>
                  <span className="text-[10px] text-muted-foreground">Star the Repository</span>
                </a>
              </div>
            </div>
          </footer>

          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
