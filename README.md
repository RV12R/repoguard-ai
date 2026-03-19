# 🛡️ RepoGuard AI

## 🎯 Our Goal
Build an autonomous, production-ready AI-powered security scanner for GitHub repositories from scratch at zero cost. The goal was to create a tool where users can paste a GitHub URL, and the system securely clones the code, runs static analysis, deeply analyzes logic with AI, and generates a professional PDF report with auto-fix capabilities.

## 🧠 Our Decisions
1. **Frontend Aesthetic**: Chose a pure Black & White, `Rekt.news`-inspired minimalist design with dark mode support, utilizing Next.js 15, Tailwind CSS, and Shadcn/ui for a highly responsive, premium UI.
2. **Backend Architecture**: Built an async Python FastAPI backend to handle complex orchestration, ensuring absolute zero code persistence (cloned repos are immediately deleted after analysis).
3. **AI Pipeline**: Selected Groq's `Llama-3.3-70B` as the primary LLM for deep review (due to its incredible speed and free tier availability), with Google's `Gemini 2.0 Flash` as a reliable free fallback.
4. **Static Tooling**: Integrated `Semgrep` and `Bandit` as foundational layers to catch known vulnerabilities fast before sending logic context to the LLM.
5. **Database**: Chosen Supabase PostgreSQL for a robust, free-tier database to track scan histories and vulnerabilities.
6. **Live Tracking**: Implemented real-time WebSocket communication to stream logs and progress directly from the backend to the frontend UI terminal.
7. **Pragmatic Workarounds**: Since Python was absent on the local Windows machine, a fully interactive "Demo Mode" was integrated directly into the Next.js frontend to visualize the final product without waiting for environmental setups.

## ✅ What We Have Done
- **Full Architecture Scaffolded**: Created the complete Docker-ready workspace, environment templates, and CI/CD pipelines (`.github/workflows/ci.yml`).
- **Frontend Completed & Refined**: Built all UI screens (Landing, Dashboard, New Scan, Scan Results). **Fixed typography and overlap issues** by stripping external Google Font dependencies, enforcing stable system font stacks, and tidying the Top Navigation (relocating the "Popular Rekts" link strictly to the footer).
- **Backend Completed**: Implemented 6 core Python services: Git clone management, Static analysis orchestration, AI context analysis, ReportLab PDF generation, Supabase DB logic, and GitHub API branching (Auto-Fixer).
- **Interactive Demo**: Built an onboard simulation mode (`/scan/demo`) allowing users to see exactly what the completed WebSocket stream will look like.

## 🚀 What Are Our Plans Next
1. **Python Environment Setup**: Install Python 3.12 locally on the host machine to test and verify the complete backend orchestration.
2. **Cloud Deployment**: Deploy the Next.js frontend on Vercel and the FastAPI backend to Render.com via the built-in GitHub Actions pipeline.
3. **Authentication**: Fully connect Supabase Auth to protect the Dashboard and authorize scans to specific users.
4. **Expand AI Rulesets**: Fine-tune the LLM systemic prompts to detect highly specific Web3/Solidity vulnerabilities (e.g., advanced reentrancy, MEV front-running) universally.
5. **GitHub Integration**: Add GitHub App support to automatically scan Pull Requests natively upon submission.

---

## 💻 How to Run It Right Now (Frontend)

Because **Node.js** is already available, you can launch the beautiful frontend and try the Demo Mode immediately:

```bash
cd frontend
npm ci
npm run dev
# The app will be running at http://localhost:3000
```
*Click "Start Scanning", enter any dummy URL, and watch the simulation in action!*

## ⚙️ How to Run the Full Engine (Once Python is Installed)

```bash
cd backend
python -m venv .venv

# Windows activation
.venv\Scripts\activate

pip install -r requirements.txt

# Create .env file by copying .env.example and populating API keys
cp .env.example .env

uvicorn main:app --reload
# API available at http://localhost:8000
```
