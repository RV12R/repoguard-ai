# 🛡️ RepoGuard AI

RepoGuard AI is an autonomous, AI-powered security scanner for GitHub repositories. Designed to seamlessly integrate into modern developer workflows, it securely clones code, runs high-speed static analysis, performs deep semantic vulnerability reviews using LLMs, and generates professional PDF reports. It also ships with zero-click vulnerability remediation capabilities.

![UI-Black & White](https://img.shields.io/badge/UI-Black%20%26%20White-000000) ![Next.js](https://img.shields.io/badge/Next.js-15-black) ![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.12-blue) ![Supabase](https://img.shields.io/badge/Supabase-DB-green)

---

## ⚡ Key Features

- **No Persistence**: Repositories are cloned to ephemeral storage and automatically securely wiped immediately after analysis.
- **Hybrid Analysis Pipeline**: Combines deterministic static analysis (`Semgrep` / `Bandit`) with deep reasoning LLMs (`Llama-3.3-70B` via Groq, with Google `Gemini 2` fallback).
- **Web3 & AI Risk Detection**: Tailored prompts specifically detect Solidity reentrancy, access control flaws, LLM prompt injections, and data leakages natively.
- **Executive Reporting**: Automatically generates professional and structured PDF audit reports using ReportLab.
- **Auto-Fix Integration**: "One-click" branch creation patches vulnerabilities using AI-suggested code fixes.
- **Streaming Live Logs**: WebSocket-powered live progress bars and streaming terminal logs directly to the browser.
- **Clean Aesthetic UI**: Beautiful, fully responsive minimalist black & white aesthetic with seamless dark mode support.

---

## 🏗️ Technical Stack

### Frontend
- **Framework**: Next.js 15 (App Router) / React 19
- **Styling**: Tailwind CSS V4 + Shadcn/ui
- **State Management**: Zustand
- **Real-Time Data**: Native WebSockets

### Backend
- **Framework**: Python FastAPI
- **Security Tools**: Semgrep, Bandit
- **LLM Integration**: Groq API, Google Generative AI SDK
- **Database / Auth**: Supabase PostgreSQL

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions pipeline pre-configured for Vercel (Frontend) and Render (Backend)

---

## 🚀 Getting Started

### 1. Database Setup
1. Create a free PostgreSQL project at [Supabase](https://supabase.com).
2. Run the provided SQL migration in `supabase/migrations/001_initial.sql`.
3. Locate your `URL`, `anon public` key, and `service_role` secret key.

### 2. Run Locally via Docker

The repository includes a ready-to-use `docker-compose.yml` for standing up both the Next.js frontend and FastAPI backend alongside each other seamlessly.

1. Rename the `.env.example` templates in both `frontend/` and `backend/` to `.local.env` or `.env`.
2. Populate the environment variables with your API keys (Groq, Gemini, Supabase).
3. Start the containers using:
```bash
docker-compose up --build
```
> The frontend will be available at `http://localhost:3000` and the API at `http://localhost:8000`.

*(Alternatively, you can run the individual environments directly using `npm run dev` in the frontend and `uvicorn main:app --reload` within a Python virtual environment in the backend.)*

---

## 🤝 Contributing
Contributions, opened issues, and pull requests are warmly welcomed. Please ensure new features include functional fallback mechanisms and adhere strictly to the minimalist design philosophy of the frontend dashboard.
