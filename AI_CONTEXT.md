# RepoGuard AI — Developer & AI Continuity Context

**Date Initialized**: March 19, 2026
**Purpose**: This document serves as the absolute master record of the project's history, architectural stack, workaround decisions, and current state. If a new AI agent takes over this repository, **read this entire file first** to understand the context of what has been built and what quirks exist.

---

## 1. Project Origins & Goals
The original objective was to build a complete, production-ready, zero-cost AI security scanner from scratch. The user requested:
- A "Rekt.news-inspired" absolute minimalist Black & White frontend UI with native Dark Mode.
- A GitHub clone service that leaves 0% persistence (auto-wipes codebase after scanning).
- A robust Python backend orchestrating Semgrep, Bandit, and LLMs (Groq Llama 3 for speed, Gemini for fallback).
- Auto-generation of executive PDF reports and "One-Click Apply Fixes" via GitHub API.

## 2. Core Decisions & Workarounds

### Visual Aesthetic & Typography
- **Issue**: Google Fonts were originally used but caused layout overlaps and hydration errors in Next.js.
- **Resolution (March 19, 2026)**: Stripped out Next.js `next/font/google` instances. We strictly use system font stacks (`ui-sans-serif, system-ui...` and `ui-monospace...`) in `globals.css` to guarantee zero overlap and peak performance.
- The "Rekt" link was requested to be removed from the top navigation to prevent clutter, and it is now strictly isolated in the Footer as a dedicated call-out module.

### Backend Execution Workarounds
- **Issue**: The host Windows machine originally lacked Python entirely.
- **Resolution**: Python 3.12 was installed natively via `winget` (March 19, 2026).
- **Issue**: The native `asyncio.create_subprocess_exec("git", ...)` in Python crashed on Windows due to path resolution failures without `shell=True`.
- **Resolution**: Explicitly resolved `git.exe` paths using `shutil.which("git")` in `services/git_service.py` to ensure cloning works flawlessly across both Windows natively and Linux (Render/Docker).

### Frontend Demo Mode
- A heavy "Demo Mode" was baked directly into `/scan/demo` on the Next.js frontend early in the development cycle. It visually simulates a real-time WebSocket connection reading logs and vulnerabilities. **Do not remove this**, as it serves as a critical fallback demonstration tool if the backend is offline.

---

## 3. Tech Stack Breakdown
- **Frontend**: Next.js 15, React 19, Tailwind CSS v4, Zustand (state), Shadcn/UI, Lucide React (icons), Sonner (toasts).
- **Backend**: FastAPI, GitPython, Semgrep (Static), Bandit (Static), Groq SDK (AI), Google GenAI SDK (AI fallback), ReportLab (PDFs), PyGitHub (Fixes), Supabase Python Client (DB).
- **DB**: Supabase PostgreSQL (Schema located at `supabase/migrations/001_initial.sql`). Contains `scans`, `vulnerabilities`, and `reports` tables.

---

## 4. Continuity Changelog

*Appending new changes here is mandatory.*

### [March 19, 2026] - v1.0 Launch
- **Scaffolded Architecture**: Generated all base folders, Git repository, `.gitignore`, and GitHub Action CI/CD pipelines.
- **Frontend Completed**: Fully implemented all frontend pages and reactive components. Repaired TypeScript React 19 strict-mode issues with `SheetTrigger`. Replaced flawed Google Fonts with stable System Fonts.
- **Backend Completed**: Wrote the 6 modular micro-services (`git_service`, `static_analyzer`, `ai_analyzer`, `report_generator`, `fix_service`, `supabase_client`). 
- **WebSocket Orchestration**: Built the full real-time event loop in `/api/scan` that communicates state to the frontend UI as clones and static scans run in `asyncio` background tasks.
- **GitHub Linkage**: User directly provided a Classic Repo PAT, triggering the remote initialization of `github.com/RV12R/repoguard-ai` and a successful `git push`.
- **Documentation Overhaul**: Split original convoluted `README.md` into this dedicated `AI_CONTEXT.md` log and a polished public-facing `README.md`.

---

## 5. Next Steps / Pending Development

If you are an AI picking up this repo next, your immediate goals are:
1. **Authentication Expansion**: Clerk was originally discussed but Supabase Auth was chosen. Tie Supabase Auth into the Next.js middleware to physically restrict access to the dashboard.
2. **LLM Prompt Fine-Tuning**: Expand the systemic prompt in `services/ai_analyzer.py` explicitly for advanced MEV/Solidity vectors.
3. **Automated PR Checking**: Write a GitHub App (Webhook) receiver endpoint in FastAPI that automatically listens for Push/PR events on tracked repositories to trigger scans autonomously.
